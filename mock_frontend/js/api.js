const hostname = window.location.hostname || 'localhost';
const API_BASE = `http://${hostname}:8000/api/v1`;

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
    refreshSubscribers.push(cb);
}

function onRefreshed(isSuccess) {
    refreshSubscribers.map(cb => cb(isSuccess));
    refreshSubscribers = [];
}

async function processResponse(response) {
    if (response.status === 401) {
        localStorage.clear();
        window.location.href = 'login.html';
        throw new Error('Session expired. Please log in again.');
    }

    const contentType = response.headers.get("content-type");
    let data = null;
    if (contentType && contentType.indexOf("application/json") !== -1) {
        data = await response.json();
    }

    if (!response.ok) {
        let errorMsg = 'An error occurred';
        if (data) {
            if (data.detail && typeof data.detail === 'string') {
                errorMsg = data.detail;
            } else if (data.detail && Array.isArray(data.detail)) {
                errorMsg = data.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join(', ');
            }
        }
        throw new Error(errorMsg);
    }

    return data;
}

async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    try {
        let response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
            credentials: 'include'
        });

        if (response.status === 401 && endpoint !== '/auth/login' && endpoint !== '/auth/refresh') {
            if (!isRefreshing) {
                isRefreshing = true;
                try {
                    const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include'
                    });
                    
                    if (refreshRes.ok) {
                        isRefreshing = false;
                        onRefreshed(true);
                        // Retry original request
                        response = await fetch(`${API_BASE}${endpoint}`, {
                            ...options,
                            headers,
                            credentials: 'include'
                        });
                    } else {
                        isRefreshing = false;
                        onRefreshed(false);
                        localStorage.clear();
                        window.location.href = 'login.html';
                        throw new Error('Session expired. Please log in again.');
                    }
                } catch (e) {
                    isRefreshing = false;
                    onRefreshed(false);
                    localStorage.clear();
                    window.location.href = 'login.html';
                    throw new Error('Session expired. Please log in again.');
                }
            } else {
                return new Promise((resolve, reject) => {
                    subscribeTokenRefresh(async (isSuccess) => {
                        if (isSuccess) {
                            try {
                                const retryRes = await fetch(`${API_BASE}${endpoint}`, {
                                    ...options,
                                    headers,
                                    credentials: 'include'
                                });
                                resolve(await processResponse(retryRes));
                            } catch (e) {
                                reject(e);
                            }
                        } else {
                            reject(new Error('Session expired. Please log in again.'));
                        }
                    });
                });
            }
        }
        
        return await processResponse(response);
    } catch (err) {
        console.error('API Error:', err);
        throw err;
    }
}

// Global Premium UI Helpers
function showToast(message, type = 'error') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function logout() {
    // We should call POST /auth/logout to invalidate refresh token in the backend
    apiFetch('/auth/logout', { method: 'POST' }).finally(() => {
        localStorage.clear();
        window.location.href = 'login.html';
    });
}

const currencyFormatter = new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' });
