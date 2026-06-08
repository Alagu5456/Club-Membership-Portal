from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Message
from app import app, db, mail
from models import Club, Member
from forms import MemberRegistrationForm, AdminLoginForm, MemberStatusForm, EmailForm
from sqlalchemy import or_
import logging

def send_email(to, subject, html_body, text_body=None):
    """Send email notification"""
    try:
        if app.config['MAIL_USERNAME']:  # Only send if email is configured
            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, str) else to,
                html=html_body,
                body=text_body,
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            logging.info(f"Email sent to {to}: {subject}")
            return True
        else:
            logging.warning("Email not configured - notification not sent")
            return False
    except Exception as e:
        logging.error(f"Failed to send email to {to}: {e}")
        return False

def format_email_message(message, member=None, club=None, format_type='html'):
    """Format email message with member and club variables"""
    # Replace variables in message
    if member:
        message = message.replace('{member_name}', member.student_name)
        message = message.replace('{member_email}', member.email)
        message = message.replace('{member_id}', str(member.id))
        if member.student_id:
            message = message.replace('{student_id}', member.student_id)
        if member.club:
            message = message.replace('{club_name}', member.club.name)
    
    if club:
        message = message.replace('{club_name}', club.name)
        message = message.replace('{club_description}', club.description)
    
    if format_type == 'html':
        # Convert line breaks to HTML
        message = message.replace('\n', '<br>')
        # Wrap in basic HTML structure
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            {message}
        </div>
        """
    
    return message

@app.route('/')
def club_list():
    """Display all available clubs"""
    clubs = Club.query.order_by(Club.name).all()
    return render_template('club_list.html', clubs=clubs)

@app.route('/club/<int:club_id>')
def club_details(club_id):
    """Display detailed information about a specific club"""
    club = Club.query.get_or_404(club_id)
    return render_template('club_details.html', club=club)

@app.route('/join/<int:club_id>', methods=['GET', 'POST'])
def join_club(club_id):
    """Show membership registration form and handle registration"""
    club = Club.query.get_or_404(club_id)
    form = MemberRegistrationForm()
    
    # Set the club_id in the form
    form.club_id.data = club_id
    
    app.logger.info(f"Form submission: method={request.method}, form_valid={form.validate_on_submit()}")
    
    if request.method == 'POST':
        app.logger.info(f"Form data: {form.data}")
        app.logger.info(f"Form errors: {form.errors}")
    
    if form.validate_on_submit():
        app.logger.info("Form validation passed, creating member...")
        
        # Check for duplicate registration
        existing_member = Member.query.filter_by(
            email=form.email.data,
            club_id=club_id
        ).first()
        
        if existing_member:
            flash('You have already registered for this club. Please check your email for updates.', 'warning')
            return redirect(url_for('join_club', club_id=club_id))
        
        # Create new member
        member = Member(
            student_name=form.student_name.data,
            email=form.email.data,
            phone=form.phone.data,
            student_id=form.student_id.data,
            club_id=club_id,
            reason=form.reason.data,
            status='Pending'
        )
        
        try:
            db.session.add(member)
            db.session.commit()
            app.logger.info(f"Member created successfully: {member.id}")
            flash('Registration successful! Your application is pending approval.', 'success')
            return redirect(url_for('confirmation', member_id=member.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            app.logger.error(f"Registration error: {e}")
    else:
        if request.method == 'POST':
            app.logger.warning(f"Form validation failed: {form.errors}")
    
    return render_template('join_club.html', club=club, form=form)

@app.route('/confirmation/<int:member_id>')
def confirmation(member_id):
    """Display confirmation page after successful registration"""
    member = Member.query.get_or_404(member_id)
    return render_template('confirmation.html', member=member)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check credentials (in production, use proper authentication)
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_members'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('club_list'))

@app.route('/admin/members')
def admin_members():
    """Admin dashboard to view and manage member applications"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    club_filter = request.args.get('club', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # Base query
    query = Member.query
    
    # Apply filters
    if club_filter:
        query = query.filter(Member.club_id == club_filter)
    
    if status_filter:
        query = query.filter(Member.status == status_filter)
    
    if search_query:
        query = query.filter(
            or_(
                Member.student_name.ilike(f'%{search_query}%'),
                Member.email.ilike(f'%{search_query}%')
            )
        )
    
    # Get members with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    members = query.order_by(Member.joined_on.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all clubs for filter dropdown
    clubs = Club.query.order_by(Club.name).all()
    
    return render_template('admin_members.html', 
                         members=members, 
                         clubs=clubs,
                         club_filter=club_filter,
                         status_filter=status_filter,
                         search_query=search_query)

@app.route('/admin/update_member_status', methods=['POST'])
def update_member_status():
    """Update member status (approve/reject)"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))
    
    member_id = request.form.get('member_id')
    new_status = request.form.get('status')
    
    if not member_id or not new_status:
        flash('Invalid request.', 'danger')
        return redirect(url_for('admin_members'))
    
    member = Member.query.get(member_id)
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('admin_members'))
    
    old_status = member.status
    member.status = new_status
    
    try:
        db.session.commit()
        flash(f'Member {member.student_name} status updated from {old_status} to {new_status}.', 'success')
        
        # Send email notification
        if new_status in ['Approved', 'Rejected']:
            subject = f"Club Membership Application - {new_status}"
            
            if new_status == 'Approved':
                email_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                    <div style="background-color: #28a745; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h2 style="margin: 0;">🎉 Congratulations!</h2>
                    </div>
                    <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <p>Dear {member.student_name},</p>
                        <p>We are delighted to inform you that your application for <strong>{member.club.name}</strong> has been <strong style="color: #28a745;">APPROVED</strong>!</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h4 style="color: #495057; margin-bottom: 10px;">Next Steps:</h4>
                            <ul style="color: #6c757d;">
                                <li>Check your student email for meeting schedules</li>
                                <li>Join our club communication channels</li>
                                <li>Attend the next club meeting: {member.club.meeting_schedule or 'TBA'}</li>
                            </ul>
                        </div>
                        
                        <p>For any questions, please contact us at: <a href="mailto:{member.club.contact_email or 'info@clubportal.com'}" style="color: #007bff;">{member.club.contact_email or 'info@clubportal.com'}</a></p>
                        
                        <p>Welcome to the {member.club.name} family!</p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; margin: 0;">Best regards,<br><strong>{member.club.name} Team</strong></p>
                        </div>
                    </div>
                </div>
                """
            else:  # Rejected
                email_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                    <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h2 style="margin: 0;">Application Update</h2>
                    </div>
                    <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <p>Dear {member.student_name},</p>
                        <p>Thank you for your interest in joining <strong>{member.club.name}</strong>.</p>
                        
                        <p>After careful consideration, we regret to inform you that your application has not been accepted at this time.</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h4 style="color: #495057; margin-bottom: 10px;">What's Next:</h4>
                            <ul style="color: #6c757d;">
                                <li>You can reapply in the next recruitment cycle</li>
                                <li>Consider joining other clubs that match your interests</li>
                                <li>Contact us for feedback on your application</li>
                            </ul>
                        </div>
                        
                        <p>For any questions, please contact us at: <a href="mailto:{member.club.contact_email or 'info@clubportal.com'}" style="color: #007bff;">{member.club.contact_email or 'info@clubportal.com'}</a></p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; margin: 0;">Best regards,<br><strong>{member.club.name} Team</strong></p>
                        </div>
                    </div>
                </div>
                """
            
            send_email(member.email, subject, email_body)
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the member status.', 'danger')
        app.logger.error(f"Status update error: {e}")
    
    return redirect(url_for('admin_members'))

@app.route('/admin/export_members')
def export_members():
    """Export club members as CSV"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))
    
    import csv
    import io
    from flask import make_response
    
    # Get filter parameters
    club_filter = request.args.get('club', '')
    status_filter = request.args.get('status', '')
    
    # Base query
    query = Member.query
    
    # Apply filters
    if club_filter:
        query = query.filter(Member.club_id == club_filter)
    
    if status_filter:
        query = query.filter(Member.status == status_filter)
    
    members = query.order_by(Member.joined_on.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Email', 'Phone', 'Student ID', 'Club', 'Status', 'Joined On', 'Reason'])
    
    # Write data
    for member in members:
        writer.writerow([
            member.student_name,
            member.email,
            member.phone or '',
            member.student_id or '',
            member.club.name,
            member.status,
            member.joined_on.strftime('%Y-%m-%d %H:%M:%S'),
            member.reason or ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=club_members.csv'
    
    return response

@app.route('/admin/send_email', methods=['GET', 'POST'])
def admin_send_email():
    """Admin interface for sending emails to members"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))
    
    form = EmailForm()
    
    # Populate form choices
    clubs = Club.query.order_by(Club.name).all()
    form.club_id.choices = [(0, 'Select a club')] + [(club.id, club.name) for club in clubs]
    
    members = Member.query.order_by(Member.student_name).all()
    form.member_id.choices = [(0, 'Select a member')] + [(member.id, f"{member.student_name} ({member.club.name})") for member in members]
    
    if form.validate_on_submit():
        # Determine recipients
        recipients = []
        recipient_type = form.recipients.data
        
        if recipient_type == 'all':
            recipients = Member.query.all()
        elif recipient_type == 'pending':
            recipients = Member.query.filter_by(status='Pending').all()
        elif recipient_type == 'approved':
            recipients = Member.query.filter_by(status='Approved').all()
        elif recipient_type == 'rejected':
            recipients = Member.query.filter_by(status='Rejected').all()
        elif recipient_type == 'club' and form.club_id.data:
            recipients = Member.query.filter_by(club_id=form.club_id.data).all()
        elif recipient_type == 'individual' and form.member_id.data:
            recipients = [Member.query.get(form.member_id.data)]
        
        if not recipients:
            flash('No recipients selected or found.', 'warning')
            return render_template('admin_send_email.html', form=form, clubs=clubs, members=members)
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        for member in recipients:
            # Format message with variables
            formatted_message = format_email_message(
                form.message.data, 
                member=member, 
                club=member.club,
                format_type=form.send_as_html.data
            )
            
            # Send email
            if form.send_as_html.data == 'html':
                success = send_email(member.email, form.subject.data, formatted_message)
            else:
                success = send_email(member.email, form.subject.data, None, formatted_message)
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        if sent_count > 0:
            flash(f'Successfully sent {sent_count} email(s).', 'success')
        if failed_count > 0:
            flash(f'Failed to send {failed_count} email(s).', 'warning')
        
        return redirect(url_for('admin_send_email'))
    
    return render_template('admin_send_email.html', form=form, clubs=clubs, members=members)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('base.html', error_message="An internal error occurred"), 500
