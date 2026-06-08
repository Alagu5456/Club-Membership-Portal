# Club Membership Portal - Setup Guide

## Running on Your Local Computer

### Prerequisites
- Python 3.8 or higher installed on your computer
- pip (Python package installer)

### Installation Steps

1. **Download the Project**
   - Download all the project files to a folder on your computer
   - Make sure you have all files including `app.py`, `main.py`, `models.py`, `routes.py`, `forms.py`, and the `templates/` and `static/` folders

2. **Install Required Packages**
   Open Command Prompt (Windows) or Terminal (Mac/Linux) in your project folder and run:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-WTF Flask-Mail WTForms email-validator Werkzeug SQLAlchemy
   ```

3. **Run the Application**
   In the same Command Prompt/Terminal, run:
   ```bash
   python main.py
   ```

4. **Access the Application**
   - Open your web browser
   - Go to: `http://localhost:5000`
   - You should see the Club Membership Portal homepage

### Default Admin Login
- Username: `admin`
- Password: `admin123`
- Admin panel: `http://localhost:5000/admin/login`

### Database
The application will automatically create a SQLite database file called `club_portal.db` in your project folder. No separate database server is needed.

### Features Available
✓ Browse available clubs
✓ Register for club membership
✓ Admin panel to approve/reject members
✓ Email notifications (if configured)
✓ Beautiful, responsive design

### Troubleshooting
- If you get a "Module not found" error, make sure you installed all packages using pip
- If port 5000 is busy, the application will try another port
- Make sure all project files are in the same folder

### Email Configuration (Optional)
To enable email notifications, set these environment variables before running:
- `MAIL_USERNAME=your_email@gmail.com`
- `MAIL_PASSWORD=your_app_password`
- `MAIL_SERVER=smtp.gmail.com`

If email is not configured, the application will still work but won't send email notifications.