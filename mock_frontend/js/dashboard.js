document.addEventListener('DOMContentLoaded', () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName;
    
    // Set up filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.getAttribute('data-filter');
            // Fetch anew from backend so financials update based on filter
            fetchDashboard(lodgeId);
        });
    });

    // Set up search
    document.getElementById('search-input').addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase();
        renderRooms();
    });

    fetchDashboard(lodgeId);
});

let dashboardData = null;
let currentFilter = 'All';
let searchQuery = '';

const currencyFormatter = new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' });

async function fetchDashboard(lodgeId) {
    try {
        let url = `/dashboard-landlord/me/landlord/${lodgeId}`;
        const params = new URLSearchParams();
        
        if (currentFilter !== 'All') {
            if (['Vacant', 'Maintenance'].includes(currentFilter)) {
                params.append('room_statuses', currentFilter);
            } else {
                params.append('financial_filters', currentFilter);
            }
        }
        
        const qs = params.toString();
        if (qs) url += `?${qs}`;

        const data = await apiFetch(url);
        dashboardData = data;
        
        bindStaticFacts(data.entity_counts);
        bindFinancials(data.financials);
        renderRooms();
    } catch (err) {
        showError(err.message);
    }
}

function bindStaticFacts(counts) {
    if (!counts) return;

    document.getElementById('fact-rooms').textContent = counts.total_rooms || 0;
    document.getElementById('fact-tenants').textContent = counts.total_tenants || 0;
    
    // Bind Pending Move-outs if we have the data
    if (counts.occupied_counts) {
        document.getElementById('fact-turnover').textContent = counts.occupied_counts.pending || 0;
    }
    
    // Use the backend-calculated occupancy rate
    const occPct = counts.occupancy_rate || 0;
    
    document.getElementById('occ-val').textContent = `${occPct}%`;
    document.getElementById('occ-text').textContent = `${occPct}%`;
    
    // The ring is 283 dasharray. 0% offset = 283. 100% offset = 0.
    const offset = 283 - (283 * (occPct / 100));
    document.getElementById('occ-ring').style.strokeDashoffset = offset;
}

function bindFinancials(fin) {
    if (!fin) return;
    
    const map = {
        'fin-potential': fin.potential_revenue,
        'fin-forecasted': fin.forecasted_revenue,
        'fin-expected': fin.expected_revenue,
        'fin-collected': fin.collected_revenue,
        'fin-unpaid': fin.unpaid_rent
    };

    for (const [id, value] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) {
            const val = value || 0;
            el.textContent = currencyFormatter.format(val);
            if (val === 0) el.classList.add('zero');
            else el.classList.remove('zero');
        }
    }
}

function renderRooms() {
    if (!dashboardData) return;
    
    let rooms = [];
    if (dashboardData.occupied_rooms_lease) {
        rooms = rooms.concat(dashboardData.occupied_rooms_lease.safe || []);
        rooms = rooms.concat(dashboardData.occupied_rooms_lease.expiring || []);
        rooms = rooms.concat(dashboardData.occupied_rooms_lease.overdue || []);
        rooms = rooms.concat(dashboardData.occupied_rooms_lease.pending || []);
        rooms = rooms.concat(dashboardData.occupied_rooms_lease.owing || []);
    }
    rooms = rooms.concat(dashboardData.vacant_rooms || []);
    rooms = rooms.concat(dashboardData.maintenance_rooms || []);

    // Search Logic (Client-side text filtering remains)
    if (searchQuery) {
        rooms = rooms.filter(r => 
            (r.main_display_text && r.main_display_text.toLowerCase().includes(searchQuery)) ||
            (r.sub_display_text && r.sub_display_text.toLowerCase().includes(searchQuery))
        );
    }
    
    // Sort rooms in ascending alphanumeric order by room number
    rooms.sort((a, b) => {
        const noA = a.room_no ? String(a.room_no) : "";
        const noB = b.room_no ? String(b.room_no) : "";
        return noA.localeCompare(noB, undefined, { numeric: true, sensitivity: 'base' });
    });

    document.getElementById('results-count').innerHTML = `Showing <span>${rooms.length}</span> rooms`;

    const grid = document.getElementById('dashboard-grid');
    grid.innerHTML = '';

    if (rooms.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--muted)">No rooms match the current filters.</div>`;
        return;
    }

    rooms.forEach(room => {
        // Map backend badge variant to colors
        const variantMap = {
            'Success': { bg: '#dcfce7', text: '#166534', bar: '#22c55e' },
            'Warning': { bg: '#fef08a', text: '#854d0e', bar: '#eab308' },
            'Danger':  { bg: '#fee2e2', text: '#991b1b', bar: '#ef4444' },
            'Orange':  { bg: '#ffedd5', text: '#9a3412', bar: '#f97316' },
            'Inactive':{ bg: '#f3f4f6', text: '#374151', bar: '#9ca3af' },
            'Info':    { bg: '#e0f2fe', text: '#075985', bar: '#0ea5e9' },
            'Purple':  { bg: '#f3e8ff', text: '#6b21a8', bar: '#a855f7' },
        };
        
        const colors = variantMap[room.badge_variant] || variantMap['Inactive'];

        // Determine a progress percentage from text (draining progress)
        let progressVal = 0;
        const textLower = (room.sub_display_text || '').toLowerCase();
        
        if (textLower.includes('days left') || textLower.includes('day left')) {
            const match = textLower.match(/(\d+)\s+day/);
            if (match) {
                const days = parseInt(match[1], 10);
                // 365 days = 100%, scaling down to 0% as days approach 0
                progressVal = Math.min(100, Math.max(0, (days / 365) * 100));
            }
        } else if (textLower.includes('overdue')) {
            progressVal = 0; // completely empty when overdue
        } else if (room.badge_text === 'Vacant' || room.badge_text === 'Maintenance') {
            progressVal = 0; // empty
        } else {
            progressVal = 100; // safe/default full
        }
        
        // Render for all rooms with badges
        const progressHtml = `
            <div style="width:100%; height:6px; background:#f3f4f6; border-radius:4px; margin-top:8px; overflow:hidden;">
                <div style="width:${progressVal}%; height:100%; background:${colors.bar}; border-radius:4px; transition:width 0.5s ease;"></div>
            </div>`;

        const card = document.createElement('div');
        card.className = `room-card`;
        card.style.borderTop = `4px solid ${colors.bar}`;
        card.style.display = 'flex';
        card.style.flexDirection = 'column';
        card.style.cursor = 'pointer';
        
        // Click action: open side panel
        card.onclick = () => {
            openRoomSidePanel(room, colors);
        };

        // Render card layout
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; color:var(--text);">
                    Room ${room.room_no}
                </div>
                <div style="background:${colors.bg}; color:${colors.text}; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:600;">
                    ${room.badge_text || 'Unknown'}
                </div>
            </div>
            
            <div style="font-size:15px; font-weight:600; color:var(--text); margin-bottom:8px;">
                ${room.main_display_text || 'N/A'}
            </div>
            
            ${progressHtml}
            
            <div style="display:flex; justify-content:flex-end; margin-top:8px;">
                <div style="font-size:13px; color:var(--muted); font-weight:500;">
                    ${room.sub_display_text || 'N/A'}
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Side Panel Functions
function closeSidePanel() {
    document.getElementById('side-panel').classList.remove('active');
    document.getElementById('sp-overlay').classList.remove('active');
}

async function openRoomSidePanel(room, colors) {
    const sp = document.getElementById('side-panel');
    const overlay = document.getElementById('sp-overlay');
    const lodgeId = localStorage.getItem('active_lodge_id');

    // Show overlay and panel
    sp.classList.add('active');
    overlay.classList.add('active');

    // Set header immediately
    document.getElementById('sp-room-no').textContent = `Room ${room.room_no}`;
    const badge = document.getElementById('sp-badge');
    badge.textContent = room.badge_text || 'Unknown';
    badge.style.background = colors.bg;
    badge.style.color = colors.text;

    // Reset visibility
    document.getElementById('sp-lease-container').style.display = 'none';
    document.getElementById('sp-vacant-container').style.display = 'none';
    const loading = document.getElementById('sp-loading');
    loading.style.display = 'block';

    try {
        // Empty Room Flow (No Lease)
        if (room.badge_text === 'Vacant' || room.badge_text === 'Maintenance' || !room.lease_id) {
            const roomDetails = await apiFetch(`/rooms/${room.room_id}`);
            
            document.getElementById('sp-room-type').textContent = roomDetails.description || 'N/A';
            document.getElementById('sp-room-status').textContent = roomDetails.status || 'N/A';
            document.getElementById('sp-room-rent').textContent = currencyFormatter.format(roomDetails.base_rent_price || 0);

            loading.style.display = 'none';
            document.getElementById('sp-vacant-container').style.display = 'block';
            document.getElementById('sp-assign-tenant-btn').onclick = () => {
                window.location.href = `leases.html?room_id=${room.room_id}`;
            };
            return;
        }

        // Occupied Room Flow (Uses your new polymorphic endpoint!)
        const leaseInfo = await apiFetch(`/dashboard-landlord/lease-info/${room.lease_id}`);

        // 1. Bind Room
        document.getElementById('sp-room-type').textContent = leaseInfo.room.description || 'N/A';
        document.getElementById('sp-room-status').textContent = leaseInfo.room.status || 'N/A';
        document.getElementById('sp-room-rent').textContent = currencyFormatter.format(leaseInfo.room.base_rent || 0);

        // 2. Bind Lease
        document.getElementById('sp-lease-start').textContent = new Date(leaseInfo.lease.start_date).toLocaleDateString();
        document.getElementById('sp-lease-end').textContent = new Date(leaseInfo.lease.end_date).toLocaleDateString();

        // 3. Bind Financials
        document.getElementById('sp-fin-agreed').textContent = currencyFormatter.format(leaseInfo.finance.agreed_rent || 0);
        document.getElementById('sp-fin-paid').textContent = currencyFormatter.format(leaseInfo.finance.total_paid || 0);
        document.getElementById('sp-fin-balance').textContent = currencyFormatter.format(leaseInfo.finance.remaining_balance || 0);

        // 4. Bind Tenant
        document.getElementById('sp-tenant-name').textContent = leaseInfo.tenant.name || 'N/A';
        document.getElementById('sp-tenant-contact').textContent = leaseInfo.tenant.phone || 'N/A';
        document.getElementById('sp-tenant-avatar').textContent = (leaseInfo.tenant.name || 'T').charAt(0).toUpperCase();

        loading.style.display = 'none';
        document.getElementById('sp-lease-container').style.display = 'block';
        
        // Contextual Actions Redirects
        document.getElementById('sp-tenant-link').onclick = () => {
            window.location.href = 'tenants.html';
        };
        const paymentRedirectUrl = `payments.html?lease_id=${room.lease_id}`;
        document.getElementById('sp-payment-history-link').href = paymentRedirectUrl;
        document.getElementById('sp-log-payment-btn').onclick = () => {
            window.location.href = paymentRedirectUrl + '&open_modal=true';
        };

    } catch (err) {
        loading.style.display = 'none';
        console.error("Failed to load side panel details", err);
        showError("Failed to fetch details: " + err.message);
    }
}
