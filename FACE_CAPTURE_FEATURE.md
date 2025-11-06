# Face Capture Feature Documentation

## Overview
The Face Capture feature has been added to the Astrology Fingerprint Report Generator app. This feature captures the user's photo via webcam **before** the personal details form (Step 1) and includes it in the generated PDF report.

## Feature Summary

### What's New
- **New Step 0**: Face capture via webcam before personal details
- **4-Step Process**: Face Capture → Personal Details → Fingerprints → Complete
- **PDF Integration**: Captured face photo is now included at the top of the PDF report
- **Webcam Integration**: Real-time webcam capture with countdown timer and preview
- **Image Optimization**: Automatic image compression and optimization

## Technical Implementation

### 1. Database Changes (`models.py`)
Added new field to the `Client` model:
```python
face_photo = db.Column(db.String(500))  # Path to face photo
```

### 2. New Form (`forms.py`)
Created `FaceCaptureForm` with:
- `face_image_data`: Hidden field storing base64 image data
- Validation to ensure photo is captured before proceeding

### 3. New Template (`templates/step0_face_capture.html`)
Features:
- Real-time webcam preview
- Oval overlay guide for face positioning
- 3-second countdown before capture
- Photo preview with retake option
- Camera permission error handling
- Skip option if camera unavailable

### 4. Routes Update (`routes.py`)
- **New route**: `/step0` - Face capture handler
- Generates session ID
- Saves captured photo using base64 data
- Stores photo path in session for later database save

### 5. Utilities Update (`utils.py`)
**New function**: `save_face_photo(image_data, session_id, upload_folder)`
- Decodes base64 image data
- Saves as optimized JPEG
- Validates image format
- Resizes if needed (max 1024px)
- Returns file metadata

**Updated function**: `generate_pdf_report(client)`
- Now includes face photo at the top of PDF (if available)
- Photo displayed as 2.5" × 2.5" centered image
- Gracefully handles missing photos

### 6. Template Updates
All templates updated to show **4-step process**:

**index.html**:
- Updated to 4-step process display
- All links now point to `step0_face_capture`
- Added face photo mention in "What We Collect"

**step1.html**:
- Progress indicator updated (Step 0 completed, Step 2 active)
- Header changed to "Step 2: Personal Information"

**step2.html**:
- Progress indicator updated (Steps 0-1 completed, Step 3 active)
- Header changed to "Step 3: Fingerprint Upload"

**success.html**:
- Progress indicator shows all 4 steps completed
- Report preview mentions captured photo

## User Flow

### Step 0: Face Capture
1. User lands on index page
2. Clicks "Start Your Reading"
3. Redirected to `/step0` (Face Capture)
4. Browser requests camera permission
5. User positions face in oval guide
6. Clicks capture button (3-second countdown)
7. Preview shown with retake option
8. User clicks "Continue to Personal Details"
9. Photo saved and session created

### Step 1: Personal Details
(Previously Step 1, now Step 2)
- Face photo path already in session
- User fills personal information
- Continues to fingerprints

### Step 2: Fingerprints
(Previously Step 2, now Step 3)
- User uploads fingerprint images
- On submit, `Client` record created with:
  - Face photo path from session
  - Personal details
  - Fingerprint images

### Step 3: Complete
(Previously Step 3, now Step 4)
- Success page shown
- PDF generated with face photo included
- User downloads comprehensive report

## PDF Report Structure

The generated PDF now includes:
1. **Title**: Astrological Client Profile & Fingerprint Report
2. **Client Photo** (NEW): Centered, 2.5" × 2.5" image
3. **Personal Information**: Table with all details
4. **Fingerprint Records**: Summary table
5. **Fingerprint Images**: All uploaded fingerprints
6. **Footer**: Timestamp and session ID

## File Storage

Photos are stored in:
```
static/uploads/{session_id}/
  ├── {session_id}_face_{random}.jpg
  ├── {session_id}_L1_{random}.jpg
  ├── {session_id}_R1_{random}.jpg
  └── ...
```

## Browser Compatibility

Webcam capture requires:
- **getUserMedia API** support
- **HTTPS** or **localhost** (for security)
- Modern browsers: Chrome 53+, Firefox 36+, Safari 11+, Edge 12+

## Error Handling

### Camera Access Denied
- Clear error message displayed
- Instructions to grant permissions
- **Skip option**: Link to proceed to Step 1 without photo
- Retry button to reload page

### No Camera Available
- Detection of missing camera
- Fallback to skip option
- App continues to function without photo

### Image Processing Errors
- Validation of image format
- Auto-conversion to RGB if needed
- Compression to optimize file size
- Cleanup on failure

## Security Considerations

1. **Base64 Validation**: Ensures data is valid image format
2. **File Type Checking**: Converts to JPEG only
3. **Size Limits**: Images resized to max 1024px
4. **Session Isolation**: Photos stored in session-specific folders
5. **CSRF Protection**: Form includes CSRF tokens
6. **Temporary Storage**: Photos deleted after session

## Testing Checklist

- [ ] Camera permission request works
- [ ] Countdown timer displays correctly
- [ ] Photo capture saves properly
- [ ] Preview shows captured image
- [ ] Retake functionality works
- [ ] Continue button enables after capture
- [ ] Session ID persists through steps
- [ ] PDF includes face photo
- [ ] Error handling for denied permissions
- [ ] Skip option works correctly
- [ ] Mobile responsive design
- [ ] All progress indicators show 4 steps

## Future Enhancements

Potential improvements:
- [ ] Upload photo option (for users without webcam)
- [ ] Multiple photo angles
- [ ] Face detection/centering
- [ ] Photo filters/adjustments
- [ ] Print-friendly photo in PDF
- [ ] Photo quality indicator

## Migration Notes

If you have an existing database, run migration to add `face_photo` field:
```python
# In Flask shell or migration script
from app import app, db

with app.app_context():
    db.drop_all()  # WARNING: Only for development
    db.create_all()
```

For production, use proper migrations (Flask-Migrate/Alembic).

## Dependencies

No new dependencies required! Uses:
- Native browser WebRTC APIs
- Existing PIL/Pillow for image processing
- Existing ReportLab for PDF generation

## Summary

The face capture feature seamlessly integrates into the existing workflow, providing a complete client identification system. The feature is optional (can be skipped), secure, and enhances the professional quality of the generated reports.
