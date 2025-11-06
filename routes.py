from flask import render_template, request, redirect, url_for, session, flash, send_file, current_app
from app import app, db
from models import Client, Fingerprint
from forms import PersonalDetailsForm, FingerprintUploadForm, FaceCaptureForm
from utils import save_uploaded_file, save_face_photo, generate_pdf_report, calculate_age, get_zodiac_sign
import os
import uuid
from datetime import datetime

@app.route('/')
def index():
    """Renders the landing page using the index.html template."""
    return render_template('index.html')

@app.route('/step0', methods=['GET', 'POST'])
def step0_face_capture():
    """Handles Step 0, capturing the user's face photo via webcam."""
    form = FaceCaptureForm()
    
    if form.validate_on_submit():
        try:
            # Generate session ID if not exists
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            # Save face photo
            face_data = form.face_image_data.data
            file_info = save_face_photo(face_data, session['session_id'], current_app.config['UPLOAD_FOLDER'])
            
            # Store face photo path in session
            session['face_photo_path'] = file_info['file_path']
            
            flash('Photo captured successfully!', 'success')
            return redirect(url_for('step1_personal_details'))
        
        except Exception as e:
            current_app.logger.error(f"Error saving face photo: {str(e)}")
            flash('Error capturing photo. Please try again.', 'danger')
    
    return render_template('step0_face_capture.html', form=form)

@app.route('/step1', methods=['GET', 'POST'])
def step1_personal_details():
    """Handles Step 1, rendering the personal details form using step1.html."""
    form = PersonalDetailsForm()

    # If returning from step 2, pre-populate the form with session data
    if 'client_data' in session and request.method == 'GET':
        client_data = session['client_data']
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
        # Store form data in the session to carry it to the next step
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

        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        flash('Personal details saved. Please upload your fingerprints.', 'success')
        return redirect(url_for('step2_fingerprints'))

    return render_template('step1.html', form=form)


@app.route('/step2', methods=['GET', 'POST'])
def step2_fingerprints():
    """Handles Step 2, rendering the fingerprint upload form using step2.html."""
    if 'client_data' not in session:
        flash('Please complete the personal details first.', 'warning')
        return redirect(url_for('step1_personal_details'))

    form = FingerprintUploadForm()

    if form.validate_on_submit():
        if form.back.data:
            return redirect(url_for('step1_personal_details'))

        try:
            form.validate_fingerprints()

            client_data = session['client_data']
            client = Client(
                session_id=session['session_id'],
                face_photo=session.get('face_photo_path'),
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
            db.session.flush()

            fingerprint_fields = ['L1', 'L2', 'L3', 'L4', 'L5', 'R1', 'R2', 'R3', 'R4', 'R5']
            uploaded_fingerprints = []
            for field_name in fingerprint_fields:
                field = getattr(form, field_name)
                if field.data:
                    file_info = save_uploaded_file(field.data, client.session_id, field_name, current_app.config['UPLOAD_FOLDER'])
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
            session['client_id'] = client.id
            flash(f'Application submitted successfully! {len(uploaded_fingerprints)} fingerprints uploaded.', 'success')
            return redirect(url_for('submission_success'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during submission: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')

    return render_template('step2.html', form=form, client_data=session.get('client_data'))

@app.route('/success')
def submission_success():
    """Displays the success page using success.html."""
    client_id = session.get('client_id')
    if not client_id:
        flash('No submission found.', 'error')
        return redirect(url_for('index'))
    
    client = Client.query.get(client_id)
    if not client:
        flash('Submission data not found.', 'error')
        return redirect(url_for('index'))

    age = calculate_age(client.date_of_birth)
    zodiac_sign = get_zodiac_sign(client.date_of_birth)
    
    # Clear session data after it's been used
    session.pop('client_data', None)
    session.pop('session_id', None)

    return render_template('success.html', 
                         client=client, 
                         age=age, 
                         zodiac_sign=zodiac_sign,
                         fingerprint_count=len(client.fingerprints))


@app.route('/download_pdf/<int:client_id>')
def download_pdf(client_id):
    """Generates and serves the PDF report for the given client."""
    # Ensure the client_id from the URL matches the one from the successful session
    if 'client_id' not in session or session['client_id'] != client_id:
        flash('Unauthorized access to download.', 'error')
        return redirect(url_for('index'))

    client = Client.query.get_or_404(client_id)
    
    try:
        pdf_path = generate_pdf_report(client)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'Astrology_Report_{client.first_name}_{client.last_name}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"PDF Generation Error: {str(e)}")
        flash('Could not generate your PDF report. Please contact support.', 'danger')
        return redirect(url_for('submission_success'))

@app.route('/new_session')
def new_session():
    """Clears the session to start a new application."""
    session.clear()
    flash('New session started.', 'info')
    return redirect(url_for('index'))

# --- Error Handlers ---

@app.errorhandler(413)
def too_large(e):
    flash('File size is too large. Please upload images smaller than 16MB.', 'danger')
    return redirect(request.referrer or url_for('step2_fingerprints'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404 # Assuming you have a 404.html template

@app.errorhandler(500)
def server_error(e):
    current_app.logger.error(f"Server Error: {str(e)}")
    return render_template('500.html'), 500 # Assuming you have a 500.html template

