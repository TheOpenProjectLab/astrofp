import os
import uuid
from datetime import datetime, date
from PIL import Image
import secrets
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import tempfile

def save_face_photo(image_data, session_id, upload_folder):
    """
    Save face photo from base64 data
    """
    if not image_data or not image_data.startswith('data:image'):
        raise ValueError("Invalid image data")
    
    # Extract base64 data
    header, encoded = image_data.split(',', 1)
    image_bytes = base64.b64decode(encoded)
    
    # Generate unique filename
    unique_filename = f"{session_id}_face_{secrets.token_hex(8)}.jpg"
    
    # Create session-specific directory
    session_dir = os.path.join(upload_folder, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_path = os.path.join(session_dir, unique_filename)
    
    # Save and validate image
    try:
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        # Validate and optimize image
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            max_dimension = 1024
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save optimized version
            img.save(file_path, 'JPEG', optimize=True, quality=85)
        
        file_size = os.path.getsize(file_path)
        
        return {
            'filename': unique_filename,
            'file_path': file_path,
            'file_size': file_size
        }
    
    except Exception as e:
        # Clean up file if validation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise ValueError(f"Invalid image file: {str(e)}")

def save_uploaded_file(file, session_id, finger_position, upload_folder):
    """
    Save uploaded fingerprint file with validation and processing
    """
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise ValueError("Invalid file type. Only PNG, JPG, and JPEG files are allowed.")
    
    # Generate unique filename
    unique_filename = f"{session_id}_{finger_position}_{secrets.token_hex(8)}.{file_extension}"
    
    # Create session-specific directory
    session_dir = os.path.join(upload_folder, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_path = os.path.join(session_dir, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Validate and process image
    try:
        with Image.open(file_path) as img:
            # Validate image
            if img.format not in ['JPEG', 'PNG']:
                os.remove(file_path)
                raise ValueError("Invalid image format")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Optional: Resize if image is too large (while maintaining aspect ratio)
            max_dimension = 2000
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
                file_size = os.path.getsize(file_path)
    
    except Exception as e:
        # Clean up file if validation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise ValueError(f"Invalid image file: {str(e)}")
    
    return {
        'filename': unique_filename,
        'original_filename': file.filename,
        'file_path': file_path,
        'file_size': file_size
    }

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_zodiac_sign(birth_date):
    """Get zodiac sign from birth date"""
    month = birth_date.month
    day = birth_date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries ♈"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus ♉"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini ♊"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer ♋"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo ♌"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo ♍"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra ♎"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio ♏"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius ♐"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn ♑"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius ♒"
    else:
        return "Pisces ♓"

def generate_pdf_report(client):
    """Generate PDF report with client details and fingerprints"""
    # Create temporary file for PDF
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_pdf.name
    temp_pdf.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#2C3E50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#34495E')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    # Title
    title = Paragraph("Astrological Client Profile & Fingerprint Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Add face photo if available
    if client.face_photo and os.path.exists(client.face_photo):
        try:
            face_photo_heading = Paragraph("Client Photo", heading_style)
            story.append(face_photo_heading)
            story.append(Spacer(1, 10))
            
            # Add face photo - centered
            face_img = RLImage(client.face_photo, width=2.5*inch, height=2.5*inch, kind='proportional')
            
            # Create a table to center the image
            photo_table = Table([[face_img]], colWidths=[2.5*inch])
            photo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(photo_table)
            story.append(Spacer(1, 20))
        except Exception as e:
            # Skip if photo can't be loaded
            pass
    
    # Client Information Section
    client_heading = Paragraph("Personal Information", heading_style)
    story.append(client_heading)
    
    # Calculate additional info
    age = calculate_age(client.date_of_birth)
    zodiac_sign = get_zodiac_sign(client.date_of_birth)
    
    # Personal details table
    personal_data = [
        ['Full Name:', client.full_name],
        ['Gender:', client.gender],
        ['Date of Birth:', client.date_of_birth.strftime('%B %d, %Y')],
        ['Age:', f'{age} years'],
        ['Zodiac Sign:', zodiac_sign],
        ['Mobile Number:', client.mobile_number],
        ['Email Address:', client.email],
        ['Address:', client.address],
    ]
    
    if client.remarks:
        personal_data.append(['Remarks:', client.remarks])
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Fingerprints Section
    if client.fingerprints:
        fingerprint_heading = Paragraph("Fingerprint Records", heading_style)
        story.append(fingerprint_heading)
        
        # Fingerprint summary
        summary_text = f"Total fingerprints collected: {len(client.fingerprints)}"
        summary = Paragraph(summary_text, normal_style)
        story.append(summary)
        story.append(Spacer(1, 10))
        
        # Group fingerprints by hand
        left_fingers = []
        right_fingers = []
        
        finger_names = {
            'L1': 'Left Thumb', 'L2': 'Left Index', 'L3': 'Left Middle', 'L4': 'Left Ring', 'L5': 'Left Pinky',
            'R1': 'Right Thumb', 'R2': 'Right Index', 'R3': 'Right Middle', 'R4': 'Right Ring', 'R5': 'Right Pinky'
        }
        
        for fingerprint in client.fingerprints:
            finger_data = [
                finger_names.get(fingerprint.finger_position, fingerprint.finger_position),
                fingerprint.original_filename,
                f"{fingerprint.file_size // 1024} KB",
                fingerprint.uploaded_at.strftime('%Y-%m-%d %H:%M')
            ]
            
            if fingerprint.finger_position.startswith('L'):
                left_fingers.append(finger_data)
            else:
                right_fingers.append(finger_data)
        
        # Fingerprint table
        fingerprint_data = [['Finger Position', 'Original Filename', 'File Size', 'Upload Time']]
        fingerprint_data.extend(left_fingers)
        fingerprint_data.extend(right_fingers)
        
        fingerprint_table = Table(fingerprint_data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
        fingerprint_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        
        story.append(fingerprint_table)
        story.append(Spacer(1, 20))
        
        # Add fingerprint images if they exist
        fingerprint_images_added = 0
        for fingerprint in sorted(client.fingerprints, key=lambda x: x.finger_position):
            if os.path.exists(fingerprint.file_path) and fingerprint_images_added < 10:  # Limit to prevent PDF from becoming too large
                try:
                    # Add fingerprint image
                    img_paragraph = Paragraph(f"<b>{finger_names.get(fingerprint.finger_position, fingerprint.finger_position)}</b>", normal_style)
                    story.append(img_paragraph)
                    
                    # Resize image for PDF
                    img = RLImage(fingerprint.file_path, width=2*inch, height=2*inch, kind='proportional')
                    story.append(img)
                    story.append(Spacer(1, 10))
                    fingerprint_images_added += 1
                except Exception as e:
                    # Skip problematic images
                    continue
    
    # Footer information
    story.append(Spacer(1, 20))
    footer_text = f"Report generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>Session ID: {client.session_id}"
    footer = Paragraph(footer_text, normal_style)
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    return pdf_path
