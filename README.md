# CareerConnect Clone

A faithful local development recreation of the **CareerConnect** mentorship platform ([https://www.careerconnect.co.in/](https://www.careerconnect.co.in/)), built with Python Flask, SQLite, Jinja2 templates, standard JavaScript (ES6), and CSS3 following modern design tokens, responsive breakpoints, and accessibility standards.

---

## Architecture & Technology Stack

- **Backend:** Python 3.10+ / Flask 3.x
- **Database:** SQLite 3 with SQL DDL schema (`sql/schema.sql`) and foreign key constraints enabled
- **Forms & Security:** Flask-WTF CSRF Protection, parameter-safe SQL queries, server-side validation
- **Templates:** Jinja2 modular inheritance with a shared `base.html` and reusable components (`navbar.html`, `footer.html`, `flash_messages.html`)
- **Frontend Interactivity:** Standard ES6 JavaScript (Light/Dark mode toggle synced to `localStorage`, mobile slide-over sheet drawer, single-collapsible FAQ accordion, testimonial review screenshot lightbox modal, back-to-top floating button, duplicate form submission prevention)
- **Styling:** CSS3 design system adopting audited HSL color tokens (`--background`, `--foreground`, `--primary`, `--border`, `--card`), responsive mobile-first grids, and smooth transitions
- **Automated Testing:** 22 pytest automated tests verifying database schema, foreign keys, routes, error handlers, and form submissions

---

## Directory Structure

```text
CareerConnectClone/
├── app.py                  # Application factory, routing, error handlers, and form handling
├── database.py             # SQLite connection management and repository functions
├── requirements.txt        # Flask, Flask-WTF, python-dotenv, and pytest dependencies
├── run.bat                 # Robust one-click Windows launcher and environment manager
├── README.md               # Project documentation and setup guide
├── .env                    # Local environment variables (loaded automatically by python-dotenv)
├── .env.example            # Sample configuration template
├── .gitignore              # Ignored files (venv, instance, pycache)
├── instance/               # Local data directory housing SQLite database
│   └── careerconnect.db    # SQLite database (auto-initialized, foreign keys enabled)
├── sql/
│   └── schema.sql          # Table definitions (courses, contact_messages, enrolments, testimonials)
├── templates/
│   ├── base.html           # Shared layout (sticky navbar, mobile drawer, footer, toasts)
│   ├── components/         # Modular template partials
│   │   ├── navbar.html     # Responsive sticky header (56px) and navigation links
│   │   ├── footer.html     # Footer columns and social destinations
│   │   └── flash_messages.html # Accessible alert notifications
│   ├── index.html          # Homepage (Hero, Blueprint, About, CTA, 8 Steps, Captain, FAQ)
│   ├── about.html          # About Us (Hero, Who We Are, Vision, CTA, Testimonials lightbox)
│   ├── course.html         # Course details (Career Accelerator Program, benefits)
│   ├── pricing.html        # Enroll / Pricing (Program overview, contact info, GPay QR card)
│   ├── contact.html        # Contact Us (CSRF-protected form with DB persistence)
│   ├── privacypolicy.html  # Full legal disclosures and student privacy policy
│   ├── 404.html            # Custom 404 Page Not Found
│   └── 500.html            # Custom 500 Internal Server Error
├── static/
│   ├── css/
│   │   └── style.css       # Audited HSL tokens, themes, layout grids, responsive breakpoints
│   ├── js/
│   │   └── script.js       # Client interactions (theme toggle, drawer, accordion, modals)
│   ├── images/             # Visual assets, SVG icons, founder photos, review screenshots
│   └── uploads/            # Dedicated directory for uploaded files or attachments
└── tests/
    ├── __init__.py
    ├── test_database.py    # Database initialization, foreign keys, and schema tests (7 tests)
    └── test_routes.py      # Route mapping, error handlers, and form validation tests (15 tests)
```

---

## Route Mapping Based on Reference Audit

| HTTP Route | Template | Description |
|---|---|---|
| `GET /` | `templates/index.html` | Homepage: Hero, Pain Points ("Are you also?"), About, CTA 1, 8-Step Accelerator, Founder Captain, FAQ Accordion. |
| `GET /about` | `templates/about.html` | About Page: Hero header, "Who We Are", "Our Vision", CTA 2, Testimonials with modal lightbox. |
| `GET /course` | `templates/course.html` | Course Page: Program card, duration (5-6 weeks), Why This Course benefits. |
| `GET /pricing`<br>`GET /enroll` | `templates/pricing.html` | Pricing & Enrollment: Program overview, contact info, GPay QR card, and registration action. |
| `GET /contact`<br>`POST /contact` | `templates/contact.html` | Contact Page: CSRF-protected contact form with database persistence. |
| `GET /privacypolicy` | `templates/privacypolicy.html` | Full legal disclosures and student privacy policy. |
| Any invalid URL | `templates/404.html` | Custom 404 error page matching site styling. |

---

## Windows Setup & Execution Instructions

### Option 1: Automatic Setup via `run.bat` (Recommended)

The included `run.bat` script handles complete end-to-end setup and execution on Windows without manual configuration.

#### First-Time Setup
1. Open the project folder in Windows File Explorer:
   ```text
   c:\Users\DELL\Desktop\Carrer Connect\CareerConnectClone
   ```
2. Double-click `run.bat` (or open Command Prompt / PowerShell, navigate to the folder, and run `.\run.bat`).
3. On first execution, `run.bat` will automatically:
   - Detect Python using the Windows `py` launcher (`py -3` or `py`) or `python` command.
   - Create a dedicated virtual environment in `.venv`.
   - Install all required dependencies from `requirements.txt`.
   - Create a default `.env` configuration file from `.env.example` if not already present.
   - Check port 5000 to ensure no conflicting server is running.
   - Automatically open `http://127.0.0.1:5000` in your default browser.
   - Start the Flask development server.

#### Normal Startup
On subsequent runs, simply double-click `run.bat` again. It detects the existing `.venv`, quickly verifies dependencies, checks the port, launches the application, and opens your browser.

#### Stopping the Server
To stop the application at any time, switch to the open `run.bat` console window and press:
```text
Ctrl + C
```
Type `Y` if prompted by Windows to terminate the batch job. The console window remains open so you can review any final server logs.

---

### Option 2: Manual Setup (Command Prompt or PowerShell)

If you prefer manual control, follow these steps:

1. **Open Command Prompt or PowerShell:**
   ```powershell
   cd "c:\Users\DELL\Desktop\Carrer Connect\CareerConnectClone"
   ```

2. **Create and Activate the Virtual Environment:**
   ```powershell
   # Create virtual environment
   py -3 -m venv .venv

   # Activate in Command Prompt (cmd.exe):
   .venv\Scripts\activate.bat

   # Or activate in PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. **Initialize SQLite Database (Automatic):**
   The database tables and seed testimonials auto-initialize on the first run of `app.py`. Alternatively, you can run the CLI command:
   ```powershell
   flask --app app init-db
   ```
   *(This initializes `instance/careerconnect.db` with schema and seed data safely without dropping existing user submissions).*

5. **Run the Application:**
   ```powershell
   python app.py
   ```
   Open your browser at: **`http://127.0.0.1:5000/`**

---

## Running the Automated Test Suite

The project includes 22 automated tests covering SQLite database initialization, foreign key constraints, state persistence, route mapping, and form validation.

Using the virtual environment Python:
```powershell
# Run all tests with verbose output:
".venv\Scripts\python.exe" -m pytest tests -v

# Run only database tests:
".venv\Scripts\python.exe" -m pytest tests/test_database.py -v

# Run only route & form tests:
".venv\Scripts\python.exe" -m pytest tests/test_routes.py -v
```

Expected result:
```text
============================== 22 passed in 1.03s ==============================
```

---

## Troubleshooting & FAQ

### 1. "Python is not installed or not found in system PATH"
- **Cause:** Neither `py` nor `python` was found in your Windows PATH.
- **Fix:** Download Python 3.10+ from [python.org](https://www.python.org/downloads/). During installation, make sure to check the box:
  `[x] Add python.exe to PATH`
  After installing, restart your command prompt or terminal.

### 2. "[WARNING] Port 5000 is already in use by process PID ..."
- **Cause:** Another instance of CareerConnect or another server is already running on port 5000.
- **Fix:** `run.bat` automatically detects this and offers to open your existing server in your browser or exit safely without creating port binding errors.
  To stop the conflicting process manually in PowerShell:
  ```powershell
  # Find process listening on port 5000:
  Get-NetTCPConnection -LocalPort 5000 | Select-Object OwningProcess

  # Stop lingering python server:
  Stop-Process -Name python -Force
  ```

### 3. PowerShell: "File ... Activate.ps1 cannot be loaded because running scripts is disabled"
- **Cause:** Windows PowerShell execution policy restricts running unsigned local scripts.
- **Fix:** Either run `run.bat` directly via Command Prompt (which does not have this restriction), or allow local scripts in PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

### 4. Database Reset or Inspection
- The SQLite database is stored locally at [`instance/careerconnect.db`](instance/careerconnect.db).
- `run.bat` never deletes or overwrites existing user messages or enrolments.
- To view submissions directly in SQLite:
  ```powershell
  ".venv\Scripts\python.exe" -c "import sqlite3; con=sqlite3.connect('instance/careerconnect.db'); print(con.execute('SELECT id, name, email, status FROM contact_messages').fetchall())"
  ```
