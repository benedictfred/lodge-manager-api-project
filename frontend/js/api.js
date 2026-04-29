/**
 * api.js - The Master API Wrapper
 * This handles all communication with the FastAPI backend.
 * It enforces the DRY (Don't Repeat Yourself) principle for fetching data.
 */

const BASE_URL = 'http://127.0.0.1:8000/api/v1';

async function apiFetch(endpoint, options = {}) {
    // 1. Check the Wallet: Grab the JWT token if the user is logged in
    const token = localStorage.getItem('access_token');
    
    // 2. Prepare the Envelope (Headers)
    const headers = new Headers(options.headers || {});
    
    // If we have a VIP pass, slap it on the envelope
    if (token) {
        headers.append('Authorization', `Bearer ${token}`);
    }
    
    // 3. Assemble the final request package
    const config = {
        ...options,
        headers: headers
    };

    try {
        // 4. Send the Waiter to the Kitchen (FastAPI)
        const response = await fetch(`${BASE_URL}${endpoint}`, config);

        // 5. The Bouncer Check: Did the backend kick us out?
        if (response.status === 401) {
            console.warn("Session expired or unauthorized. Redirecting to login...");
            localStorage.removeItem('access_token'); // Shred the fake/expired pass
            window.location.href = 'index.html';     // Kick to the curb
            return null;
        }

        // 6. Handle other errors (like 400 Bad Request or 404 Not Found)
        if (!response.ok) {
            // Try to extract the detailed FastAPI error message
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        // 7. Success! Return the JSON plate to the caller
        return await response.json();
        
    } catch (error) {
        console.error("API Fetch Error:", error);
        throw error; // Re-throw so the UI can show a red error box
    }
}
