document.addEventListener('DOMContentLoaded', () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName;
    fetchRooms();
});

async function fetchRooms() {
    const tbody = document.getElementById('rooms-tbody');
    try {
        const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
        const rooms = await apiFetch(`/rooms/${activeLodgeId}/rooms?skip=0&limit=100`);
        const lodgeRooms = rooms.filter(r => r.lodge_id === activeLodgeId);
        
        tbody.innerHTML = '';
        if (lodgeRooms.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 24px; color: var(--muted)">No rooms found for this property. Add one above.</td></tr>`;
            return;
        }

        lodgeRooms.forEach(room => {
            const tr = document.createElement('tr');
            
            const rentStr = new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' }).format(room.base_rent_price);
            
            let statusBadge = `<span class="room-badge badge-safe">Vacant</span>`;
            if (room.status === 'Occupied') statusBadge = `<span class="room-badge badge-expiring">Occupied</span>`;
            if (room.status === 'Maintenance') statusBadge = `<span class="room-badge badge-maintenance">Maintenance</span>`;

            tr.innerHTML = `
                <td style="font-weight: 600; color: var(--text)">${room.room_no}</td>
                <td>${room.description || 'N/A'}</td>
                <td>N/A</td>
                <td style="font-weight: 500">${rentStr}</td>
                <td>${statusBadge}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        showError(err.message);
    }
}

function openRoomModal() {
    document.getElementById('room-modal').classList.add('active');
}

function closeRoomModal() {
    document.getElementById('room-modal').classList.remove('active');
}

document.getElementById('create-room-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
    
    const payload = {
        lodge_id: activeLodgeId,
        room_no: document.getElementById('room-no').value,
        description: document.getElementById('room-type').value,
        base_rent_price: parseFloat(document.getElementById('room-rent').value),
        status: "Vacant"
    };

    try {
        await apiFetch('/rooms/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        closeRoomModal();
        showToast('Room added successfully!');
        e.target.reset();
        fetchRooms();
    } catch (err) {
        alert('Failed to add room: ' + err.message);
    }
});
