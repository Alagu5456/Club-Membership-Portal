from app import db
from datetime import datetime
from sqlalchemy import func

class Club(db.Model):
    """Model for campus clubs"""
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    detailed_description = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    meeting_schedule = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with members
    members = db.relationship('Member', backref='club', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Club {self.name}>'
    
    def get_member_count(self):
        """Get total number of members for this club"""
        return Member.query.filter_by(club_id=self.id).count()
    
    def get_approved_member_count(self):
        """Get number of approved members for this club"""
        return Member.query.filter_by(club_id=self.id, status='Approved').count()
    
    def get_pending_member_count(self):
        """Get number of pending members for this club"""
        return Member.query.filter_by(club_id=self.id, status='Pending').count()

class Member(db.Model):
    """Model for club members"""
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    student_id = db.Column(db.String(20), nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Approved, Rejected
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text, nullable=True)  # Reason for joining
    
    def __repr__(self):
        return f'<Member {self.student_name} - {self.club.name}>'
    
    def is_duplicate(self):
        """Check if this member already exists for the same club"""
        existing_member = Member.query.filter_by(
            email=self.email,
            club_id=self.club_id
        ).filter(Member.id != self.id).first()
        return existing_member is not None
    
    @staticmethod
    def get_members_by_club(club_id):
        """Get all members for a specific club"""
        return Member.query.filter_by(club_id=club_id).order_by(Member.joined_on.desc()).all()
    
    @staticmethod
    def get_members_by_status(status):
        """Get all members with a specific status"""
        return Member.query.filter_by(status=status).order_by(Member.joined_on.desc()).all()
    
    @staticmethod
    def search_members(query):
        """Search members by name or email"""
        return Member.query.filter(
            db.or_(
                Member.student_name.ilike(f'%{query}%'),
                Member.email.ilike(f'%{query}%')
            )
        ).order_by(Member.joined_on.desc()).all()
