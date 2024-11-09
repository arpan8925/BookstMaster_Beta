// Function to handle user editing
function editUser(userId) {
    fetch(`/manager/users/${userId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('edit_user_id').value = userId;
            document.getElementById('edit_username').value = data.username;
            document.getElementById('edit_email').value = data.email;
            document.getElementById('edit_is_active').checked = data.is_active;
            
            // Show the modal
            new bootstrap.Modal(document.getElementById('editUserModal')).show();
        });
}

// Function to view user details
function viewUser(userId) {
    fetch(`/manager/users/${userId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('view_username').textContent = data.username;
            document.getElementById('view_email').textContent = data.email;
            document.getElementById('view_status').textContent = data.is_active ? 'Active' : 'Inactive';
            document.getElementById('view_joined_date').textContent = data.date_joined;
            document.getElementById('view_balance').textContent = `$${data.balance || '0.00'}`;
            document.getElementById('view_total_orders').textContent = data.total_orders || '0';
            document.getElementById('view_last_login').textContent = data.last_login || 'Never';
            
            // Show the modal
            new bootstrap.Modal(document.getElementById('viewUserModal')).show();
        });
}

// Function to handle adding funds
function addFunds(userId) {
    document.getElementById('funds_user_id').value = userId;
    new bootstrap.Modal(document.getElementById('addFundsModal')).show();
}

// Function to handle password setting
function setPassword(userId) {
    document.getElementById('password_user_id').value = userId;
    new bootstrap.Modal(document.getElementById('setPasswordModal')).show();
}

// Function to handle email sending
function sendMail(userId) {
    document.getElementById('mail_user_id').value = userId;
    new bootstrap.Modal(document.getElementById('sendMailModal')).show();
}

// Function to handle user deletion
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        fetch(`/manager/users/${userId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error deleting user');
            }
        });
    }
} 