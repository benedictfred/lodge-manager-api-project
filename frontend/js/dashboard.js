/**
 * LodgeManager Dashboard Logic
 * Fully Restored + Tenant Bio & Action Alerts 🚀
 */

// ===================================================================================
// 1. CONFIGURATION & STATE
// ===================================================================================
let globalRoomData = [];

const UI_CONFIG = {
    themes: {
        'Safe': { bg: 'bg-emerald-50/80', border: 'border-emerald-200', text: 'text-emerald-700', bar: 'bg-emerald-500' },
        'Overdue': { bg: 'bg-rose-50/80', border: 'border-rose-200', text: 'text-rose-700', bar: 'bg-rose-500' },
        'Expiring': { bg: 'bg-amber-50/80', border: 'border-amber-200', text: 'text-amber-700', bar: 'bg-amber-500' },
        'Vacant': { bg: 'bg-gray-200/80', border: 'border-gray-300', text: 'text-gray-700', bar: 'bg-gray-300' },
        'Maintenance': { bg: 'bg-yellow-50/80', border: 'border-yellow-200', text: 'text-yellow-700', bar: 'bg-yellow-500' }
    },
    currency: new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN', maximumFractionDigits: 0 }),
    date: new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
};

// ===================================================================================
// 2. MOCK DATA ENGINE (Now with deeper Bio Data!)
// ===================================================================================
function generateMockData() {
    const dummyNames = ["Chinedu Okafor", "Aisha Bello", "Emeka Nwosu", "Fatima Aliyu", "Tunde Bakare"];
    const rooms = [];
    const today = new Date();

    for (let i = 1; i <= 20; i++) {
        const rand = Math.random();
        let status = 'Occupied';
        if (rand > 0.7) status = 'Vacant';
        if (rand > 0.9) status = 'Maintenance';

        let active_lease = null;

        if (status === 'Occupied') {
            const scenario = Math.random();
            let daysLeft, paymentStatus, percentageComplete;
            const totalDays = 365;

            let start = new Date(today); start.setDate(today.getDate() - Math.floor(Math.random() * 200));
            let end = new Date(today);

            if (scenario < 0.2) {
                daysLeft = -Math.floor(Math.random() * 30) - 1; paymentStatus = 'Overdue'; percentageComplete = 100;
            } else if (scenario < 0.5) {
                daysLeft = Math.floor(Math.random() * 89) + 1; paymentStatus = 'Expiring'; percentageComplete = ((totalDays - daysLeft) / totalDays) * 100;
            } else {
                daysLeft = Math.floor(Math.random() * 200) + 90; paymentStatus = 'Safe'; percentageComplete = ((totalDays - daysLeft) / totalDays) * 100;
            }
            end.setDate(today.getDate() + daysLeft);

            const nameParts = dummyNames[i % dummyNames.length].split(" ");
            active_lease = {
                // NEW BIO DATA ADDED HERE
                tenant: {
                    first_name: nameParts[0],
                    last_name: nameParts[1],
                    email: `${nameParts[0].toLowerCase()}@example.com`,
                    phone: `0803 ${Math.floor(Math.random() * 900) + 100} ${Math.floor(Math.random() * 9000) + 1000}`,
                    department: ["Software Engineering", "Computer Science", "Law", "Medicine", "Business Admin"][Math.floor(Math.random() * 5)],
                    level: ["100L", "200L", "300L", "400L", "500L"][Math.floor(Math.random() * 5)],
                    guarantor_name: "Mr/Mrs " + dummyNames[(i + 1) % dummyNames.length],
                    guarantor_phone: `0812 ${Math.floor(Math.random() * 900000) + 100000}`
                },
                agreed_rent_amt: 250000,
                amount_paid: paymentStatus === 'Overdue' ? 200000 : 250000,
                start_date: start.toISOString().split('T')[0],
                end_date: end.toISOString().split('T')[0],
                timeline: { days_left: daysLeft, payment_status: paymentStatus, percentage_complete: parseFloat(percentageComplete.toFixed(2)) },
                payment_history: [
                    { date: start.toISOString().split('T')[0], amount: 150000, method: "Bank Transfer", ref: `TXN-${Math.floor(Math.random() * 90000) + 10000}` },
                    { date: new Date(start.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], amount: paymentStatus === 'Overdue' ? 50000 : 100000, method: "Cash", ref: `RCPT-${Math.floor(Math.random() * 9000) + 1000}` }
                ]
            };
        }
        rooms.push({ id: i, room_no: `${100 + i}`, description: "Standard Unit with excellent ventilation.", status: status, active_lease: active_lease });
    }
    return rooms.sort((a, b) => String(a.room_no).localeCompare(String(b.room_no), undefined, { numeric: true }));
}

// ===================================================================================
// 3. CORE RENDERING ENGINE
// ===================================================================================
function renderGrid(rooms) {
    const container = document.getElementById('gridContainer');
    const template = document.getElementById('room-card-template');
    container.innerHTML = '';

    rooms.forEach(room => {
        const clone = template.content.cloneNode(true);
        const card = clone.querySelector('.room-card');
        const lease = room.active_lease;
        const state = lease ? lease.timeline.payment_status : room.status;
        const theme = UI_CONFIG.themes[state];

        clone.querySelector('.room-no').textContent = `Rm ${room.room_no}`;

        const tenantNameEl = clone.querySelector('.tenant-name');
        if (lease) tenantNameEl.textContent = `Tenant: ${lease.tenant.first_name}`;
        else if (room.status === 'Maintenance') tenantNameEl.textContent = 'Currently Unavailable';
        else tenantNameEl.textContent = 'Ready for Tenant';

        const badge = clone.querySelector('.status-badge');
        badge.textContent = state;
        badge.className += ` ${theme.bg} ${theme.border} ${theme.text}`;

        const bar = clone.querySelector('.progress-bar');
        const daysLabel = clone.querySelector('.days-left');

        if (lease) {
            bar.style.width = `${lease.timeline.percentage_complete}%`;
            bar.classList.add(theme.bar);
            const absDays = Math.abs(lease.timeline.days_left);
            daysLabel.textContent = lease.timeline.days_left < 0 ? `Expired ${absDays}d ago` : `${absDays} days left`;
            daysLabel.classList.add(theme.text);
        } else {
            bar.style.width = '0%';
            daysLabel.textContent = room.status === 'Maintenance' ? 'Under Maintenance' : 'Available';
            daysLabel.classList.add('text-gray-400', 'italic');
        }

        card.onclick = () => openPanel(room.id);
        container.appendChild(clone);
    });
    updateFinancialStats(rooms);
}

// ===================================================================================
// 4. MODAL LOGIC
// ===================================================================================
function openModal(title, contentHtml, onSave) {
    const container = document.getElementById('modalContainer');
    const shell = document.getElementById('modalShell');
    const saveBtn = document.getElementById('modalSaveBtn');

    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalContent').innerHTML = contentHtml;

    if (onSave) {
        saveBtn.classList.remove('hidden');
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        newSaveBtn.addEventListener('click', onSave);
    } else {
        saveBtn.classList.add('hidden'); // Hides "Save" for Bio Data & History!
    }

    container.classList.remove('hidden');
    setTimeout(() => {
        shell.classList.remove('opacity-0', 'scale-95');
        shell.classList.add('opacity-100', 'scale-100');
    }, 10);
}

function closeModal() {
    const shell = document.getElementById('modalShell');
    shell.classList.remove('opacity-100', 'scale-100');
    shell.classList.add('opacity-0', 'scale-95');
    setTimeout(() => {
        document.getElementById('modalContainer').classList.add('hidden');
        document.getElementById('modalContent').innerHTML = '';
    }, 300);
}
document.getElementById('modalCancelBtn').addEventListener('click', closeModal);

// ===================================================================================
// 5. ADD ROOM LOGIC
// ===================================================================================
document.getElementById('addRoomBtn').addEventListener('click', () => {
    const formHtml = `
        <form id="addRoomForm" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-indigo-900 mb-1">Room Number</label>
                <input type="text" id="newRoomNo" required class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-indigo-900 mb-1">Status</label>
                <select id="newRoomStatus" class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-indigo-500">
                    <option value="Vacant">Vacant</option>
                    <option value="Maintenance">Under Maintenance</option>
                </select>
            </div>
        </form>`;

    openModal('Register New Room', formHtml, () => {
        const roomNo = document.getElementById('newRoomNo').value;
        if (!roomNo) return alert("Room Number is required!");
        globalRoomData.push({
            id: Date.now(), room_no: roomNo, description: "Standard unit.",
            status: document.getElementById('newRoomStatus').value, active_lease: null
        });
        globalRoomData.sort((a, b) => String(a.room_no).localeCompare(String(b.room_no), undefined, { numeric: true }));
        renderGrid(globalRoomData);
        closeModal();
    });
});

// ===================================================================================
// 6. SIDE PANEL LOGIC (WITH TENANT BIO & ALERTS)
// ===================================================================================
function openPanel(roomId) {
    const room = globalRoomData.find(r => r.id === roomId);
    if (!room) return;

    document.getElementById('panelRoomNo').innerText = `Room ${room.room_no}`;
    document.getElementById('panelDesc').innerText = room.description;

    const state = room.active_lease ? room.active_lease.timeline.payment_status : room.status;
    const theme = UI_CONFIG.themes[state];
    const badge = document.getElementById('panelStatusBadge');
    badge.className = `px-3 py-1 text-xs font-bold rounded-full border ${theme.bg} ${theme.border} ${theme.text}`;
    badge.innerText = state;

    const tlSec = document.getElementById('timelineSection');
    const finSec = document.getElementById('financeSection');
    const tenSec = document.getElementById('tenantSection');
    const vacSec = document.getElementById('vacantSection');
    const assignBtn = document.getElementById('assignTenantBtn');
    const maintBtn = document.getElementById('removeFromMaintenanceBtn');

    if (room.status === 'Occupied' && room.active_lease) {
        tlSec.classList.remove('hidden'); finSec.classList.remove('hidden');
        tenSec.classList.remove('hidden'); vacSec.classList.add('hidden');

        const lease = room.active_lease;

        // Timeline population
        const pBar = document.getElementById('panelProgressBar');
        pBar.style.width = `${lease.timeline.percentage_complete}%`;
        pBar.className = `h-3 rounded-full transition-all duration-500 ${theme.bar}`;

        const daysEl = document.getElementById('panelDaysLeft');
        const absDays = Math.abs(lease.timeline.days_left);
        daysEl.innerHTML = `<span class="${theme.text} font-bold">${lease.timeline.days_left < 0 ? 'Expired '+absDays+' days ago' : absDays+' days left'}</span>`;

        document.getElementById('panelStartDate').innerText = UI_CONFIG.date.format(new Date(lease.start_date));
        document.getElementById('panelEndDate').innerText = UI_CONFIG.date.format(new Date(lease.end_date));

        // Finance population
        document.getElementById('panelAgreedRent').innerText = UI_CONFIG.currency.format(lease.agreed_rent_amt);
        document.getElementById('viewPaymentsBtn').onclick = () => {
            let historyHtml = `<div class="overflow-hidden rounded-lg border border-indigo-100 shadow-sm"><table class="w-full text-sm text-left"><thead class="text-xs text-indigo-600 uppercase bg-indigo-50"><tr><th class="px-4 py-3">Date</th><th class="px-4 py-3">Amount</th><th class="px-4 py-3">Ref</th></tr></thead><tbody class="divide-y divide-indigo-50">`;
            if (lease.payment_history && lease.payment_history.length > 0) {
                lease.payment_history.forEach(p => {
                    historyHtml += `<tr class="bg-white"><td class="px-4 py-3 font-medium text-indigo-900">${UI_CONFIG.date.format(new Date(p.date))}</td><td class="px-4 py-3 font-bold text-emerald-600">${UI_CONFIG.currency.format(p.amount)}</td><td class="px-4 py-3 text-xs text-gray-500">${p.ref}</td></tr>`;
                });
            } else { historyHtml += `<tr><td colspan="3" class="px-4 py-6 text-center text-gray-400 italic">No payments.</td></tr>`; }
            historyHtml += `</tbody></table></div>`;
            openModal(`Payment History: Rm ${room.room_no}`, historyHtml);
        };

        // Tenant population
        const fullName = `${lease.tenant.first_name} ${lease.tenant.last_name}`;
        document.getElementById('tenantFullName').innerText = fullName;
        document.getElementById('tenantInitials').innerText = lease.tenant.first_name[0] + (lease.tenant.last_name ? lease.tenant.last_name[0] : '');
        document.getElementById('tenantEmail').innerText = lease.tenant.phone;

        // ACTION BUTTONS (CALL / EMAIL ALERT)
        const actionArea = document.getElementById('tenantActionArea');
        if (state === 'Overdue' || state === 'Expiring') {
            actionArea.classList.remove('hidden');
            actionArea.classList.add('flex');

            const btnCall = document.getElementById('btnCallTenant');
            const btnEmail = document.getElementById('btnEmailTenant');

            // Native Phone Dialer Protocol
            btnCall.href = `tel:${lease.tenant.phone.replace(/\s+/g, '')}`;

            // Pre-written Email Protocol
            const subject = encodeURIComponent(`LodgeManager Notice: Rent ${state} for Rm ${room.room_no}`);
            const body = encodeURIComponent(`Hello ${lease.tenant.first_name},\n\nThis is an automated reminder regarding your rent for Room ${room.room_no}. Your current status is ${state}.\n\nPlease arrange payment as soon as possible.\n\nThank you.`);
            btnEmail.href = `mailto:${lease.tenant.email}?subject=${subject}&body=${body}`;

            // Theme the email button based on severity
            if(state === 'Overdue') {
                btnEmail.className = "flex-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold py-2 px-3 rounded-lg transition-colors shadow-sm text-xs flex justify-center items-center gap-2";
            } else {
                btnEmail.className = "flex-1 bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 font-bold py-2 px-3 rounded-lg transition-colors shadow-sm text-xs flex justify-center items-center gap-2";
            }
        } else {
            actionArea.classList.add('hidden');
            actionArea.classList.remove('flex');
        }

        // BIO DATA MODAL (The Clickable Profile)
        document.getElementById('tenantProfileCard').onclick = () => {
            const bioHtml = `
                <div class="space-y-6">
                    <div class="flex items-center gap-4 border-b border-indigo-50 pb-4">
                        <div class="w-16 h-16 rounded-full bg-indigo-100 text-indigo-700 text-xl font-bold flex items-center justify-center shrink-0 border-2 border-indigo-200">
                            ${lease.tenant.first_name[0]}${lease.tenant.last_name ? lease.tenant.last_name[0] : ''}
                        </div>
                        <div>
                            <h2 class="text-2xl font-black text-indigo-900">${fullName}</h2>
                            <p class="text-sm font-medium text-emerald-600">Active Tenant • Rm ${room.room_no}</p>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-indigo-50/50 p-3 rounded-lg border border-indigo-50">
                            <p class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">Phone Number</p>
                            <p class="text-sm font-medium text-indigo-900">${lease.tenant.phone}</p>
                        </div>
                        <div class="bg-indigo-50/50 p-3 rounded-lg border border-indigo-50">
                            <p class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">Email</p>
                            <p class="text-sm font-medium text-indigo-900 truncate" title="${lease.tenant.email}">${lease.tenant.email}</p>
                        </div>
                        <div class="bg-indigo-50/50 p-3 rounded-lg border border-indigo-50">
                            <p class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">Department</p>
                            <p class="text-sm font-medium text-indigo-900">${lease.tenant.department}</p>
                        </div>
                        <div class="bg-indigo-50/50 p-3 rounded-lg border border-indigo-50">
                            <p class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">Level</p>
                            <p class="text-sm font-medium text-indigo-900">${lease.tenant.level}</p>
                        </div>
                    </div>

                    <div class="bg-rose-50/50 p-4 rounded-lg border border-rose-100">
                        <h4 class="text-xs font-bold text-rose-500 uppercase tracking-wider mb-3">Guarantor / Emergency</h4>
                        <div class="space-y-2">
                            <div class="flex justify-between">
                                <span class="text-sm text-rose-700/80">Name</span>
                                <span class="text-sm font-medium text-rose-900">${lease.tenant.guarantor_name}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-sm text-rose-700/80">Phone</span>
                                <span class="text-sm font-medium text-rose-900">${lease.tenant.guarantor_phone}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            openModal('Tenant Details', bioHtml);
        };

    } else {
        tlSec.classList.add('hidden'); finSec.classList.add('hidden'); tenSec.classList.add('hidden');
        vacSec.classList.remove('hidden');

        if(room.status === 'Vacant') {
            assignBtn.classList.remove('hidden'); maintBtn.classList.add('hidden');
            document.getElementById('vacantMsgText').innerText = "This room is currently vacant.";
            assignBtn.onclick = () => alert("Link this to FastAPI 'POST /leases' later!");
        } else {
            assignBtn.classList.add('hidden'); maintBtn.classList.remove('hidden');
            document.getElementById('vacantMsgText').innerText = "This room is under maintenance.";
            maintBtn.onclick = () => { room.status = 'Vacant'; closePanel(); renderGrid(globalRoomData); };
        }
    }

    document.getElementById('sidePanel').classList.remove('translate-x-full');
    document.getElementById('panelOverlay').classList.remove('hidden');
    setTimeout(() => document.getElementById('panelOverlay').classList.remove('opacity-0'), 10);
}

function closePanel() {
    document.getElementById('sidePanel').classList.add('translate-x-full');
    document.getElementById('panelOverlay').classList.add('opacity-0');
    setTimeout(() => document.getElementById('panelOverlay').classList.add('hidden'), 300);
}

// ===================================================================================
// 7. UTILITIES & INIT
// ===================================================================================
function updateFinancialStats(rooms) {
    let expected = 0, collected = 0;
    rooms.forEach(r => { if (r.active_lease) { expected += r.active_lease.agreed_rent_amt; collected += r.active_lease.amount_paid; } });
    document.getElementById('statExpected').textContent = UI_CONFIG.currency.format(expected);
    document.getElementById('statCollected').textContent = UI_CONFIG.currency.format(collected);
    document.getElementById('statOutstanding').textContent = UI_CONFIG.currency.format(expected - collected);
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        globalRoomData = generateMockData();
        renderGrid(globalRoomData);

        const checkboxes = document.querySelectorAll('.filter-checkbox');
        const badge = document.getElementById('filterCountBadge');
        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                const activeFilters = [...checkboxes].filter(c => c.checked).map(c => c.value);
                badge.textContent = activeFilters.length;
                activeFilters.length > 0 ? badge.classList.remove('hidden') : badge.classList.add('hidden');

                const filtered = activeFilters.length === 0 ? globalRoomData : globalRoomData.filter(r => {
                    const status = r.active_lease ? r.active_lease.timeline.payment_status : r.status;
                    return activeFilters.includes(status);
                });
                renderGrid(filtered);
            });
        });
    }, 800);

    document.getElementById('filterToggleBtn').onclick = (e) => {
        e.stopPropagation(); document.getElementById('filterDropdown').classList.toggle('hidden');
    };
    document.onclick = () => document.getElementById('filterDropdown').classList.add('hidden');
});