document.addEventListener('DOMContentLoaded', async () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName;
    await fetchTenants();
    
    // Auto-open modal if tenant_id is in query string
    const urlParams = new URLSearchParams(window.location.search);
    const tenantId = urlParams.get('tenant_id');
    if (tenantId) {
        openTenantModal(parseInt(tenantId, 10));
    }
});

let globalTenants = [];

async function fetchTenants() {
    const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
    const tbody = document.getElementById('tenants-tbody');
    
    try {
        const tenants = await apiFetch(`/lodges/${activeLodgeId}/tenants`);
        globalTenants = tenants;
        
        tbody.innerHTML = '';
        if (tenants.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 24px; color: var(--muted)">No tenants found. Provide them with the registration link to join.</td></tr>`;
            return;
        }

        tenants.forEach(tenant => {
            const tr = document.createElement('tr');
            
            const nameStr = tenant.user ? `${tenant.user.first_name} ${tenant.user.last_name}` : `Tenant ${tenant.id}`;
            const emailStr = tenant.user ? tenant.user.email : 'N/A';
            const phoneStr = tenant.user && tenant.user.phone_no ? tenant.user.phone_no : 'N/A';

            tr.innerHTML = `
                <td style="font-weight: 600; color: var(--text)">${nameStr}</td>
                <td>${emailStr}</td>
                <td>${phoneStr}</td>
                <td>
                    <button class="btn" style="padding: 6px 12px; font-size:12px; border: 1px solid var(--border); background: var(--surface2);" onclick="openTenantModal(${tenant.id})">View Profile</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        showError(err.message);
    }
}

function openTenantModal(tenantId) {
    const tenant = globalTenants.find(t => t.id === tenantId);
    if (!tenant) return;

    document.getElementById('tenant-modal').classList.add('active');
    
    const user = tenant.user || {};
    const first = user.first_name || '';
    const last = user.last_name || '';
    
    document.getElementById('modal-avatar').textContent = first ? first.charAt(0).toUpperCase() : 'T';
    document.getElementById('modal-name').textContent = (first || last) ? `${first} ${last}` : `Tenant ${tenant.id}`;
    document.getElementById('modal-id').textContent = `ID: ${tenant.id}`;
    
    document.getElementById('modal-email').textContent = user.email || 'N/A';
    document.getElementById('modal-phone').textContent = user.phone_no || 'N/A';
    document.getElementById('modal-tenant-type').textContent = tenant.tenant_type || 'N/A';
    
    document.getElementById('modal-em-name').textContent = tenant.emergency_contact_name || 'N/A';
    document.getElementById('modal-em-phone').textContent = tenant.emergency_contact_phone_no || 'N/A';
    
    const studentFields = document.getElementById('modal-student-fields');
    if (tenant.tenant_type === 'Student') {
        studentFields.style.display = 'block';
        document.getElementById('modal-level').textContent = tenant.level || 'N/A';
        document.getElementById('modal-reg-no').textContent = tenant.reg_no || 'N/A';
        document.getElementById('modal-department').textContent = tenant.department || 'N/A';
    } else {
        studentFields.style.display = 'none';
    }
}

function closeTenantModal() {
    document.getElementById('tenant-modal').classList.remove('active');
}

async function copyInviteLink() {
    const lodgeId = localStorage.getItem('active_lodge_id');
    if (!lodgeId) {
        alert('No active lodge found.');
        return;
    }
    
    // Construct the link dynamically based on the current window location
    const origin = window.location.origin;
    let basePath = window.location.pathname;
    basePath = basePath.substring(0, basePath.lastIndexOf('/'));
    const link = `${origin}${basePath}/tenant-register.html?lodge_id=${lodgeId}`;
    
    try {
        await navigator.clipboard.writeText(link);
        if (typeof showToast === 'function') {
            showToast('Invite link copied to clipboard!');
        } else {
            alert('Invite link copied to clipboard: \n' + link);
        }
    } catch (err) {
        // Fallback for older browsers or if clipboard API fails
        prompt("Copy this invite link and send to your tenant:", link);
    }
}
