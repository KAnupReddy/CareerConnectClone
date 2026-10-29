import os
import re
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf.csrf import CSRFProtect, CSRFError
import dotenv
import database

# Load environment variables from .env file if present
dotenv.load_dotenv()

def create_app(test_config=None):
    """Application factory for CareerConnectClone."""
    app = Flask(__name__, instance_relative_config=True)

    db_default_path = os.path.join(app.instance_path, 'careerconnect.db')
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'careerconnect-clone-dev-secret-key-2024'),
        DATABASE=os.environ.get('DATABASE', db_default_path),
        WTF_CSRF_ENABLED=True,
    )

    if test_config is not None:
        app.config.update(test_config)

    # Ensure the instance directory exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Enable CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Initialize Database helpers
    database.init_app(app)

    # Auto-initialize SQLite tables on application startup
    with app.app_context():
        try:
            database.init_db_if_missing()
        except Exception as e:
            app.logger.warning(f"Database auto-initialization deferred: {e}")

    # --- Core Routes based on reference website audit ---

    @app.route('/')
    def index():
        """Homepage: Hero, Blueprint, About, CTA, 8 Accelerator Steps, Captain, FAQ."""
        return render_template('index.html')

    @app.route('/about')
    def about():
        """About Page: Hero, Who We Are, Vision, CTA, Testimonials from SQLite DB."""
        testimonials = []
        try:
            testimonials = database.get_all_testimonials()
        except Exception:
            pass
        return render_template('about.html', testimonials=testimonials)

    @app.route('/course')
    def course():
        """Course Page: Program Header, Duration, Syllabus highlights, Why This Course."""
        course_data = None
        try:
            course_data = database.get_course_by_slug('career-accelerator-program')
        except Exception:
            pass
        return render_template('course.html', course=course_data)

    @app.route('/pricing')
    def pricing():
        """Pricing Page: Program details, Average delivery, Contact info, GPay QR."""
        return render_template('pricing.html')

    @app.route('/enroll', methods=['GET', 'POST'])
    def enroll():
        """
        Enrollment verification route.
        Validates enrollment submission and saves record with pending_verification status.
        Never invents successful payments or claims false confirmation.
        """
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            transaction_ref = request.form.get('transaction_reference', '').strip()
            notes = request.form.get('notes', '').strip()

            errors = []
            if not full_name or len(full_name) < 2 or len(full_name) > 100:
                errors.append('Please provide a valid full name (2-100 characters).')
            
            email_regex = r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$"
            if not email or not re.match(email_regex, email) or len(email) > 120:
                errors.append('Please provide a valid email address.')
                
            if not phone or len(phone) < 7 or len(phone) > 20:
                errors.append('Please provide a valid phone number.')

            if errors:
                for err in errors:
                    flash(err, 'error')
                return render_template('pricing.html', form_data=request.form, errors=errors), 400

            course_row = database.get_course_by_slug('career-accelerator-program')
            course_id = course_row['id'] if course_row else 1

            database.save_enrolment(
                course_id=course_id,
                full_name=full_name,
                email=email,
                phone=phone,
                transaction_reference=transaction_ref,
                notes=notes
            )

            # Never claim instant payment confirmation - explicit pending notice
            flash(
                'Your enrollment request and payment reference have been submitted for verification. '
                'Our admissions team will review your payment and contact you within 6 to 24 hours to confirm your registration.',
                'success'
            )
            return redirect(url_for('pricing'))

        return render_template('pricing.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """
        Contact Page: Form (Name, Email, Message) with strict validation & DB persistence.
        Stores submission in contact_messages table using parameterized query.
        """
        intent = request.args.get('intent', '').strip().lower()
        prefill_message = ''
        if intent == 'enroll':
            prefill_message = 'I have completed payment for the Career Accelerator Program via Google Pay. Please confirm my enrollment and share live class details.'

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()

            errors = []
            error_fields = []

            # 1. Name validation
            if not name:
                errors.append('Name is required.')
                error_fields.append('name')
            elif len(name) < 2:
                errors.append('Name must be at least 2 characters long.')
                error_fields.append('name')
            elif len(name) > 100:
                errors.append('Name cannot exceed 100 characters.')
                error_fields.append('name')

            # 2. Email validation
            email_regex = r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$"
            if not email:
                errors.append('Email is required.')
                error_fields.append('email')
            elif not re.match(email_regex, email) or len(email) > 120:
                errors.append('Please provide a valid email address.')
                error_fields.append('email')

            # 3. Message validation
            if not message:
                errors.append('Message is required.')
                error_fields.append('message')
            elif len(message) < 5:
                errors.append('Message must be at least 5 characters long.')
                error_fields.append('message')
            elif len(message) > 3000:
                errors.append('Message cannot exceed 3000 characters.')
                error_fields.append('message')

            if errors:
                for err in errors:
                    flash(err, 'error')
                return render_template(
                    'contact.html',
                    form_data=request.form,
                    errors=errors,
                    error_fields=error_fields,
                    prefill_message=prefill_message
                ), 400

            # Parameterized insert into contact_messages
            database.save_contact_message(name, email, message)

            flash(f'Thank you, {name}! Your message has been sent successfully. We will get back to you shortly.', 'success')
            return redirect(url_for('contact'))

        return render_template('contact.html', prefill_message=prefill_message)

    @app.route('/privacypolicy')
    def privacypolicy():
        """Privacy Policy Page: Full data handling and candidate rights disclosures."""
        return render_template('privacypolicy.html')

    # --- Error Handlers ---

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF validation failures gracefully."""
        flash('The session has expired or the security token was invalid. Please try submitting again.', 'error')
        return redirect(url_for('contact'))

    @app.errorhandler(404)
    def page_not_found(error):
        """Custom 404 error page."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Custom 500 error page."""
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
