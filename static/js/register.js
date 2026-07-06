document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('.register-form');
    const roleSelect = document.getElementById('role');
    const passwordField = document.getElementById('password');
    const confirmField = document.getElementById('confirm_password');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            // Validate password match
            if (passwordField.value !== confirmField.value) {
                e.preventDefault();
                showError('Passwords do not match');
                return;
            }
            
            // Validate password strength
            if (passwordField.value.length < 6) {
                e.preventDefault();
                showError('Password must be at least 6 characters long');
                return;
            }
        });
    }
    
    // Toggle doctor fields
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const doctorFields = document.getElementById('doctor-fields');
            if (this.value === 'doctor') {
                doctorFields.style.display = 'block';
            } else {
                doctorFields.style.display = 'none';
            }
        });
    }
    
    // Password strength indicator
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const strength = getPasswordStrength(this.value);
            updateStrengthIndicator(strength);
        });
    }
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 10) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
}

function updateStrengthIndicator(strength) {
    const indicator = document.querySelector('.password-strength');
    if (!indicator) return;
    
    const strengths = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'];
    const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60'];
    
    indicator.textContent = strengths[strength - 1] || '';
    indicator.style.color = colors[strength - 1] || '#666';
}

function showError(message) {
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash-message flash-error';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
        <span class="flash-close" onclick="this.parentElement.remove()">&times;</span>
    `;
    
    const form = document.querySelector('.register-form');
    form.insertBefore(errorDiv, form.firstChild);
}