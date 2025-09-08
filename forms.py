from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp
from datetime import datetime, date

class PersonalDetailsForm(FlaskForm):
    title = SelectField('Title', choices=[
        ('', 'Select Title'),
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Ms.'),
        ('Dr.', 'Dr.'),
        ('Prof.', 'Prof.')
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(min=2, max=50, message="First name must be between 2 and 50 characters")
    ])
    
    middle_name = StringField('Middle Name', validators=[
        Length(max=50, message="Middle name cannot exceed 50 characters")
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message="Last name is required"),
        Length(min=2, max=50, message="Last name must be between 2 and 50 characters")
    ])
    
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired(message="Please select your gender")])
    
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(message="Date of birth is required")
    ])
    
    mobile_number = StringField('Mobile Number', validators=[
        DataRequired(message="Mobile number is required"),
        Regexp(r'^\+?[\d\s\-\(\)]{10,15}$', message="Please enter a valid mobile number")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    
    address = TextAreaField('Address', validators=[
        DataRequired(message="Address is required"),
        Length(min=10, max=500, message="Address must be between 10 and 500 characters")
    ])
    
    next_step = SubmitField('Next: Upload Fingerprints')
    
    def validate_date_of_birth(self, field):
        if field.data and field.data > date.today():
            raise ValidationError("Date of birth cannot be in the future")
        if field.data and field.data < date(1900, 1, 1):
            raise ValidationError("Please enter a valid date of birth")

class FingerprintUploadForm(FlaskForm):
    # Left hand fingerprints
    L1 = FileField('Left Thumb (L1)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    L2 = FileField('Left Index (L2)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    L3 = FileField('Left Middle (L3)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    L4 = FileField('Left Ring (L4)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    L5 = FileField('Left Pinky (L5)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    
    # Right hand fingerprints
    R1 = FileField('Right Thumb (R1)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    R2 = FileField('Right Index (R2)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    R3 = FileField('Right Middle (R3)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    R4 = FileField('Right Ring (R4)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    R5 = FileField('Right Pinky (R5)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
    ])
    
    remarks = TextAreaField('Remarks (Optional)', validators=[
        Length(max=1000, message="Remarks cannot exceed 1000 characters")
    ])
    
    submit = SubmitField('Submit Application')
    back = SubmitField('Back to Personal Details')
    
    def validate_fingerprints(self):
        """Custom validation to ensure at least one fingerprint is uploaded"""
        fingerprint_fields = ['L1', 'L2', 'L3', 'L4', 'L5', 'R1', 'R2', 'R3', 'R4', 'R5']
        uploaded_count = 0
        
        for field_name in fingerprint_fields:
            field = getattr(self, field_name)
            if field.data:
                uploaded_count += 1
        
        if uploaded_count == 0:
            raise ValidationError("Please upload at least one fingerprint image")
        
        return True
