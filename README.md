# Enterprise Backup Monitoring Dashboard

A full-stack web application for uploading backup reports (CSV, Excel, HTML) and visualizing backup health across multiple categories (Disk-to-Disk, Disk-to-Tape, Replication), with authentication, per-user data isolation, upload history, and basic anomaly detection.

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy
- **Frontend:** Plain HTML, CSS, JavaScript (no build tools), Chart.js
- **Auth:** JWT (python-jose), bcrypt password hashing (passlib)
- **Parsing:** Pandas (CSV/Excel/HTML), openpyxl, lxml
- **Anomaly detection:** Statistical (median/MAD-based outlier detection)

## Prerequisites

Before running this project, make sure you have:

1. **Python 3.10+** installed
2. **PostgreSQL** installed and running locally
3. A modern web browser (Chrome/Edge recommended)

## Setup Instructions

### 1. Clone the repository

\`\`\`bash
git clone <repo-url>
cd backup-dashboard
\`\`\`

### 2. Set up the backend

\`\`\`bash
cd backend
python -m venv venv
\`\`\`

Activate the virtual environment:
- **Windows (PowerShell):** \`venv\\Scripts\\Activate.ps1\`
- **Mac/Linux:** \`source venv/bin/activate\`

Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Set up PostgreSQL

Create a database named \`backup_dashboard\` (via pgAdmin or \`psql\`).

### 4. Configure environment variables

Create a file called \`.env\` inside the \`backend\` folder with the following content:

\`\`\`
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/backup_dashboard
\`\`\`

Replace \`<username>\` and \`<password>\` with your actual PostgreSQL credentials. If your password contains special characters (like \`@\`), URL-encode them (e.g. \`@\` becomes \`%40\`).

### 5. Create the database tables

\`\`\`bash
python create_tables.py
\`\`\`

You should see: \`Tables created successfully!\`

### 6. Start the backend server

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

The API will be running at \`http://127.0.0.1:8000\`. You can view the interactive API docs at \`http://127.0.0.1:8000/docs\`.

### 7. Run the frontend

No build step needed. Simply open \`frontend/index.html\` directly in your browser (double-click it, or right-click → Open with Live Server in VS Code).

**Important:** Keep the backend server running in a separate terminal window while using the frontend.

## Using the Application

1. Open \`frontend/register.html\` and create an account
2. Log in via \`frontend/login.html\`
3. Upload backup reports via the 3 category cards (Disk-to-Disk, Disk-to-Tape, Replication) — supports CSV, Excel (.xlsx), and HTML formats
4. View the dashboard for summary stats, category-wise pie charts, VM search with anomaly detection, and upload history

## Sample Data Format

### Disk-to-Disk / Disk-to-Tape (CSV/Excel/HTML)
Columns: \`App Job Id, Server, Client, Status, Status Code, Backup Level, Backup Size (GB), Total Files, Files Not Backed Up, Started, Finished, Duration (Minutes), Expires, Total Jobs, Reduction Ratio\`

### Replication (CSV)
Columns: \`Client Name, Latest Updated Date, Last Updated Date, Unit Number\`

## Project Structure

\`\`\`
backup-dashboard/
  backend/
    app/
      routers/       # API endpoints (auth, upload, dashboard)
      models/        # Database table definitions (SQLAlchemy)
      services/
        parsers/      # File format parsers (CSV, Excel, HTML, Replication)
        auth_service.py
      database/       # DB connection setup
      main.py         # FastAPI app entrypoint
    create_tables.py  # Script to initialize database tables
    requirements.txt
    .env              # Not committed — create this yourself (see Setup step 4)
  frontend/