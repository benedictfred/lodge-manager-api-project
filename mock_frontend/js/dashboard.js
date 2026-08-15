let currentDashboardData = null;
let currentFilter = 'all';
let currentSearch = '';

const safeSetText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
};

const safeSetHTML = (id, html) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
};

document.addEventListener('DOMContentLoaded', () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    safeSetText('lodge-name-display', lodgeName || `Lodge #${lodgeId}`);
    
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-chip').forEach(b => {
                b.classList.remove('bg-white', 'text-slate-800', 'shadow-sm', 'border', 'border-slate-200', 'active');
                b.classList.add('text-slate-500', 'hover:text-slate-800', 'hover:bg-white/80');
            });
            const target = e.currentTarget;
            target.classList.remove('text-slate-500', 'hover:text-slate-800', 'hover:bg-white/80');
            target.classList.add('bg-white', 'text-slate-800', 'shadow-sm', 'border', 'border-slate-200', 'active');
            
            currentFilter = target.getAttribute('data-filter');
            
            const params = new URLSearchParams();
            if (currentFilter === 'Chase Rent') {
                params.append('financial_filters', 'Overdue');
                params.append('financial_filters', 'Owing');
            } else if (currentFilter === 'Overdue') {
                params.append('financial_filters', 'Overdue');
            } else if (currentFilter === 'Safe') {
                params.append('financial_filters', 'Safe');
            } else if (currentFilter === 'Expiring') {
                params.append('financial_filters', 'Expiring');
            } else if (currentFilter === 'Pending') {
                params.append('financial_filters', 'Pending');
            } else if (currentFilter === 'Vacant') {
                params.append('room_statuses', 'Vacant');
            } else if (currentFilter === 'Maintenance') {
                params.append('room_statuses', 'Maintenance');
            }
            const queryString = params.toString() ? `?${params.toString()}` : '';
            fetchDashboard(lodgeId, queryString);
        });
    });

    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.toLowerCase();
            renderDashboardGrid();
        });
    }

    fetchDashboard(lodgeId);
});

async function fetchDashboard(lodgeId, queryString = '') {
    try {
        const data = await apiFetch(`/dashboard-landlord/me/landlord/${lodgeId}${queryString}`);
        currentDashboardData = data;
        
        // Currency Formatter: Values in Naira
        const cF = (val) => {
            if (val === undefined || val === null) return '₦0.00';
            return `₦${val.toLocaleString('en-NG')}.00`;
        };
        
        // Safe DOM bindings for Financials
        if (data && data.financials) {
            safeSetText('fin-potential', cF(data.financials.potential_revenue));
            safeSetText('fin-forecasted', cF(data.financials.forecasted_revenue));
            safeSetText('fin-expected', cF(data.financials.expected_revenue));
            safeSetText('fin-collected', cF(data.financials.collected_revenue));
            safeSetText('fin-unpaid', cF(data.financials.unpaid_rent));
        }
        
        // Safe DOM bindings for Entity Counts
        if (data && data.entity_counts) {
            safeSetText('fact-rooms', data.entity_counts.total_rooms ?? 0);
            safeSetText('fact-tenants', data.entity_counts.total_tenants ?? 0);

            const occRate = data.entity_counts.occupancy_rate ?? 0;
            safeSetText('occ-text', occRate + '%');
            
            const ring = document.getElementById('occ-ring');
            if (ring) {
                const circumference = 175.9;
                const offset = Math.max(0, circumference - (circumference * (occRate / 100)));
                ring.style.strokeDashoffset = offset;
            }
        }

        const pendingMoveouts = (data?.occupied_rooms_lease?.pending || []).length;
        safeSetText('fact-pending-moveouts', pendingMoveouts);
        
        renderDashboardGrid();
        
    } catch (err) {
        showToast(err.message || 'Failed to load dashboard data');
        safeSetHTML('dashboard-grid', `<div class="col-span-full text-center py-12 text-slate-500 font-semibold bg-white rounded-xl border border-slate-200">${err.message || 'Error loading dashboard data'}</div>`);
    }
}

function renderDashboardGrid() {
    if (!currentDashboardData) return;
    const grid = document.getElementById('dashboard-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    let roomsToRender = [];
    const d = currentDashboardData;
    
    const safeRooms = d.occupied_rooms_lease?.safe || [];
    const expiringRooms = d.occupied_rooms_lease?.expiring || [];
    const overdueRooms = d.occupied_rooms_lease?.overdue || [];
    const owingRooms = d.occupied_rooms_lease?.owing || [];
    const pendingRooms = d.occupied_rooms_lease?.pending || [];
    const vRooms = d.vacant_rooms || [];
    const mRooms = d.maintenance_rooms || [];

    const toTitleCase = (str) => {
        if (!str) return '';
        return str.toLowerCase().replace(/\b\w/g, s => s.toUpperCase());
    };

    const getInitials = (name) => {
        if (!name || name === 'N/A' || name === 'Ready to Lease' || name === 'Under Repair' || name === 'Unavailable') return 'RM';
        const parts = name.trim().split(/\s+/);
        if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
        return parts[0].substring(0, 2).toUpperCase();
    };

    roomsToRender = [...safeRooms, ...expiringRooms, ...overdueRooms, ...owingRooms, ...pendingRooms, ...vRooms, ...mRooms];

    if (currentSearch) {
        roomsToRender = roomsToRender.filter(r => 
            String(r.room_no || '').toLowerCase().includes(currentSearch) ||
            String(r.main_display_text || '').toLowerCase().includes(currentSearch)
        );
    }
    
    roomsToRender.sort((a, b) => String(a.room_no || '').localeCompare(String(b.room_no || ''), undefined, {numeric: true, sensitivity: 'base'}));

    safeSetHTML('results-count', `Showing <span class="font-bold">${roomsToRender.length}</span> rooms`);

    if (roomsToRender.length === 0) {
        grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500 font-semibold bg-white rounded-xl border border-slate-200">No rooms match the selected filter.</div>`;
        return;
    }

    roomsToRender.forEach(r => {
        if (!r) return;
        const card = document.createElement('div');
        
        // Case-insensitive Variant Map
        const vKey = String(r.badge_variant || '').toLowerCase();
        
        const variantStyles = {
            'orange': {
                borderTop: 'border-t-red-500',
                badgeText: 'text-red-700 bg-red-50 border-red-200',
                dotBg: 'bg-red-500',
                avatarBg: 'bg-red-100/80 text-red-700',
                barBg: 'bg-gradient-to-r from-red-500 to-rose-600',
                subTextColor: 'text-red-600'
            },
            'danger': {
                borderTop: 'border-t-pink-500',
                badgeText: 'text-pink-700 bg-pink-50 border-pink-200',
                dotBg: 'bg-pink-500',
                avatarBg: 'bg-pink-100/80 text-pink-700',
                barBg: 'bg-gradient-to-r from-pink-500 to-rose-500',
                subTextColor: 'text-pink-600'
            },
            'success': {
                borderTop: 'border-t-emerald-500',
                badgeText: 'text-emerald-700 bg-emerald-50 border-emerald-200',
                dotBg: 'bg-emerald-500',
                avatarBg: 'bg-emerald-100/80 text-emerald-700',
                barBg: 'bg-gradient-to-r from-emerald-400 to-emerald-600',
                subTextColor: 'text-emerald-700'
            },
            'warning': {
                borderTop: 'border-t-amber-500',
                badgeText: 'text-amber-700 bg-amber-50 border-amber-200',
                dotBg: 'bg-amber-500',
                avatarBg: 'bg-amber-100/80 text-amber-700',
                barBg: 'bg-gradient-to-r from-amber-400 to-amber-500',
                subTextColor: 'text-amber-700'
            },
            'purple': {
                borderTop: 'border-t-purple-500',
                badgeText: 'text-purple-700 bg-purple-50 border-purple-200',
                dotBg: 'bg-purple-500',
                avatarBg: 'bg-purple-100/80 text-purple-700',
                barBg: 'bg-gradient-to-r from-purple-500 to-indigo-600',
                subTextColor: 'text-purple-700'
            },
            'info': {
                borderTop: 'border-t-blue-500',
                badgeText: 'text-blue-700 bg-blue-50 border-blue-200',
                dotBg: 'bg-blue-500',
                avatarBg: 'bg-blue-100/80 text-blue-700',
                barBg: 'bg-blue-400',
                subTextColor: 'text-blue-600'
            },
            'inactive': {
                borderTop: 'border-t-slate-400',
                badgeText: 'text-slate-600 bg-slate-100 border-slate-200',
                dotBg: 'bg-slate-400',
                avatarBg: 'bg-slate-100 text-slate-500',
                barBg: 'bg-slate-300',
                subTextColor: 'text-slate-500'
            }
        };

        const styleConfig = variantStyles[vKey] || {
            borderTop: 'border-t-primary',
            badgeText: 'text-primary bg-blue-50 border-blue-200',
            dotBg: 'bg-primary',
            avatarBg: 'bg-blue-100 text-primary',
            barBg: 'bg-primary',
            subTextColor: 'text-slate-500'
        };

        card.className = `bg-white rounded-xl border border-slate-200 shadow-sm p-7 flex flex-col justify-between relative transition-all duration-300 hover:-translate-y-1.5 hover:shadow-lg hover:shadow-slate-200/50 cursor-pointer group`;
        
        const tenantName = toTitleCase(r.main_display_text || 'N/A');
        const tenantInitials = getInitials(r.main_display_text);
        
        let progressPercent = 100;
        let daysLeftVal = null;
        const match = (r.sub_display_text || '').match(/(-?\d+)/);
        if (match) {
            daysLeftVal = parseInt(match[1]);
            progressPercent = Math.min(100, Math.max(0, (daysLeftVal / 365) * 100));
        }

        const isVacantOrMaintenance = !r.lease_id;

        let bottomStatusText = '';
        if (daysLeftVal !== null && daysLeftVal < 0) {
            bottomStatusText = `${Math.abs(daysLeftVal)} days overdue`;
            progressPercent = 0;
        } else {
            bottomStatusText = r.sub_display_text || 'Available';
        }

        card.innerHTML = `
            <div>
                <div class="flex justify-between items-center mb-5">
                    <h3 class="text-lg font-bold text-slate-800 tracking-tight group-hover:text-primary transition-colors">Room ${r.room_no || '??'}</h3>
                    <span class="inline-flex items-center gap-1.5 text-[11px] font-bold ${styleConfig.badgeText} uppercase px-2.5 py-0.5 rounded-full border tracking-wider shadow-sm">
                        <span class="w-1.5 h-1.5 rounded-full ${styleConfig.dotBg}"></span>
                        ${r.badge_text || 'N/A'}
                    </span>
                </div>
                <div class="flex items-center gap-3 mb-6">
                    <div class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-bold uppercase border border-slate-200/60 flex-shrink-0">
                        ${tenantInitials}
                    </div>
                    <p class="text-sm font-semibold text-slate-700 capitalize truncate">${tenantName}</p>
                </div>
            </div>
            
            <div class="mt-auto">
                <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mb-3 border border-slate-200/40">
                    <div class="${isVacantOrMaintenance ? 'bg-slate-200' : styleConfig.barBg} h-full rounded-full transition-all duration-700 ease-out" style="width: ${isVacantOrMaintenance ? 0 : progressPercent}%"></div>
                </div>
                <div class="flex items-center justify-end text-xs">
                    <span class="font-bold tracking-wide text-slate-500">${bottomStatusText}</span>
                </div>
            </div>
        `;
        
        card.onclick = () => openRoomSidePanel(r);
        grid.appendChild(card);
    });
}

async function openRoomSidePanel(roomData) {
    const panel = document.getElementById('room-panel');
    if (panel) panel.classList.add('open');
    
    safeSetText('panel-room-no', `Room ${roomData?.room_no || '??'}`);
    
    const content = document.getElementById('panel-content');
    if (!content) return;
    
    content.innerHTML = '<div style="padding:24px; text-align:center; color:var(--text-secondary);">Loading details...</div>';
    
    try {
        if (!roomData || !roomData.lease_id) {
            content.innerHTML = `
                <div class="space-y-4 p-4">
                    <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
                        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Room Status</div>
                        <div class="text-lg font-bold text-slate-800">${roomData?.badge_text || 'Vacant'}</div>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
                        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Description</div>
                        <div class="text-sm text-slate-700">${roomData?.main_display_text || 'No description provided.'}</div>
                    </div>
                </div>
            `;
            return;
        }

        const lease = await apiFetch(`/leases/${roomData.lease_id}`);
        const cF = (val) => `₦${(val || 0).toLocaleString('en-NG')}.00`;
        
        content.innerHTML = `
            <div class="space-y-6 p-2">
                <div class="bg-blue-50/50 p-4 rounded-lg border border-blue-100 space-y-2">
                    <div class="text-xs font-bold text-primary uppercase tracking-wider">Tenant Profile</div>
                    <div class="text-xl font-bold text-slate-800">${lease.tenant ? (lease.tenant.first_name + ' ' + lease.tenant.last_name) : roomData.main_display_text}</div>
                    <div class="text-sm text-slate-500">${lease.tenant?.email || 'N/A'}</div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Rent Amount</div>
                        <div class="text-base font-bold text-slate-800">${cF(lease.rent_amount)}</div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Lease Status</div>
                        <div class="text-base font-bold text-emerald-600 capitalize">${lease.status}</div>
                    </div>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-500 font-medium">Start Date:</span>
                        <span class="font-semibold text-slate-800">${lease.start_date}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-500 font-medium">End Date:</span>
                        <span class="font-semibold text-slate-800">${lease.end_date}</span>
                    </div>
                </div>
            </div>
        `;
    } catch (err) {
        content.innerHTML = `<div class="p-4 text-red-500 font-semibold">${err.message}</div>`;
    }
}
