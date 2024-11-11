function viewTransaction(id) {
    window.location.href = `/manager/transactions/${id}/`;
}

function approveTransaction(id) {
    if (confirm('Are you sure you want to approve this transaction?')) {
        fetch(`/manager/transactions/${id}/approve/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert(data.message || 'Error approving transaction');
            }
        });
    }
}

function cancelTransaction(id) {
    if (confirm('Are you sure you want to cancel this transaction?')) {
        fetch(`/manager/transactions/${id}/cancel/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert(data.message || 'Error cancelling transaction');
            }
        });
    }
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
    
    const startDate = this.querySelector('[name="start_date"]').value;
    const endDate = this.querySelector('[name="end_date"]').value;
    
    // Validate dates
    if (new Date(startDate) > new Date(endDate)) {
        alert('Start date cannot be later than end date');
        return;
    }
    
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('date', 'custom');
    currentUrl.searchParams.set('start_date', startDate);
    currentUrl.searchParams.set('end_date', endDate);
    
    window.location.href = currentUrl.toString();
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