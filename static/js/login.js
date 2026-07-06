document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            
            if (!username.value.trim()) {
                e.preventDefault();
                showError('Please enter your username');
                username.focus();
                return;
            }
            
            if (!password.value.trim()) {
                e.preventDefault();
                showError('Please enter your password');
                password.focus();
                return;
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
    errorDiv.className = 'flash-message flash-error';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
        <span class="flash-close" onclick="this.parentElement.remove()">&times;</span>
    `;
    
    // Insert at top of form
    const form = document.querySelector('.login-form');
    form.insertBefore(errorDiv, form.firstChild);
}