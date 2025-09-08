from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp
from datetime import date

class PersonalDetailsForm(FlaskForm):
    """Form for collecting the user's personal information."""
    title = SelectField('Title', choices=[('', 'Select Title'), ('Mr.', 'Mr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Ms.')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    middle_name = StringField('Middle Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Regexp(r'^\+?[\d\s\-()]{10,15}$', message="Invalid mobile number.")])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    next_step = SubmitField('Next: Upload Fingerprints')

    def validate_date_of_birth(self, field):
        if field.data and field.data > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        if field.data and field.data < date(1920, 1, 1):
            raise ValidationError("Please enter a valid date of birth.")

class FingerprintUploadForm(FlaskForm):
    """Form for uploading fingerprint images for all 10 fingers."""
    allowed_files = ['jpg', 'jpeg', 'png']
    
    # Left Hand
    L1 = FileField('Left Thumb (L1)', validators=[FileAllowed(allowed_files, 'Images only!')])
    L2 = FileField('Left Index (L2)', validators=[FileAllowed(allowed_files, 'Images only!')])
    L3 = FileField('Left Middle (L3)', validators=[FileAllowed(allowed_files, 'Images only!')])
    L4 = FileField('Left Ring (L4)', validators=[FileAllowed(allowed_files, 'Images only!')])
    L5 = FileField('Left Pinky (L5)', validators=[FileAllowed(allowed_files, 'Images only!')])
    
    # Right Hand
    R1 = FileField('Right Thumb (R1)', validators=[FileAllowed(allowed_files, 'Images only!')])
    R2 = FileField('Right Index (R2)', validators=[FileAllowed(allowed_files, 'Images only!')])
    R3 = FileField('Right Middle (R3)', validators=[FileAllowed(allowed_files, 'Images only!')])
    R4 = FileField('Right Ring (R4)', validators=[FileAllowed(allowed_files, 'Images only!')])
    R5 = FileField('Right Pinky (R5)', validators=[FileAllowed(allowed_files, 'Images only!')])
    
    remarks = TextAreaField('Remarks (Optional)', validators=[Length(max=1000)])
    
    submit = SubmitField('Submit Application')
    back = SubmitField('Back to Personal Details')

    def validate_fingerprints(self):
        """Custom validator to ensure at least one fingerprint image is uploaded."""
        fingerprint_fields = ['L1', 'L2', 'L3', 'L4', 'L5', 'R1', 'R2', 'R3', 'R4', 'R5']
        if not any(getattr(self, field).data for field in fingerprint_fields):
            raise ValidationError("Please upload at least one fingerprint image.")
        return True
