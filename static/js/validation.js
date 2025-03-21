// Construction ERP Form Validation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize validation for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
        
        // Add input event listeners for real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(this);
            });
            
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });
    });
    
    // Add success alert handling
    setupSuccessAlerts();
});

/**
 * Validate an entire form before submission
 * @param {Event} event - The form submission event
 */
function validateForm(event) {
    const form = event.target;
    let isValid = true;
    
    // Validate all inputs in the form
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    // Special validation for specific forms
    if (form.id === 'worklogForm' || form.getAttribute('action') === '/worklogs') {
        isValid = validateWorklogForm(form) && isValid;
    } else if (form.id === 'paymentForm' || form.querySelector('[name="payment_method"]')) {
        isValid = validatePaymentForm(form) && isValid;
    } else if (form.id === 'invoiceForm' || form.getAttribute('action') === '/invoices') {
        isValid = validateInvoiceForm(form) && isValid;
    }
    
    // Prevent submission if validation fails
    if (!isValid) {
        event.preventDefault();
        
        // Show alert at the top of the form
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show';
        errorAlert.innerHTML = `
            <strong>Error!</strong> Please correct the highlighted fields before submitting.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the form
        form.prepend(errorAlert);
        
        // Scroll to the first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } else if (form.getAttribute('data-confirm') === 'true') {
        // If form requires confirmation, show dialog
        event.preventDefault();
        showConfirmationDialog(form);
    }
}

/**
 * Validate a specific input field
 * @param {HTMLElement} input - The input element to validate
 * @returns {boolean} - Whether the input is valid
 */
function validateInput(input) {
    // Skip disabled or hidden inputs
    if (input.disabled || input.type === 'hidden') {
        return true;
    }
    
    let isValid = true;
    const value = input.value.trim();
    const errorElement = getOrCreateErrorElement(input);
    
    // Required field validation
    if (input.required && value === '') {
        isValid = false;
        setInvalidState(input, errorElement, 'This field is required');
        return false;
    }
    
    // Field-specific validation based on name or type
    if (input.name === 'hourly_rate' || input.name === 'amount' || 
        input.name === 'value' || input.name.includes('amount')) {
        // Validate currency amounts
        if (value !== '' && (isNaN(parseFloat(value)) || parseFloat(value) < 0)) {
            isValid = false;
            setInvalidState(input, errorElement, 'Please enter a valid positive number');
        }
    } else if (input.type === 'date') {
        // Validate dates
        if (value !== '' && !isValidDate(value)) {
            isValid = false;
            setInvalidState(input, errorElement, 'Please enter a valid date');
        }
    } else if (input.type === 'time') {
        // Validate times
        if (value !== '' && !isValidTime(value)) {
            isValid = false;
            setInvalidState(input, errorElement, 'Please enter a valid time');
        }
    } else if (input.name === 'lunch_duration') {
        // Validate lunch duration
        if (value !== '' && (isNaN(parseInt(value)) || parseInt(value) < 0)) {
            isValid = false;
            setInvalidState(input, errorElement, 'Please enter a valid duration in minutes');
        }
    } else if (input.name === 'check_number' && input.closest('.check-details').style.display !== 'none') {
        // Validate check number when check payment is selected
        if (value === '') {
            isValid = false;
            setInvalidState(input, errorElement, 'Check number is required for check payments');
        }
    }
    
    // If valid, reset any error state
    if (isValid) {
        setValidState(input, errorElement);
    }
    
    return isValid;
}

/**
 * Create or get the error message element for an input
 * @param {HTMLElement} input - The input element
 * @returns {HTMLElement} - The error element
 */
function getOrCreateErrorElement(input) {
    let errorElement = input.nextElementSibling;
    
    // Check if the next element is our error element
    if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
        // Create a new error element
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        
        // Insert it after the input
        input.parentNode.insertBefore(errorElement, input.nextSibling);
    }
    
    return errorElement;
}

/**
 * Set an input to invalid state with an error message
 * @param {HTMLElement} input - The input element
 * @param {HTMLElement} errorElement - The error message element
 * @param {string} message - The error message
 */
function setInvalidState(input, errorElement, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    errorElement.textContent = message;
}

/**
 * Set an input to valid state
 * @param {HTMLElement} input - The input element
 * @param {HTMLElement} errorElement - The error message element
 */
function setValidState(input, errorElement) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    errorElement.textContent = '';
}

/**
 * Check if a string is a valid date
 * @param {string} dateString - The date string to validate
 * @returns {boolean} - Whether the date is valid
 */
function isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

/**
 * Check if a string is a valid time
 * @param {string} timeString - The time string to validate
 * @returns {boolean} - Whether the time is valid
 */
function isValidTime(timeString) {
    const regex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return regex.test(timeString);
}

/**
 * Validate a worklog form (entry time before exit time)
 * @param {HTMLElement} form - The form element
 * @returns {boolean} - Whether the form is valid
 */
function validateWorklogForm(form) {
    const entryTime = form.querySelector('[name="entry_time"]');
    const exitTime = form.querySelector('[name="exit_time"]');
    
    if (entryTime && exitTime && entryTime.value && exitTime.value) {
        // Check that entry time is before exit time
        if (entryTime.value >= exitTime.value) {
            const errorElement = getOrCreateErrorElement(exitTime);
            setInvalidState(exitTime, errorElement, 'Exit time must be after entry time');
            return false;
        }
    }
    
    return true;
}

/**
 * Validate a payment form (check payment requires check number)
 * @param {HTMLElement} form - The form element
 * @returns {boolean} - Whether the form is valid
 */
function validatePaymentForm(form) {
    const paymentMethod = form.querySelector('[name="payment_method"]');
    
    if (paymentMethod && paymentMethod.value === 'check') {
        const checkNumber = form.querySelector('[name="check_number"]');
        if (checkNumber && checkNumber.value.trim() === '') {
            const errorElement = getOrCreateErrorElement(checkNumber);
            setInvalidState(checkNumber, errorElement, 'Check number is required for check payments');
            return false;
        }
    }
    
    return true;
}

/**
 * Validate an invoice form
 * @param {HTMLElement} form - The form element
 * @returns {boolean} - Whether the form is valid
 */
function validateInvoiceForm(form) {
    const amountCharged = form.querySelector('[name="amount_charged"]');
    
    if (amountCharged && parseFloat(amountCharged.value) <= 0) {
        const errorElement = getOrCreateErrorElement(amountCharged);
        setInvalidState(amountCharged, errorElement, 'Invoice amount must be greater than zero');
        return false;
    }
    
    return true;
}

/**
 * Show a confirmation dialog for important actions
 * @param {HTMLElement} form - The form to submit after confirmation
 */
function showConfirmationDialog(form) {
    // Get confirmation message from data attribute
    const message = form.getAttribute('data-confirm-message') || 'Are you sure you want to proceed?';
    const title = form.getAttribute('data-confirm-title') || 'Confirm Action';
    
    // Create modal if it doesn't exist
    let confirmModal = document.getElementById('confirmActionModal');
    if (!confirmModal) {
        confirmModal = document.createElement('div');
        confirmModal.className = 'modal fade';
        confirmModal.id = 'confirmActionModal';
        confirmModal.setAttribute('tabindex', '-1');
        confirmModal.setAttribute('aria-labelledby', 'confirmActionModalLabel');
        confirmModal.setAttribute('aria-hidden', 'true');
        
        confirmModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmActionModalLabel">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmActionBtn">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmModal);
    } else {
        // Update modal content
        confirmModal.querySelector('.modal-title').textContent = title;
        confirmModal.querySelector('.modal-body').textContent = message;
    }
    
    // Set up the confirm button to submit the form
    const confirmBtn = document.getElementById('confirmActionBtn');
    confirmBtn.onclick = function() {
        // Hide modal
        const modalInstance = bootstrap.Modal.getInstance(confirmModal);
        modalInstance.hide();
        
        // Submit the form
        form.removeAttribute('data-confirm');
        form.submit();
    };
    
    // Show the modal
    const modalInstance = new bootstrap.Modal(confirmModal);
    modalInstance.show();
}

/**
 * Set up success alert handling
 */
function setupSuccessAlerts() {
    // Check URL parameters for success messages
    const urlParams = new URLSearchParams(window.location.search);
    const successMessage = urlParams.get('success');
    
    if (successMessage) {
        // Create success alert
        const successAlert = document.createElement('div');
        successAlert.className = 'alert alert-success alert-dismissible fade show mb-4';
        successAlert.innerHTML = `
            <strong>Success!</strong> ${decodeURIComponent(successMessage)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the content
        const content = document.querySelector('.container');
        content.prepend(successAlert);
        
        // Automatically dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(successAlert);
            bsAlert.close();
        }, 5000);
        
        // Remove success parameter from URL
        urlParams.delete('success');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState({}, '', newUrl);
    }
}
