from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional
from models import Club

class MemberRegistrationForm(FlaskForm):
    """Form for club membership registration"""
    student_name = StringField('Full Name', validators=[
        DataRequired(message="Please enter your full name"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(message="Please enter your email address"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message="Phone number must be less than 20 characters")
    ])
    
    student_id = StringField('Student ID', validators=[
        Optional(),
        Length(max=20, message="Student ID must be less than 20 characters")
    ])
    
    reason = TextAreaField('Why do you want to join this club?', validators=[
        Optional(),
        Length(max=500, message="Reason must be less than 500 characters")
    ])
    
    club_id = HiddenField('Club ID', validators=[DataRequired()])
    
    def validate_club_id(self, field):
        """Validate that the club exists"""
        club = Club.query.get(field.data)
        if not club:
            raise ValueError("Invalid club selected")

class AdminLoginForm(FlaskForm):
    """Form for admin login"""
    username = StringField('Username', validators=[
        DataRequired(message="Please enter your username")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password")
    ])

class MemberStatusForm(FlaskForm):
    """Form for updating member status"""
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], validators=[DataRequired()])
    
    member_id = HiddenField('Member ID', validators=[DataRequired()])

class EmailForm(FlaskForm):
    """Form for sending emails to members"""
    recipients = SelectField('Send To', choices=[
        ('all', 'All Members'),
        ('pending', 'Pending Members'),
        ('approved', 'Approved Members'),
        ('rejected', 'Rejected Members'),
        ('club', 'Members of Specific Club'),
        ('individual', 'Individual Member')
    ], validators=[DataRequired()])
    
    club_id = SelectField('Club (if selected)', coerce=int, validators=[Optional()])
    member_id = SelectField('Member (if selected)', coerce=int, validators=[Optional()])
    
    subject = StringField('Email Subject', validators=[
        DataRequired(message="Please enter email subject"),
        Length(max=200, message="Subject must be less than 200 characters")
    ])
    
    message = TextAreaField('Email Message', validators=[
        DataRequired(message="Please enter email message"),
        Length(max=2000, message="Message must be less than 2000 characters")
    ], render_kw={"rows": 8})
    
    send_as_html = SelectField('Message Format', choices=[
        ('plain', 'Plain Text'),
        ('html', 'HTML Format')
    ], default='html')
