-- CareerConnect Clone SQL Database Schema
-- SQLite 3 Compatible

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS enrolments;
DROP TABLE IF EXISTS contact_messages;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS testimonials;

-- Courses Table (Audited Course: Career Accelerator Program)
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    duration TEXT NOT NULL,
    availability TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Contact Messages Table
CREATE TABLE contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) >= 2 AND length(name) <= 100),
    email TEXT NOT NULL CHECK(length(trim(email)) >= 5 AND length(email) <= 120),
    message TEXT NOT NULL CHECK(length(trim(message)) >= 5 AND length(message) <= 3000),
    status TEXT NOT NULL DEFAULT 'unread' CHECK(status IN ('unread', 'read', 'in_progress', 'responded', 'archived')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Course Enrolments Table
-- Requires manual staff verification for UPI/GPay transfers.
-- Never marked as verified or confirmed automatically.
CREATE TABLE enrolments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) >= 2 AND length(full_name) <= 100),
    email TEXT NOT NULL CHECK(length(trim(email)) >= 5 AND length(email) <= 120),
    phone TEXT NOT NULL CHECK(length(trim(phone)) >= 7 AND length(phone) <= 20),
    payment_method TEXT NOT NULL DEFAULT 'UPI / Google Pay',
    transaction_reference TEXT CHECK(length(transaction_reference) <= 100),
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'pending_verification' CHECK(status IN ('pending_verification', 'under_review', 'verified', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Testimonials & Student Reviews Table
CREATE TABLE testimonials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name TEXT NOT NULL,
    user_handle TEXT NOT NULL,
    initials TEXT NOT NULL,
    comment TEXT,
    review_image TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed Audited Courses
INSERT INTO courses (slug, title, duration, availability, description) VALUES
(
    'career-accelerator-program',
    'Career Accelerator Program',
    '5-6 Weeks',
    'Live Course',
    'Designed to equip you with the skills and knowledge you need to excel to get placed in your desired company.'
);

-- Seed Audited Student Reviews
INSERT INTO testimonials (author_name, user_handle, initials, comment, review_image, display_order) VALUES
(
    'Rushikesh Kalane',
    '@rushi_kalane2',
    'RK',
    'Journey from the basics of communication to personal interview and GD all you covered was fantastic. I really enjoyed your sessions. What impressed me the most was your willingness to help the students.',
    NULL,
    1
),
(
    'Diotima Bose',
    '@Diotima_Bose3',
    'DB',
    NULL,
    'images/DBJ1-qjXgtFw5.jpg',
    2
),
(
    'Diotima Bose',
    '@Diotima_Bose3',
    'DB',
    NULL,
    'images/DBJ2-BN1-Dk1n.jpg',
    3
),
(
    'Er. Dikshant V. Jagtap',
    '@dikshant.jagtap',
    'DJ',
    'I would like to thank the wonderful faculty for guiding us on communication skills behavioural skills and many more things. It made such a difference in my attitude.',
    'images/DBJ3--hEaMT16.jpg',
    4
),
(
    'Naila Parween',
    '@pnaila',
    'NP',
    'Learning communication skills from the mentor was a pleasent and favourable experience for me. One thing I want to mention here is that earlier I used to think that since I have no professional experience, I can never convince my recruiter on certain things but you Instilled the confidence in me to use my academic achievments to better present my capabilities.',
    NULL,
    5
),
(
    'Jasleen',
    '@jasleen_4',
    'JN',
    'Thankyou so much for giving guidance to me because of you only I got such good results in IELTS.. Thankyou so much ma''am.',
    'images/DC-rkDvZU0d.jpg',
    6
),
(
    'Dinesh Choudhary',
    '@dinesh_choudhary',
    'DC',
    'Thank you @Shubhangi ma''am for delivering such informative and engaging lectures on Effective Communication. We learned something new in every lecture. Your passion for teaching and expertise in the subject made it easy for us to understand the subject.',
    'images/Pic-1-Qq7fJYgp.jpg',
    7
);
