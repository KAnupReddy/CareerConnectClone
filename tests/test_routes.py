import os
import tempfile
import pytest
from app import create_app
import database

@pytest.fixture
def app_instance():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-12345'
    })

    with app.app_context():
        database.init_db()

    yield app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

# --- Page Route Tests ---

def test_homepage_route(client):
    """Test that homepage loads with 200 OK and expected copy."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Holding Your Hand From Preparation To Placement" in response.data
    assert b"Welcome to Career Accelerator Program" in response.data
    assert b"Career Captain" in response.data
    assert b"Frequently Asked" in response.data
    assert b"Still have questions?" in response.data

def test_about_route_with_db_testimonials(client):
    """Test that about page queries and renders testimonials from SQLite."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b"Empowering Your" in response.data
    assert b"Who We" in response.data
    assert b"Our" in response.data
    assert b"Rushikesh Kalane" in response.data
    assert b"Diotima Bose" in response.data
    assert b"Er. Dikshant V. Jagtap" in response.data

def test_course_route(client):
    """Test course page renders program and benefits."""
    response = client.get('/course')
    assert response.status_code == 200
    assert b"Career Accelerator Program" in response.data
    assert b"Duration: 5-6 Weeks" in response.data
    assert b"Why" in response.data
    assert b"Immerse in interactive sessions along with hands-on skill development." in response.data

def test_pricing_and_enroll_routes(client):
    """Test pricing and enroll GET routes render payment instructions and GPay QR."""
    res_pricing = client.get('/pricing')
    assert res_pricing.status_code == 200
    assert b"Average Delivery Time" in response_bytes(res_pricing)
    assert b"QR-GPay-BbuHc8Xi.jpg" in response_bytes(res_pricing)

    res_enroll = client.get('/enroll')
    assert res_enroll.status_code == 200
    assert b"Career Accelerator Program" in response_bytes(res_enroll)

def test_privacypolicy_route(client):
    """Test privacy policy page renders full legal disclosure clauses."""
    response = client.get('/privacypolicy')
    assert response.status_code == 200
    assert b"Privacy Policy" in response.data
    assert b"Information We Collect" in response.data
    assert b"Data Security" in response.data

def test_404_error_page(client):
    """Test that unknown URLs return 404 with custom error page."""
    response = client.get('/some-invalid-page-xyz')
    assert response.status_code == 404
    assert b"404" in response.data
    assert b"Page Not Found" in response.data

# --- Contact Form Validation & DB Persistence Tests ---

def test_contact_get_renders_clean_form(client):
    """Test GET /contact renders form fields cleanly."""
    response = client.get('/contact')
    assert response.status_code == 200
    assert b"Contact Us" in response.data
    assert b'name="name"' in response.data
    assert b'name="email"' in response.data
    assert b'name="message"' in response.data

def test_contact_get_with_enroll_intent_prefills_message(client):
    """Test GET /contact?intent=enroll pre-fills enrollment message."""
    response = client.get('/contact?intent=enroll')
    assert response.status_code == 200
    assert b"completed payment for the Career Accelerator Program" in response.data

def test_contact_post_valid_submits_to_database(client, app_instance):
    """Test POST /contact with valid data persists to SQLite contacts table."""
    data = {
        'name': 'Priya Sharma',
        'email': 'priya.sharma@example.com',
        'message': 'I would like to inquire about upcoming batches for the Career Accelerator Program.'
    }
    response = client.post('/contact', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Thank you, Priya Sharma!" in response.data

    with app_instance.app_context():
        db = database.get_db()
        row = db.execute('SELECT * FROM contact_messages WHERE email = ?', ('priya.sharma@example.com',)).fetchone()
        assert row is not None
        assert row['name'] == 'Priya Sharma'
        assert row['message'] == data['message']
        assert row['status'] == 'unread'

def test_contact_post_missing_fields_validation_error(client):
    """Test POST /contact with empty fields returns 400 Bad Request and validation errors."""
    response = client.post('/contact', data={'name': '', 'email': '', 'message': ''})
    assert response.status_code == 400
    assert b"Name is required." in response.data
    assert b"Email is required." in response.data
    assert b"Message is required." in response.data

def test_contact_post_invalid_email_validation_error(client):
    """Test POST /contact with invalid email format returns 400 and preserves user input."""
    data = {
        'name': 'Rohan Patel',
        'email': 'invalid-email-format-without-at',
        'message': 'Valid message content exceeding minimum length.'
    }
    response = client.post('/contact', data=data)
    assert response.status_code == 400
    assert b"Please provide a valid email address." in response.data
    assert b"Rohan Patel" in response.data

def test_contact_post_short_message_validation_error(client):
    """Test POST /contact with too short message returns 400."""
    data = {
        'name': 'Rohan Patel',
        'email': 'rohan@example.com',
        'message': 'Hi'
    }
    response = client.post('/contact', data=data)
    assert response.status_code == 400
    assert b"Message must be at least 5 characters long." in response.data

# --- Enrollment Form Validation & DB Persistence Tests ---

def test_enroll_post_valid_submits_to_database(client, app_instance):
    """Test POST /enroll stores registration in SQLite enrolments table with pending status."""
    data = {
        'full_name': 'Amit Verma',
        'email': 'amit.verma@example.com',
        'phone': '9876543210',
        'transaction_reference': 'UPI1234567890',
        'notes': 'Paid via Google Pay'
    }
    response = client.post('/enroll', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"submitted for verification" in response.data

    with app_instance.app_context():
        db = database.get_db()
        row = db.execute('SELECT * FROM enrolments WHERE email = ?', ('amit.verma@example.com',)).fetchone()
        assert row is not None
        assert row['full_name'] == 'Amit Verma'
        assert row['phone'] == '9876543210'
        assert row['transaction_reference'] == 'UPI1234567890'
        assert row['status'] == 'pending_verification'

def test_enroll_post_invalid_data_validation_error(client):
    """Test POST /enroll with invalid data returns 400 with error feedback."""
    data = {
        'full_name': '',
        'email': 'bad-email',
        'phone': '123'
    }
    response = client.post('/enroll', data=data)
    assert response.status_code == 400
    assert b"Please provide a valid full name" in response.data

# --- Static Assets Loading Tests ---

def test_static_assets_load_correctly(client):
    """Test that key static assets (CSS, JS, images) return 200 OK."""
    assets = [
        '/static/css/style.css',
        '/static/js/script.js',
        '/static/images/CareerConnect-CHv0KAkV.svg',
        '/static/images/QR-GPay-BbuHc8Xi.jpg',
        '/static/images/CourseImg-DQBjLpzY.png',
        '/static/images/contact img-CBu579C3.jpg',
        '/static/images/favicon-32x32.png'
    ]
    for asset in assets:
        res = client.get(asset)
        assert res.status_code == 200, f"Failed to load asset: {asset}"

def response_bytes(res):
    return res.data
