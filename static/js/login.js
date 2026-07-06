document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!username) {
                showError('Please enter your username');
                return;
            }
            
            if (!password) {
                showError('Please enter your password');
                return;
            }
            
            // Disable submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Redirect based on role
                    if (data.role === 'admin') {
                        window.location.href = '/admin/dashboard';
                    } else if (data.role === 'doctor') {
                        window.location.href = '/doctor/dashboard';
                    } else {
                        window.location.href = '/patient/dashboard';
                    }
                } else {
                    showError(data.message || 'Invalid username or password');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
                }
            } catch (error) {
                showError('An error occurred. Please try again.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
                console.error('Login error:', error);
            }
        });
    }
});

function showError(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash-message flash-error error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
        <span class="flash-close" onclick="this.parentElement.remove()">&times;</span>
    `;
    
    // Insert at top of form
    const form = document.querySelector('.login-form');
    form.insertBefore(errorDiv, form.firstChild);
}