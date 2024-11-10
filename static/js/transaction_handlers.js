// Global variables
let currentTransactionId = null;

// Function to refresh transactions
function refreshTransactions() {
    showLoader('Refreshing transactions...');
    location.reload();
}

// Function to export transactions
function exportTransactions() {
    showLoader('Preparing export...');
    
    fetch('/manager/payments/export/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.blob())
    .then(blob => {
        hideLoader();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        hideLoader();
        console.error('Error:', error);
        alert('Error exporting transactions');
    });
}

// Function to view transaction details
function viewTransaction(transactionId) {
    currentTransactionId = transactionId;
    showLoader('Loading transaction details...');
    
    fetch(`/manager/payments/${transactionId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            // Populate modal with transaction data
            document.getElementById('view_transaction_id').textContent = data.id;
            document.getElementById('view_user_email').textContent = data.user_email;
            document.getElementById('view_amount').textContent = `$${data.amount}`;
            document.getElementById('view_balance').textContent = `$${data.balance}`;
            document.getElementById('view_payment_method').textContent = data.payment_method;
            document.getElementById('view_transaction_id_ext').textContent = data.transaction_id;
            document.getElementById('view_fee').textContent = `$${data.fee}`;
            document.getElementById('view_note').textContent = data.note || '-';
            document.getElementById('view_created').textContent = data.created_at;
            document.getElementById('view_status').textContent = data.status;

            // Show modal
            new bootstrap.Modal(document.getElementById('viewTransactionModal')).show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading transaction details');
        })
        .finally(() => {
            hideLoader();
        });
}

// Function to approve transaction
function approveTransaction(transactionId) {
    if (!confirm('Are you sure you want to approve this transaction?')) return;
    
    showLoader('Approving transaction...');
    
    fetch(`/manager/payments/${transactionId}/approve/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            alert(data.error || 'Error approving transaction');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error approving transaction');
    })
    .finally(() => {
        hideLoader();
    });
}

// Function to cancel transaction
function cancelTransaction(transactionId) {
    if (!confirm('Are you sure you want to cancel this transaction?')) return;
    
    showLoader('Cancelling transaction...');
    
    fetch(`/manager/payments/${transactionId}/cancel/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            alert(data.error || 'Error cancelling transaction');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error cancelling transaction');
    })
    .finally(() => {
        hideLoader();
    });
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Status filter buttons
    const statusButtons = document.querySelectorAll('[data-status]');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const status = this.dataset.status;
            window.location.href = `?status=${status}`;
        });
    });

    // Search functionality
    const searchForm = document.querySelector('#transactionSearch').closest('.input-group');
    if (searchForm) {
        searchForm.querySelector('button').addEventListener('click', function(e) {
            e.preventDefault();
            const searchTerm = document.querySelector('#transactionSearch').value;
            const searchType = searchForm.querySelector('select').value;
            window.location.href = `?search=${searchTerm}&type=${searchType}`;
        });
    }

    // Date filter
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            if (this.value === 'custom') {
                // Show date range picker modal
                new bootstrap.Modal(document.getElementById('dateRangeModal')).show();
            } else {
                window.location.href = `?date_filter=${this.value}`;
            }
        });
    }
}); 