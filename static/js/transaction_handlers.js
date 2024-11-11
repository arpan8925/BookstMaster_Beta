function viewTransaction(transactionId) {
    fetch(`/manager/transactions/${transactionId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Populate modal fields with proper formatting
            document.getElementById('view_transaction_id').textContent = data.transaction_id || '-';
            document.getElementById('view_amount').textContent = `$${data.amount}`;
            document.getElementById('view_user_email').textContent = data.user;
            document.getElementById('view_status').textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            document.getElementById('view_payment_method').textContent = data.payment_method;
            document.getElementById('view_transaction_id_ext').textContent = data.transaction_id || '-';
            document.getElementById('view_fee').textContent = `$${data.fee}`;
            document.getElementById('view_note').textContent = data.note;
            document.getElementById('view_created').textContent = data.created_at;
            document.getElementById('view_balance').textContent = `$${data.balance}`;

            // Show appropriate action buttons based on status
            const actionsDiv = document.getElementById('view_transaction_actions');
            actionsDiv.innerHTML = '';

            if (data.status === 'waiting') {
                actionsDiv.innerHTML = `
                    <button class="btn btn-success" onclick="approveTransaction(${data.id})">
                        <i class="bi bi-check-circle me-2"></i>Approve
                    </button>
                    <button class="btn btn-danger ms-2" onclick="cancelTransaction(${data.id})">
                        <i class="bi bi-x-circle me-2"></i>Cancel
                    </button>
                `;
            }

            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('viewTransactionModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading transaction details');
        });
}

function approveTransaction(transactionId) {
    if (!confirm('Are you sure you want to approve this transaction?')) return;

    fetch(`/manager/transactions/${transactionId}/approve/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('viewTransactionModal')).hide();
            location.reload();
        } else {
            alert(data.message || 'Error approving transaction');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error approving transaction');
    });
}

function cancelTransaction(transactionId) {
    if (!confirm('Are you sure you want to cancel this transaction?')) return;

    fetch(`/manager/transactions/${transactionId}/cancel/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('viewTransactionModal')).hide();
            location.reload();
        } else {
            alert(data.message || 'Error canceling transaction');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error canceling transaction');
    });
}

function searchTransactions() {
    const searchQuery = document.getElementById('transactionSearch').value;
    const searchType = document.querySelector('select[name="search_type"]').value;
    const dateFilter = document.getElementById('dateFilter').value;
    
    // Get current URL and update search parameters
    const currentUrl = new URL(window.location.href);
    
    // Update search parameters
    if (searchQuery) {
        currentUrl.searchParams.set('search', searchQuery);
        currentUrl.searchParams.set('type', searchType);
    } else {
        currentUrl.searchParams.delete('search');
        currentUrl.searchParams.delete('type');
    }
    
    // Keep existing date filter
    if (dateFilter && dateFilter !== 'all') {
        currentUrl.searchParams.set('date', dateFilter);
    }
    
    window.location.href = currentUrl.toString();
}

function filterByStatus(status) {
    const currentUrl = new URL(window.location.href);
    if (status === 'all') {
        currentUrl.searchParams.delete('status');
    } else {
        currentUrl.searchParams.set('status', status);
    }
    window.location.href = currentUrl.toString();
}

function filterByDate(value) {
    if (value === 'custom') {
        // Show date range modal with Bootstrap 5
        const dateRangeModal = new bootstrap.Modal(document.getElementById('dateRangeModal'));
        dateRangeModal.show();
    } else {
        const currentUrl = new URL(window.location.href);
        if (value === 'all') {
            currentUrl.searchParams.delete('date');
            currentUrl.searchParams.delete('start_date');
            currentUrl.searchParams.delete('end_date');
        } else {
            currentUrl.searchParams.set('date', value);
            // Remove custom date range params if they exist
            currentUrl.searchParams.delete('start_date');
            currentUrl.searchParams.delete('end_date');
        }
        window.location.href = currentUrl.toString();
    }
}

// Handle custom date range form submission
document.getElementById('dateRangeForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const params = new URLSearchParams(window.location.search);
    
    params.set('start_date', formData.get('start_date'));
    params.set('end_date', formData.get('end_date'));
    params.set('date', 'custom');
    
    window.location.href = `${window.location.pathname}?${params.toString()}`;
});

// Initialize datepicker if using custom date range
document.addEventListener('DOMContentLoaded', function() {
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter.value === 'custom') {
        const dateRangeModal = new bootstrap.Modal(document.getElementById('dateRangeModal'));
        dateRangeModal.show();
    }
});

function refreshTransactions() {
    location.reload();
}

function exportTransactions() {
    // Get current filters
    const searchQuery = document.getElementById('transactionSearch').value;
    const searchType = document.querySelector('.form-select').value;
    const dateFilter = document.getElementById('dateFilter').value;
    
    // Build export URL with current filters
    let exportUrl = `/manager/transactions/export/?`;
    if (searchQuery) exportUrl += `search=${searchQuery}&type=${searchType}&`;
    if (dateFilter) exportUrl += `date=${dateFilter}&`;
    
    window.location.href = exportUrl;
} 