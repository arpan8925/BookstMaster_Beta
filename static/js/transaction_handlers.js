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
                alert(data.error || 'Error approving transaction');
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
                alert(data.error || 'Error cancelling transaction');
            }
        });
    }
}

function searchTransactions() {
    const searchQuery = document.getElementById('transactionSearch').value;
    const searchType = document.querySelector('.form-select').value;
    window.location.href = `?search=${searchQuery}&type=${searchType}`;
}

function filterByDate(value) {
    if (value === 'custom') {
        // Show date range modal
        $('#dateRangeModal').modal('show');
    } else {
        window.location.href = `?date=${value}`;
    }
} 