/**
 * Main JavaScript for Astrology Fingerprint Collection App
 * Handles form interactions, file uploads, validation, and UI enhancements
 */

// Global app configuration
const App = {
    config: {
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedTypes: ['image/jpeg', 'image/jpg', 'image/png'],
        fingerprintPositions: ['L1', 'L2', 'L3', 'L4', 'L5', 'R1', 'R2', 'R3', 'R4', 'R5'],
        fingerNames: {
            'L1': 'Left Thumb', 'L2': 'Left Index', 'L3': 'Left Middle', 
            'L4': 'Left Ring', 'L5': 'Left Pinky',
            'R1': 'Right Thumb', 'R2': 'Right Index', 'R3': 'Right Middle', 
            'R4': 'Right Ring', 'R5': 'Right Pinky'
        }
    },

    // Initialize the application
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.handlePageSpecificLogic();
    },

    // Set up global event listeners
    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.enhanceFormValidation();
            this.setupTooltips();
            this.setupAlertDismissals();
            this.setupSmoothScrolling();
        });

        // Handle window resize for responsive adjustments
        window.addEventListener('resize', this.debounce(() => {
            this.handleResponsiveAdjustments();
        }, 250));

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAnimations();
            } else {
                this.resumeAnimations();
            }
        });
    },

    // Initialize components based on current page
    initializeComponents() {
        const currentPage = this.getCurrentPage();
        
        switch(currentPage) {
            case 'index':
                this.initHomePage();
                break;
            case 'step1':
                this.initStep1();
                break;
            case 'step2':
                this.initStep2();
                break;
            case 'success':
                this.initSuccessPage();
                break;
        }
    },

    // Determine current page based on URL or body class
    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path.includes('index')) return 'index';
        if (path.includes('step1')) return 'step1';
        if (path.includes('step2')) return 'step2';
        if (path.includes('success')) return 'success';
        return 'unknown';
    },

    // Page-specific initialization
    initHomePage() {
        this.animateZodiacSymbols();
        this.setupFeatureAnimations();
        this.initModalInteractions();
    },

    initStep1() {
        this.setupFormValidation();
        this.setupDateOfBirthEnhancements();
        this.setupMobileNumberValidation();
        this.setupFormAutoSave();
    },

    initStep2() {
        this.setupFileUploadHandlers();
        this.setupProgressTracking();
        this.setupHandVisualUpdates();
        this.setupDragDropUpload();
    },

    initSuccessPage() {
        this.setupDownloadTracking();
        this.setupSessionIdCopy();
        this.animateSuccessElements();
    },

    // Enhanced form validation
    enhanceFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                // Real-time validation
                input.addEventListener('input', (e) => {
                    this.validateField(e.target);
                });

                input.addEventListener('blur', (e) => {
                    this.validateField(e.target);
                });

                // Custom validation messages
                input.addEventListener('invalid', (e) => {
                    e.preventDefault();
                    this.showCustomValidationMessage(e.target);
                });
            });

            // Form submission validation
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.focusFirstInvalidField(form);
                }
            });
        });
    },

    // Validate individual field
    validateField(field) {
        const isValid = field.checkValidity();
        const feedback = field.parentElement.querySelector('.invalid-feedback');
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedback) feedback.style.display = 'none';
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (feedback) feedback.style.display = 'block';
        }

        return isValid;
    },

    // Show custom validation messages
    showCustomValidationMessage(field) {
        let message = '';
        
        if (field.validity.valueMissing) {
            message = `${this.getFieldLabel(field)} is required.`;
        } else if (field.validity.typeMismatch) {
            message = `Please enter a valid ${field.type}.`;
        } else if (field.validity.patternMismatch) {
            message = this.getPatternMessage(field);
        } else if (field.validity.tooShort) {
            message = `${this.getFieldLabel(field)} must be at least ${field.minLength} characters.`;
        } else if (field.validity.tooLong) {
            message = `${this.getFieldLabel(field)} must be no more than ${field.maxLength} characters.`;
        }

        if (message) {
            this.showFieldError(field, message);
        }
    },

    // Get field label for validation messages
    getFieldLabel(field) {
        const label = document.querySelector(`label[for="${field.id}"]`);
        return label ? label.textContent.replace('*', '').trim() : field.name;
    },

    // Get pattern-specific validation messages
    getPatternMessage(field) {
        if (field.name === 'mobile_number') {
            return 'Please enter a valid mobile number (10-15 digits).';
        }
        return 'Please enter a valid format.';
    },

    // Show field error
    showFieldError(field, message) {
        let feedback = field.parentElement.querySelector('.invalid-feedback');
        
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentElement.appendChild(feedback);
        }
        
        feedback.innerHTML = `<small>${message}</small>`;
        feedback.style.display = 'block';
        field.classList.add('is-invalid');
    },

    // File upload handlers for Step 2
    setupFileUploadHandlers() {
        const fileInputs = document.querySelectorAll('.file-input');
        
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileSelection(e.target);
            });
        });

        // Setup remove file buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-file') || e.target.closest('.remove-file')) {
                e.preventDefault();
                this.removeUploadedFile(e.target);
            }
        });
    },

    // Handle file selection
    handleFileSelection(input) {
        const file = input.files[0];
        const uploadItem = input.closest('.upload-item');
        const fingerPosition = uploadItem.dataset.finger;

        if (!file) {
            this.clearFilePreview(uploadItem, fingerPosition);
            return;
        }

        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showFileError(uploadItem, validation.message);
            input.value = '';
            return;
        }

        // Show preview
        this.showFilePreview(file, uploadItem, fingerPosition);
        this.updateFingerVisual(fingerPosition, true);
        this.updateUploadProgress();
    },

    // Validate uploaded file
    validateFile(file) {
        if (!this.config.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: 'Please upload only JPG or PNG images.'
            };
        }

        if (file.size > this.config.maxFileSize) {
            return {
                valid: false,
                message: 'File size must be less than 16MB.'
            };
        }

        return { valid: true };
    },

    // Show file preview
    showFilePreview(file, uploadItem, fingerPosition) {
        const preview = uploadItem.querySelector('.upload-preview');
        const previewImg = uploadItem.querySelector('.preview-image');
        
        if (preview && previewImg) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                preview.style.display = 'block';
                uploadItem.classList.add('has-file');
                
                // Animate preview appearance
                preview.style.opacity = '0';
                preview.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    preview.style.transition = 'all 0.3s ease';
                    preview.style.opacity = '1';
                    preview.style.transform = 'scale(1)';
                }, 10);
            };
            reader.readAsDataURL(file);
        }
    },

    // Clear file preview
    clearFilePreview(uploadItem, fingerPosition) {
        const preview = uploadItem.querySelector('.upload-preview');
        if (preview) {
            preview.style.display = 'none';
            uploadItem.classList.remove('has-file');
        }
        this.updateFingerVisual(fingerPosition, false);
        this.updateUploadProgress();
    },

    // Remove uploaded file
    removeUploadedFile(button) {
        const uploadItem = button.closest('.upload-item');
        const fileInput = uploadItem.querySelector('.file-input');
        const fingerPosition = uploadItem.dataset.finger;
        
        fileInput.value = '';
        this.clearFilePreview(uploadItem, fingerPosition);
        
        // Animate removal
        const preview = uploadItem.querySelector('.upload-preview');
        if (preview) {
            preview.style.transition = 'all 0.3s ease';
            preview.style.opacity = '0';
            preview.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                preview.style.display = 'none';
                preview.style.opacity = '1';
                preview.style.transform = 'scale(1)';
            }, 300);
        }
    },

    // Update finger visual indicator
    updateFingerVisual(fingerPosition, hasFile) {
        const fingerCircle = document.querySelector(`[data-finger="${fingerPosition}"]`);
        if (fingerCircle) {
            if (hasFile) {
                fingerCircle.setAttribute('fill', '#28a745');
                fingerCircle.setAttribute('stroke', '#1e7e34');
                fingerCircle.style.filter = 'drop-shadow(0 2px 4px rgba(40, 167, 69, 0.3))';
            } else {
                fingerCircle.setAttribute('fill', '#e9ecef');
                fingerCircle.setAttribute('stroke', '#6c757d');
                fingerCircle.style.filter = 'none';
            }
        }
    },

    // Update upload progress
    updateUploadProgress() {
        const fileInputs = document.querySelectorAll('.file-input');
        const uploadedCount = Array.from(fileInputs).filter(input => input.files.length > 0).length;
        const uploadedCountEl = document.getElementById('uploadedCount');
        const submitBtn = document.getElementById('submitBtn');
        
        if (uploadedCountEl) {
            uploadedCountEl.textContent = uploadedCount;
            
            // Animate count change
            uploadedCountEl.style.transform = 'scale(1.2)';
            setTimeout(() => {
                uploadedCountEl.style.transform = 'scale(1)';
            }, 200);
        }

        if (submitBtn) {
            if (uploadedCount > 0) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Submit Application';
                submitBtn.classList.remove('btn-outline-secondary');
                submitBtn.classList.add('btn-success');
            } else {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Upload at least 1 fingerprint';
                submitBtn.classList.remove('btn-success');
                submitBtn.classList.add('btn-outline-secondary');
            }
        }
    },

    // Setup drag and drop upload
    setupDragDropUpload() {
        const uploadItems = document.querySelectorAll('.upload-item');
        
        uploadItems.forEach(item => {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                item.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                item.addEventListener(eventName, () => this.highlight(item), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                item.addEventListener(eventName, () => this.unhighlight(item), false);
            });

            item.addEventListener('drop', (e) => this.handleDrop(e, item), false);
        });
    },

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    },

    highlight(item) {
        item.classList.add('drag-over');
    },

    unhighlight(item) {
        item.classList.remove('drag-over');
    },

    handleDrop(e, item) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = item.querySelector('.file-input');
        
        if (files.length > 0) {
            fileInput.files = files;
            this.handleFileSelection(fileInput);
        }
    },

    // Date of birth enhancements
    setupDateOfBirthEnhancements() {
        const dobInput = document.querySelector('#date_of_birth');
        if (!dobInput) return;

        dobInput.addEventListener('change', (e) => {
            const date = new Date(e.target.value);
            if (date && !isNaN(date.getTime())) {
                const age = this.calculateAge(date);
                const zodiacSign = this.getZodiacSign(date);
                
                this.updateDateOfBirthInfo(age, zodiacSign);
            }
        });
    },

    // Calculate age from date
    calculateAge(birthDate) {
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age;
    },

    // Get zodiac sign from date
    getZodiacSign(date) {
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        if ((month == 3 && day >= 21) || (month == 4 && day <= 19)) return "Aries ♈";
        if ((month == 4 && day >= 20) || (month == 5 && day <= 20)) return "Taurus ♉";
        if ((month == 5 && day >= 21) || (month == 6 && day <= 20)) return "Gemini ♊";
        if ((month == 6 && day >= 21) || (month == 7 && day <= 22)) return "Cancer ♋";
        if ((month == 7 && day >= 23) || (month == 8 && day <= 22)) return "Leo ♌";
        if ((month == 8 && day >= 23) || (month == 9 && day <= 22)) return "Virgo ♍";
        if ((month == 9 && day >= 23) || (month == 10 && day <= 22)) return "Libra ♎";
        if ((month == 10 && day >= 23) || (month == 11 && day <= 21)) return "Scorpio ♏";
        if ((month == 11 && day >= 22) || (month == 12 && day <= 21)) return "Sagittarius ♐";
        if ((month == 12 && day >= 22) || (month == 1 && day <= 19)) return "Capricorn ♑";
        if ((month == 1 && day >= 20) || (month == 2 && day <= 18)) return "Aquarius ♒";
        return "Pisces ♓";
    },

    // Update date of birth information display
    updateDateOfBirthInfo(age, zodiacSign) {
        const dobInput = document.querySelector('#date_of_birth');
        if (dobInput) {
            const helpText = dobInput.parentElement.querySelector('.form-text');
            if (helpText) {
                helpText.innerHTML = `
                    <i class="fas fa-info-circle me-1"></i>
                    Age: ${age} years, Zodiac: ${zodiacSign}
                `;
                
                // Animate the update
                helpText.style.color = '#28a745';
                setTimeout(() => {
                    helpText.style.color = '';
                }, 1000);
            }
        }
    },

    // Mobile number validation
    setupMobileNumberValidation() {
        const mobileInput = document.querySelector('#mobile_number');
        if (!mobileInput) return;

        mobileInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, ''); // Remove non-digits
            
            // Format phone number (optional)
            if (value.length >= 10) {
                // Format as (XXX) XXX-XXXX for US numbers or similar
                value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            }
            
            // Update input if formatting applied
            if (value !== e.target.value && value.length <= 14) {
                e.target.value = value;
            }
        });
    },

    // Form auto-save functionality
    setupFormAutoSave() {
        const form = document.querySelector('form');
        if (!form) return;

        const inputs = form.querySelectorAll('input, select, textarea');
        const saveKey = 'astrology_form_data';
        
        // Load saved data
        this.loadFormData(inputs, saveKey);
        
        // Auto-save on input
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.saveFormData(inputs, saveKey);
            });
        });
        
        // Clear saved data on successful submission
        form.addEventListener('submit', () => {
            localStorage.removeItem(saveKey);
        });
    },

    // Save form data to localStorage
    saveFormData(inputs, key) {
        const data = {};
        
        inputs.forEach(input => {
            if (input.type === 'file') return; // Skip file inputs
            data[input.name || input.id] = input.value;
        });
        
        localStorage.setItem(key, JSON.stringify(data));
    },

    // Load form data from localStorage
    loadFormData(inputs, key) {
        const savedData = localStorage.getItem(key);
        if (!savedData) return;
        
        try {
            const data = JSON.parse(savedData);
            
            inputs.forEach(input => {
                const fieldName = input.name || input.id;
                if (data[fieldName] && input.type !== 'file') {
                    input.value = data[fieldName];
                }
            });
        } catch (e) {
            console.warn('Error loading saved form data:', e);
        }
    },

    // Setup tooltips
    setupTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    // Setup alert dismissals
    setupAlertDismissals() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(alert => {
            // Auto-dismiss success messages
            if (alert.classList.contains('alert-success')) {
                setTimeout(() => {
                    this.fadeOutAlert(alert);
                }, 5000);
            }
        });
    },

    // Fade out alert
    fadeOutAlert(alert) {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        
        setTimeout(() => {
            alert.remove();
        }, 500);
    },

    // Setup smooth scrolling
    setupSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },

    // Animate zodiac symbols on home page
    animateZodiacSymbols() {
        const zodiacSymbols = document.querySelectorAll('.zodiac-symbol');
        
        zodiacSymbols.forEach((symbol, index) => {
            symbol.style.animationDelay = `${index * 0.1}s`;
        });
    },

    // Setup feature animations
    setupFeatureAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });

        const animatedElements = document.querySelectorAll('.step-card, .feature-item, .stat-card');
        animatedElements.forEach(el => observer.observe(el));
    },

    // Modal interactions
    initModalInteractions() {
        const modal = document.getElementById('infoModal');
        if (!modal) return;

        modal.addEventListener('shown.bs.modal', () => {
            // Focus first interactive element
            const firstInput = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstInput) firstInput.focus();
        });
    },

    // Success page animations
    animateSuccessElements() {
        const elements = document.querySelectorAll('.client-summary, .submission-summary, .pdf-download');
        
        elements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('slide-up');
            }, index * 200);
        });
    },

    // Setup download tracking
    setupDownloadTracking() {
        const downloadLinks = document.querySelectorAll('a[href*="download_pdf"]');
        
        downloadLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.trackDownload();
            });
        });
    },

    // Track download event
    trackDownload() {
        console.log('PDF download initiated at:', new Date().toISOString());
        
        // Show download feedback
        const downloadBtn = document.querySelector('a[href*="download_pdf"]');
        if (downloadBtn) {
            const originalText = downloadBtn.innerHTML;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Preparing Download...';
            downloadBtn.classList.add('disabled');
            
            setTimeout(() => {
                downloadBtn.innerHTML = originalText;
                downloadBtn.classList.remove('disabled');
            }, 2000);
        }
    },

    // Setup session ID copy functionality
    setupSessionIdCopy() {
        const copyButtons = document.querySelectorAll('button[onclick*="copyToClipboard"]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const sessionId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.copyToClipboard(sessionId, button);
            });
        });
    },

    // Copy text to clipboard
    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            
            // Visual feedback
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check text-success"></i>';
            
            // Show success message
            this.showCopySuccess();
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
            }, 2000);
            
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showCopyError();
        }
    },

    // Show copy success message
    showCopySuccess() {
        this.showToast('Session ID copied to clipboard!', 'success');
    },

    // Show copy error message
    showCopyError() {
        this.showToast('Failed to copy to clipboard', 'error');
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info'} me-2"></i>
                ${message}
            </div>
        `;
        
        // Styles for toast
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });
        
        // Animate out and remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    },

    // Handle responsive adjustments
    handleResponsiveAdjustments() {
        const isMobile = window.innerWidth < 768;
        
        // Adjust zodiac circle size on mobile
        const zodiacCircle = document.querySelector('.zodiac-circle');
        if (zodiacCircle) {
            if (isMobile) {
                zodiacCircle.style.width = '200px';
                zodiacCircle.style.height = '200px';
            } else {
                zodiacCircle.style.width = '300px';
                zodiacCircle.style.height = '300px';
            }
        }
    },

    // Pause animations when page is hidden
    pauseAnimations() {
        const animatedElements = document.querySelectorAll('.zodiac-circle, .zodiac-symbol');
        animatedElements.forEach(el => {
            el.style.animationPlayState = 'paused';
        });
    },

    // Resume animations when page is visible
    resumeAnimations() {
        const animatedElements = document.querySelectorAll('.zodiac-circle, .zodiac-symbol');
        animatedElements.forEach(el => {
            el.style.animationPlayState = 'running';
        });
    },

    // Handle page-specific logic
    handlePageSpecificLogic() {
        // Add any additional page-specific functionality here
        this.setupKeyboardNavigation();
        this.setupAccessibilityEnhancements();
    },

    // Setup keyboard navigation
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const modal = bootstrap.Modal.getInstance(openModal);
                    if (modal) modal.hide();
                }
            }
            
            // Enter key to submit forms (with confirmation)
            if (e.key === 'Enter' && e.ctrlKey) {
                const submitBtn = document.querySelector('input[type="submit"], button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                }
            }
        });
    },

    // Setup accessibility enhancements
    setupAccessibilityEnhancements() {
        // Add ARIA labels where needed
        const fileInputs = document.querySelectorAll('.file-input');
        fileInputs.forEach(input => {
            const fingerPosition = input.closest('.upload-item')?.dataset.finger;
            if (fingerPosition && this.config.fingerNames[fingerPosition]) {
                input.setAttribute('aria-label', `Upload fingerprint for ${this.config.fingerNames[fingerPosition]}`);
            }
        });

        // Add focus indicators
        const focusableElements = document.querySelectorAll('button, input, select, textarea, a[href]');
        focusableElements.forEach(el => {
            el.addEventListener('focus', () => {
                el.style.outline = '2px solid #3498db';
                el.style.outlineOffset = '2px';
            });
            
            el.addEventListener('blur', () => {
                el.style.outline = '';
                el.style.outlineOffset = '';
            });
        });
    },

    // Utility function: Debounce
    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    // Utility function: Throttle
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize the app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

// Global functions for backward compatibility
window.copyToClipboard = function(text) {
    App.copyToClipboard(text);
};

window.trackDownload = function() {
    App.trackDownload();
};

// Export App for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}
