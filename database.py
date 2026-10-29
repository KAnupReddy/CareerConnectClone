import os
import sqlite3
import click
from flask import current_app, g

def get_db():
    """
    Open a unique database connection per request if not already open.
    Enables SQLite foreign key enforcement and dictionary-like Row access.
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=0,
            timeout=10.0
        )
        g.db.row_factory = sqlite3.Row
        
        # Enforce foreign key constraints in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    
    return g.db

def close_db(e=None):
    """Close the database connection on request teardown."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Clear existing data and create new tables using sql/schema.sql."""
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'sql', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())

def init_db_if_missing():
    """
    Check if required tables exist; if missing, initialize automatically.
    Ensures safe automatic table creation on startup without deleting data.
    """
    db = get_db()
    cursor = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('contact_messages', 'courses', 'enrolments', 'testimonials')"
    )
    count = cursor.fetchone()[0]
    if count < 4:
        init_db()

# --- Repository / Parameterized SQL Query Helpers ---

def save_contact_message(name: str, email: str, message: str) -> int:
    """
    Insert a contact form submission using parameterized query.
    Returns the newly created message ID.
    """
    db = get_db()
    cursor = db.execute(
        '''
        INSERT INTO contact_messages (name, email, message, status)
        VALUES (?, ?, ?, 'unread')
        ''',
        (name.strip(), email.strip(), message.strip())
    )
    db.commit()
    return cursor.lastrowid

def save_enrolment(course_id: int, full_name: str, email: str, phone: str, transaction_reference: str = None, notes: str = None) -> int:
    """
    Insert a course enrolment submission using parameterized query.
    Status is strictly initialized to 'pending_verification'.
    Returns the newly created enrolment ID.
    """
    db = get_db()
    cursor = db.execute(
        '''
        INSERT INTO enrolments (course_id, full_name, email, phone, payment_method, transaction_reference, notes, status)
        VALUES (?, ?, ?, ?, 'UPI / Google Pay', ?, ?, 'pending_verification')
        ''',
        (
            course_id,
            full_name.strip(),
            email.strip(),
            phone.strip(),
            transaction_reference.strip() if transaction_reference else None,
            notes.strip() if notes else None
        )
    )
    db.commit()
    return cursor.lastrowid

def get_all_testimonials():
    """Fetch all testimonials ordered by display_order."""
    db = get_db()
    return db.execute(
        'SELECT * FROM testimonials ORDER BY display_order ASC, id ASC'
    ).fetchall()

def get_course_by_slug(slug: str = 'career-accelerator-program'):
    """Fetch course details by slug using parameterized query."""
    db = get_db()
    return db.execute(
        'SELECT * FROM courses WHERE slug = ?',
        (slug,)
    ).fetchone()

@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the SQLite database with CareerConnect schema.')

def init_app(app):
    """Register database functions and CLI commands with the Flask application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
