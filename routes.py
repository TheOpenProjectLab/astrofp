from flask import render_template, request, redirect, url_for, session, flash, send_file, current_app
from app import app, db
from models import Client, Fingerprint
from forms import PersonalDetailsForm, FingerprintUploadForm
from utils import save_uploaded_file, generate_pdf_report, calculate_age, get_zodiac_sign
import os
import uuid
from datetime import datetime

@app.route('/')
def index():
    """Landing page for the astrology fingerprint collection app"""
    return render_template('index.html')

@app.route('/step1', methods=['GET', 'POST'])
def step1_personal_details():
    """Step 1: Collect personal details"""
    form = PersonalDetailsForm()
    
    # Pre-populate form if returning from step 2
    if 'client_data' in session:
        client_data = session['client_data']
        if request.method == 'GET':
            form.title.data = client_data.get('title')
            form.first_name.data = client_data.get('first_name')
            form.middle_name.data = client_data.get('middle_name')
            form.last_name.data = client_data.get('last_name')
            form.gender.data = client_data.get('gender')
            form.date_of_birth.data = datetime.strptime(client_data.get('date_of_birth'), '%Y-%m-%d').date() if client_data.get('date_of_birth') else None
            form.mobile_number.data = client_data.get('mobile_number')
            form.email.data = client_data.get('email')
            form.address.data = client_data.get('address')
    
    if form.validate_on_submit():
        # Store form data in session
        session['client_data'] = {
            'title': form.title.data,
            'first_name': form.first_name.data,
            'middle_name': form.middle_name.data,
            'last_name': form.last_name.data,
            'gender': form.gender.data,
            'date_of_birth': form.date_of_birth.data.strftime('%Y-%m-%d'),
            'mobile_number': form.mobile_number.data,
            'email': form.email.data,
            'address': form.address.data
        }
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        flash('Personal details saved. Please upload your fingerprints.', 'success')
        return redirect(url_for('step2_fingerprints'))
    
    return render_template('step1.html', form=form)

@app.route('/step2', methods=['GET', 'POST'])
def step2_fingerprints():
    """Step 2: Upload fingerprint images"""
    if 'client_data' not in session:
        flash('Please complete the personal details first.', 'error')
        return redirect(url_for('step1_personal_details'))
    
    form = FingerprintUploadForm()
    
    if form.validate_on_submit():
        if form.back.data:
            # Go back to step 1
            return redirect(url_for('step1_personal_details'))
        
        try:
            # Validate at least one fingerprint is uploaded
            form.validate_fingerprints()
            
            # Create client record
            client_data = session['client_data']
            client = Client(
                session_id=session['session_id'],
                title=client_data.get('title'),
                first_name=client_data['first_name'],
                middle_name=client_data.get('middle_name'),
                last_name=client_data['last_name'],
                gender=client_data['gender'],
                date_of_birth=datetime.strptime(client_data['date_of_birth'], '%Y-%m-%d').date(),
                mobile_number=client_data['mobile_number'],
                email=client_data['email'],
                address=client_data['address'],
                remarks=form.remarks.data
            )
            
            db.session.add(client)
            db.session.flush()  # Get the client ID
            
            # Process fingerprint uploads
            fingerprint_fields = ['L1', 'L2', 'L3', 'L4', 'L5', 'R1', 'R2', 'R3', 'R4', 'R5']
            uploaded_fingerprints = []
            
            for field_name in fingerprint_fields:
                field = getattr(form, field_name)
                if field.data:
                    file_info = save_uploaded_file(
                        field.data, 
                        client.session_id, 
                        field_name, 
                        current_app.config['UPLOAD_FOLDER']
                    )
                    
                    fingerprint = Fingerprint(
                        client_id=client.id,
                        finger_position=field_name,
                        filename=file_info['filename'],
                        original_filename=file_info['original_filename'],
                        file_path=file_info['file_path'],
                        file_size=file_info['file_size']
                    )
                    
                    db.session.add(fingerprint)
                    uploaded_fingerprints.append(fingerprint)
            
            db.session.commit()
            
            # Store client ID in session for PDF generation
            session['client_id'] = client.id
            
            flash(f'Application submitted successfully! {len(uploaded_fingerprints)} fingerprints uploaded.', 'success')
            return redirect(url_for('submission_success'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error submitting application: {str(e)}")
            flash('An error occurred while submitting your application. Please try again.', 'error')
    
    return render_template('step2.html', form=form, client_data=session.get('client_data'))

@app.route('/success')
def submission_success():
    """Success page with PDF download option"""
    if 'client_id' not in session:
        flash('No submission found.', 'error')
        return redirect(url_for('index'))
    
    client = Client.query.get(session['client_id'])
    if not client:
        flash('Submission not found.', 'error')
        return redirect(url_for('index'))
    
    # Calculate additional info
    age = calculate_age(client.date_of_birth)
    zodiac_sign = get_zodiac_sign(client.date_of_birth)
    
    return render_template('success.html', 
                         client=client, 
                         age=age, 
                         zodiac_sign=zodiac_sign,
                         fingerprint_count=len(client.fingerprints))

@app.route('/download_pdf/<int:client_id>')
def download_pdf(client_id):
    """Generate and download PDF report"""
    if 'client_id' not in session or session['client_id'] != client_id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))
    
    client = Client.query.get_or_404(client_id)
    
    try:
        pdf_path = generate_pdf_report(client)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'astrology_report_{client.first_name}_{client.last_name}_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        flash('Error generating PDF report. Please try again.', 'error')
        return redirect(url_for('submission_success'))

@app.route('/new_session')
def new_session():
    """Clear session and start new application"""
    session.clear()
    flash('Started new session.', 'info')
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Please upload images smaller than 16MB.', 'error')
    return redirect(url_for('step2_fingerprints'))

@app.errorhandler(404)
def not_found(e):
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def server_error(e):
    current_app.logger.error(f"Server error: {str(e)}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))
