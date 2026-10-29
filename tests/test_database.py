import os
import tempfile
import sqlite3
import pytest
from app import create_app
import database

@pytest.fixture
def app_and_db():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-db-secret-key'
    })

    with app.app_context():
        database.init_db()
        yield app, db_path

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_init_db_creates_all_required_tables(app_and_db):
    """Verify that init_db creates courses, contact_messages, enrolments, testimonials."""
    app, db_path = app_and_db
    with app.app_context():
        db = database.get_db()
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [row['name'] for row in tables]

        assert 'courses' in table_names
        assert 'contact_messages' in table_names
        assert 'enrolments' in table_names
        assert 'testimonials' in table_names

def test_seed_data_presence(app_and_db):
    """Verify default course and 7 authentic student testimonials are seeded."""
    app, _ = app_and_db
    with app.app_context():
        course = database.get_course_by_slug('career-accelerator-program')
        assert course is not None
        assert course['title'] == 'Career Accelerator Program'
        assert course['duration'] == '5-6 Weeks'
        assert course['availability'] == 'Live Course'

        testimonials = database.get_all_testimonials()
        assert len(testimonials) == 7
        names = [t['author_name'] for t in testimonials]
        assert 'Rushikesh Kalane' in names
        assert 'Diotima Bose' in names
        assert 'Er. Dikshant V. Jagtap' in names
        assert 'Naila Parween' in names
        assert 'Jasleen' in names
        assert 'Dinesh Choudhary' in names

def test_foreign_key_enforcement(app_and_db):
    """Verify SQLite foreign keys are strictly enabled and enforce constraints."""
    app, _ = app_and_db
    with app.app_context():
        db = database.get_db()
        
        # Verify PRAGMA foreign_keys is ON (1)
        fk_status = db.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk_status == 1

        # Attempt inserting into enrolments with a non-existent course_id
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                '''INSERT INTO enrolments (course_id, full_name, email, phone, status)
                   VALUES (999999, 'Invalid Course Student', 'student@example.com', '9876543210', 'pending_verification')'''
            )
            db.commit()

def test_contact_messages_check_constraints(app_and_db):
    """Verify CHECK constraints on contact_messages (name length, message length, status)."""
    app, _ = app_and_db
    with app.app_context():
        db = database.get_db()

        # Name too short (< 2 chars)
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO contact_messages (name, email, message) VALUES ('A', 'a@b.com', 'Valid message content')")
            db.commit()

        # Message too short (< 5 chars)
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO contact_messages (name, email, message) VALUES ('Alice', 'a@b.com', 'Hi')")
            db.commit()

        # Invalid status not in allowed list
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO contact_messages (name, email, message, status) VALUES ('Alice', 'a@b.com', 'Valid message content', 'invalid_status')")
            db.commit()

def test_enrolments_status_defaults_to_pending_verification(app_and_db):
    """Verify enrolments never invent confirmed payment and default to pending_verification."""
    app, _ = app_and_db
    with app.app_context():
        course = database.get_course_by_slug('career-accelerator-program')
        enrolment_id = database.save_enrolment(
            course_id=course['id'],
            full_name='Vikram Singh',
            email='vikram@example.com',
            phone='9876543210',
            transaction_reference='GPay-Ref-98765',
            notes='Paid via UPI QR scan'
        )
        assert enrolment_id > 0

        db = database.get_db()
        row = db.execute('SELECT * FROM enrolments WHERE id = ?', (enrolment_id,)).fetchone()
        assert row is not None
        assert row['full_name'] == 'Vikram Singh'
        assert row['status'] == 'pending_verification'
        assert row['payment_method'] == 'UPI / Google Pay'
        assert row['transaction_reference'] == 'GPay-Ref-98765'

def test_save_contact_message_repository(app_and_db):
    """Verify parameterized save_contact_message helper."""
    app, _ = app_and_db
    with app.app_context():
        msg_id = database.save_contact_message(
            name='Rohit Sen',
            email='rohit.sen@example.com',
            message='I want to enquire about the live sessions timing.'
        )
        assert msg_id > 0

        db = database.get_db()
        row = db.execute('SELECT * FROM contact_messages WHERE id = ?', (msg_id,)).fetchone()
        assert row is not None
        assert row['name'] == 'Rohit Sen'
        assert row['status'] == 'unread'
        assert row['created_at'] is not None

def test_init_db_if_missing_is_idempotent(app_and_db):
    """Verify init_db_if_missing preserves existing data if tables exist."""
    app, _ = app_and_db
    with app.app_context():
        # Insert a test message
        database.save_contact_message('Existing User', 'user@example.com', 'Persisted message content')
        
        # Call init_db_if_missing again
        database.init_db_if_missing()

        db = database.get_db()
        count = db.execute("SELECT count(*) FROM contact_messages WHERE name = 'Existing User'").fetchone()[0]
        assert count == 1

