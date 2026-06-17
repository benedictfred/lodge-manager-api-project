function switchTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    
    document.querySelector(`.auth-tab[onclick="switchTab('${tab}')"]`).classList.add('active');
    document.getElementById(`${tab}-form`).classList.add('active');
    document.getElementById('error-msg').style.display = 'none';
}

function showError(msg) {
    const errorEl = document.getElementById('error-msg');
    errorEl.textContent = msg;
    errorEl.style.display = 'block';
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const data = await apiFetch('/auth/login', {
            method: 'POST',
            body: formData
        });
        
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
        }
        
        // After login, fetch profile to see if it's a Landlord or Tenant
        // For our mock, we assume Landlord logging in goes to lodges
        // A tenant logging in would go to their tenant dashboard
        window.location.href = 'lodges.html';
    } catch (err) {
        showError(err.message);
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fullName = document.getElementById('reg-name').value.trim();
    const parts = fullName.split(' ');
    const firstName = parts[0];
    const lastName = parts.slice(1).join(' ') || 'N/A';
    
    const payload = {
        first_name: firstName,
        last_name: lastName,
        email: document.getElementById('reg-email').value,
        phone_no: document.getElementById('reg-phone').value,
        password: document.getElementById('reg-password').value
    };

    try {
        await apiFetch('/auth/register/landlord', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        showToast('Registration successful! Please log in.');
        switchTab('login');
        document.getElementById('login-email').value = payload.email;
    } catch (err) {
        showError(err.message);
    }
});
