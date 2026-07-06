document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const roleSelect = document.getElementById('role');
    const passwordField = document.getElementById('password');
    const confirmField = document.getElementById('confirm_password');
    
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous errors
            const existingErrors = document.querySelectorAll('.error-message');
            existingErrors.forEach(el => el.remove());
            
            // Validate password match
            if (passwordField.value !== confirmField.value) {
                showError('Passwords do not match');
                return;
            }
            
            // Validate password strength
            if (passwordField.value.length < 6) {
                showError('Password must be at least 6 characters long');
                return;
            }
            
            // Collect form data
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                if (value && value.trim()) {
                    data[key] = value.trim();
                }
            });
            
            // For doctor role, validate specialization
            if (data.role === 'doctor') {
                if (!data.specialization) {
                    showError('Specialization is required for doctors');
                    return;
                }
            }
            
            // Convert numeric fields
            if (data.age) data.age = parseInt(data.age);
            if (data.years_experience) data.years_experience = parseInt(data.years_experience);
            if (data.consultation_fee) data.consultation_fee = parseFloat(data.consultation_fee);
            
            // Disable submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';
            
            try {
                console.log('Sending registration data:', data); // Debug log
                
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                console.log('Registration response:', result); // Debug log
                
                if (result.success) {
                    alert('✅ Registration successful! Please login.');
                    window.location.href = '/login';
                } else {
                    showError(result.message || 'Registration failed');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
                }
            } catch (error) {
                console.error('Registration error:', error);
                showError('An error occurred. Please try again.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
            }
        });
    }
    
    // Toggle doctor fields
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const doctorFields = document.getElementById('doctor-fields');
            const specializationField = document.getElementById('specialization');
            
            if (this.value === 'doctor') {
                doctorFields.style.display = 'block';
                specializationField.required = true;
                specializationField.parentElement.querySelector('label').innerHTML = 
                    'Specialization <span style="color: #c0392b;">*</span>';
            } else {
                doctorFields.style.display = 'none';
                specializationField.required = false;
                specializationField.parentElement.querySelector('label').innerHTML = 
                    'Specialization';
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
    let indicator = document.querySelector('.password-strength');
    if (!indicator) {
        const passwordField = document.getElementById('password');
        indicator = document.createElement('div');
        indicator.className = 'password-strength';
        indicator.style.cssText = 'margin-top: 0.25rem; font-size: 0.9rem;';
        passwordField.parentNode.insertBefore(indicator, passwordField.nextSibling);
    }
    
    const strengths = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'];
    const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60'];
    
    if (strength === 0 || !document.getElementById('password').value) {
        indicator.textContent = '';
        return;
    }
    
    indicator.textContent = strengths[strength - 1];
    indicator.style.color = colors[strength - 1];
}

function showError(message) {
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash-message flash-error error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
        <span class="flash-close" onclick="this.parentElement.remove()">&times;</span>
    `;
    
    const form = document.querySelector('.register-form');
    form.insertBefore(errorDiv, form.firstChild);
}