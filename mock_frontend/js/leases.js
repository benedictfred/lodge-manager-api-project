document.addEventListener('DOMContentLoaded', async () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName;
    await fetchLeases();
    
    // Auto-open modal if room_id is in query string
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('room_id');
    if (roomId) {
        await openLeaseModal();
        // Give the DOM a tiny tick to render the options
        setTimeout(() => {
            document.getElementById('lease-room').value = roomId;
        }, 50);
    }
});

let roomsLoaded = false;
let tenantsLoaded = false;

async function fetchLeases() {
    const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
    const tbody = document.getElementById('leases-tbody');
    try {
        // Fetch leases, rooms, and tenants in parallel to resolve IDs
        const [leases, rooms, tenants] = await Promise.all([
            apiFetch(`/leases/${activeLodgeId}`),
            apiFetch('/rooms/?skip=0&limit=100').catch(() => []),
            apiFetch(`/lodges/${activeLodgeId}/tenants`).catch(() => [])
        ]);
        
        // Build maps for quick lookup
        const roomMap = {};
        rooms.forEach(r => roomMap[r.id] = r.room_no);
        
        const tenantMap = {};
        tenants.forEach(t => {
            if (t.user) {
                tenantMap[t.id] = `${t.user.first_name} ${t.user.last_name}`;
            } else {
                tenantMap[t.id] = `Tenant ${t.id}`;
            }
        });
        
        tbody.innerHTML = '';
        if (leases.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color: var(--muted)">No leases found. Create one above.</td></tr>`;
            return;
        }

        leases.forEach(lease => {
            const tr = document.createElement('tr');
            
            const rentStr = new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' }).format(lease.agreed_rent_amt);
            
            let statusBadge = `<span class="room-badge badge-safe">Active</span>`;
            if (lease.status === 'Overdue') statusBadge = `<span class="room-badge badge-overdue">Overdue</span>`;
            if (lease.status === 'Terminated') statusBadge = `<span class="room-badge badge-maintenance">Terminated</span>`;
            if (lease.status === 'Pending_Termination') statusBadge = `<span class="room-badge badge-pending">Pending Term.</span>`;

            const roomDisplay = roomMap[lease.room_id] ? `Room ${roomMap[lease.room_id]}` : `Room ID: ${lease.room_id}`;
            // If the user_info is nested inside tenant, or we just have an email/name. 
            // In the tenant response, user info is in t.user.first_name, but our map lookup handles whatever we stored.
            // Wait, we need to fix tenantMap to look at t.user.first_name + t.user.last_name! Let's do that below.
            const tenantDisplay = tenantMap[lease.tenant_id] ? tenantMap[lease.tenant_id] : `Tenant ID: ${lease.tenant_id}`;

            tr.innerHTML = `
                <td style="font-weight: 600; color: var(--text)">${roomDisplay}</td>
                <td>${tenantDisplay}</td>
                <td>${new Date(lease.start_date).toLocaleDateString()}</td>
                <td>${new Date(lease.end_date).toLocaleDateString()}</td>
                <td style="font-weight: 500">${rentStr}</td>
                <td>${statusBadge}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        showError(err.message);
    }
}

async function populateDropdowns() {
    const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
    
    if (!roomsLoaded) {
        try {
            const rooms = await apiFetch(`/rooms/${activeLodgeId}/rooms?skip=0&limit=100`);
            const lodgeRooms = rooms.filter(r => r.lodge_id === activeLodgeId && r.status !== 'Occupied');
            const roomSelect = document.getElementById('lease-room');
            roomSelect.innerHTML = '<option value="">-- Select Available Room --</option>';
            lodgeRooms.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = `Room ${r.room_no} (${r.description || 'N/A'}) - ₦${r.base_rent_price}`;
                roomSelect.appendChild(opt);
            });
            roomsLoaded = true;
        } catch (err) {
            console.error(err);
        }
    }

    if (!tenantsLoaded) {
        try {
            const tenants = await apiFetch(`/lodges/${activeLodgeId}/tenants`);
            const tenantSelect = document.getElementById('lease-tenant');
            tenantSelect.innerHTML = '<option value="">-- Select Tenant --</option>';
            tenants.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                const nameStr = t.user ? `${t.user.first_name} ${t.user.last_name}` : `Tenant ${t.id}`;
                const emailStr = t.user ? t.user.email : 'No Email';
                opt.textContent = `${nameStr} (${emailStr})`;
                tenantSelect.appendChild(opt);
            });
            
            if (tenants.length === 0) {
                tenantSelect.innerHTML = '<option value="">No tenants found. Did they register via invite?</option>';
            }
            tenantsLoaded = true;
        } catch (err) {
            console.error(err);
        }
    }
}

async function openLeaseModal() {
    document.getElementById('lease-modal').classList.add('active');
    await populateDropdowns();
}

function closeLeaseModal() {
    document.getElementById('lease-modal').classList.remove('active');
}

document.getElementById('create-lease-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        room_id: parseInt(document.getElementById('lease-room').value, 10),
        tenant_id: parseInt(document.getElementById('lease-tenant').value, 10),
        start_date: document.getElementById('lease-start').value,
        end_date: document.getElementById('lease-end').value,
        agreed_rent_amt: parseFloat(document.getElementById('lease-rent').value),
        status: "Active",
        total_amt_paid: 0
    };

    try {
        await apiFetch('/leases/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        closeLeaseModal();
        showToast('Lease created successfully!');
        e.target.reset();
        fetchLeases();
    } catch (err) {
        alert('Failed to create lease: ' + err.message);
    }
});
