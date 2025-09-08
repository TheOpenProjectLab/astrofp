# Overview

This is a Flask-based web application designed for astrologers to collect and manage client fingerprints and personal details for astrological analysis. The app provides a secure, two-step form submission process where clients first provide personal information and then upload high-resolution fingerprint images for all 10 fingers. After submission, the system generates a comprehensive PDF report containing all collected data and fingerprint images.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Core web framework with SQLAlchemy ORM for database operations
- **Flask-WTF**: Form handling and CSRF protection for security
- **Werkzeug ProxyFix**: Handles proxy headers for deployment behind reverse proxies

## Frontend Architecture
- **Bootstrap 5**: Responsive CSS framework for modern UI components
- **Font Awesome**: Icon library for enhanced visual elements
- **Custom CSS/JS**: Progressive enhancement with custom styling and JavaScript functionality
- **Multi-step Form Flow**: Guided user experience through personal details → fingerprint upload → completion

## Database Design
- **SQLAlchemy with SQLite**: Default database with PostgreSQL support via environment configuration
- **Two-table Schema**:
  - `Client`: Stores personal details, contact information, and session management
  - `Fingerprint`: Stores uploaded fingerprint metadata and file references
- **Session-based Data Management**: Temporary storage during multi-step form completion

## File Upload System
- **Secure File Handling**: Validates file types (PNG, JPG, JPEG), size limits (16MB), and image integrity
- **Session-organized Storage**: Files stored in session-specific directories under `/static/uploads/`
- **PIL Integration**: Image validation and processing capabilities
- **Unique Filename Generation**: Prevents conflicts using UUID and secure tokens

## Security Features
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **File Validation**: Strict file type and size validation
- **Session Management**: UUID-based session tracking for form state
- **Input Validation**: Comprehensive form validation with WTForms

## PDF Generation
- **ReportLab Integration**: Generates professional PDF reports with embedded fingerprint images
- **Comprehensive Reports**: Includes personal details, astrological calculations (age, zodiac sign), and all uploaded fingerprint images

## Configuration Management
- **Environment-based Config**: Database URLs, session secrets, and file paths configurable via environment variables
- **Development vs Production**: Separate configurations for different deployment environments

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

## File Processing
- **Pillow (PIL)**: Image validation, processing, and manipulation
- **Werkzeug**: File upload utilities and security helpers

## PDF Generation
- **ReportLab**: PDF document creation with embedded images and structured layouts

## Frontend Libraries (CDN)
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI enhancements

## Database Support
- **SQLite**: Default development database (included with Python)
- **PostgreSQL**: Production database support via psycopg2 (configurable)

## Development Tools
- **Flask Debug Mode**: Development server with auto-reload
- **Python Logging**: Application logging and debugging support