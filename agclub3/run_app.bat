@echo off
echo Installing required packages...
pip install Flask Flask-SQLAlchemy Flask-WTF Flask-Mail WTForms email-validator Werkzeug SQLAlchemy

echo.
echo Starting Club Membership Portal...
echo Open your browser and go to: http://localhost:5000
echo Admin login: username=admin, password=admin123
echo.

python main.py
pause