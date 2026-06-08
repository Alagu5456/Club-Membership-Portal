import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@clubportal.com')

mail = Mail()

# Configure the database
# Use SQLite for local development if no DATABASE_URL is provided
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgresql"):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///club_portal.db"
# Configure engine options based on database type
if database_url and database_url.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # SQLite doesn't need pool settings
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

# Initialize the app with the extension
db.init_app(app)
mail.init_app(app)

# Admin credentials (in production, use proper authentication)
app.config["ADMIN_USERNAME"] = os.environ.get("ADMIN_USERNAME", "admin")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "admin123")

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Initialize sample clubs if none exist
    if not models.Club.query.first():
        sample_clubs = [
            models.Club(
                name="National Service Scheme (NSS)",
                description="A volunteer program for students to participate in community service and social development activities.",
                detailed_description="The National Service Scheme (NSS) is a Central Sector Scheme of Government of India, Ministry of Youth Affairs & Sports. It provides opportunity to the student youth of technical institutions, graduate & post graduate classes in Universities and Colleges to take part in various government led community service activities & programmes.",
                activities="Community service, Blood donation camps, Environmental awareness drives, Health camps, Literacy campaigns, Disaster relief work",
                meeting_schedule="Every Saturday 10:00 AM - 12:00 PM",
                contact_email="nss@college.edu",
                requirements="Must be a regular student with good academic standing. Commitment to serve the community.",
                benefits="Certificate of recognition, Leadership development, Community service experience, Government recognition",
                image_url="/static/images/nss.svg"
            ),
            models.Club(
                name="Coding Club",
                description="A community for programming enthusiasts to learn, share knowledge, and work on exciting projects together.",
                detailed_description="Join our vibrant coding community where innovation meets collaboration. Whether you're a beginner taking your first steps in programming or an experienced developer looking to expand your skills, our club offers a supportive environment for growth and learning.",
                activities="Weekly coding sessions, Hackathons, Tech talks, Project collaborations, Algorithm competitions, Open source contributions",
                meeting_schedule="Every Tuesday and Thursday 4:00 PM - 6:00 PM",
                contact_email="coding@college.edu",
                requirements="Basic computer literacy and enthusiasm to learn programming. No prior coding experience required.",
                benefits="Industry connections, Portfolio development, Internship opportunities, Technical skill enhancement",
                image_url="/static/images/coding.svg"
            ),
            models.Club(
                name="Literary Club",
                description="A platform for students passionate about literature, creative writing, poetry, and literary discussions.",
                detailed_description="Immerse yourself in the world of words and imagination. Our Literary Club is a sanctuary for book lovers, aspiring writers, and anyone who appreciates the beauty of language and storytelling.",
                activities="Book discussions, Creative writing workshops, Poetry recitations, Author interactions, Literary magazine publication, Storytelling events",
                meeting_schedule="Every Friday 3:00 PM - 5:00 PM",
                contact_email="literary@college.edu",
                requirements="Love for reading and writing. Open to all skill levels.",
                benefits="Publication opportunities, Writing skill development, Literary network, Creative expression platform",
                image_url="/static/images/literary.svg"
            ),
            models.Club(
                name="Photography Club",
                description="Capture moments and express creativity through the lens. Learn photography techniques and participate in photo walks.",
                detailed_description="Discover the art of visual storytelling through photography. From basic camera techniques to advanced composition, our club helps you develop your unique photographic style while exploring the world around you.",
                activities="Photo walks, Technical workshops, Portfolio reviews, Exhibition planning, Nature photography, Street photography, Portrait sessions",
                meeting_schedule="Every Sunday 8:00 AM - 11:00 AM (includes outdoor sessions)",
                contact_email="photography@college.edu",
                requirements="Own camera or smartphone with camera. Passion for visual arts.",
                benefits="Equipment access, Professional guidance, Exhibition opportunities, Photography contests",
                image_url="/static/images/photography.svg"
            ),
            models.Club(
                name="Debate Society",
                description="Develop public speaking skills and critical thinking through structured debates and discussions on current affairs.",
                detailed_description="Sharpen your intellect and eloquence in our Debate Society. We foster critical thinking, articulate expression, and confident public speaking through engaging debates on contemporary issues.",
                activities="Parliamentary debates, Impromptu speaking, Research and preparation, Inter-college competitions, Public speaking workshops, Current affairs discussions",
                meeting_schedule="Every Wednesday 5:00 PM - 7:00 PM",
                contact_email="debate@college.edu",
                requirements="Good command of English. Interest in current affairs and public speaking.",
                benefits="Leadership skills, Critical thinking, Confidence building, Competition opportunities",
                image_url="/static/images/debate.svg"
            ),
            models.Club(
                name="Music Club",
                description="A harmonious community for musicians of all levels to perform, learn, and appreciate various forms of music.",
                detailed_description="Let your musical talents shine in our inclusive Music Club. Whether you're a vocalist, instrumentalist, or music enthusiast, find your rhythm and create beautiful melodies with fellow musicians.",
                activities="Jam sessions, Music theory classes, Performance opportunities, Band formations, Music production workshops, Cultural event participation",
                meeting_schedule="Every Monday and Wednesday 6:00 PM - 8:00 PM",
                contact_email="music@college.edu",
                requirements="Basic musical knowledge or instrument playing ability. Passion for music.",
                benefits="Performance platform, Skill development, Recording opportunities, Music network",
                image_url="/static/images/music.svg"
            )
        ]
        
        for club in sample_clubs:
            db.session.add(club)
        
        try:
            db.session.commit()
            logging.info("Sample clubs initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing sample clubs: {e}")
            db.session.rollback()

# Import routes after app initialization
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
