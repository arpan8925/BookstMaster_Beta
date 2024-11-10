// Global variables
let currentOrderId = null;

// Function to view order details
function viewOrder(orderId) {
    currentOrderId = orderId;
    showLoader('Loading order details...');
    
    fetch(`/manager/orders/${orderId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            // Populate modal with order data
            document.getElementById('view_order_id').textContent = data.id;
            document.getElementById('view_service').textContent = data.service;
            document.getElementById('view_status').textContent = data.status;
            document.getElementById('view_created').textContent = data.created_at;
            document.getElementById('view_user_email').textContent = data.user_email;
            document.getElementById('view_charge').textContent = data.charge;
            document.getElementById('view_link').textContent = data.link;
            document.getElementById('view_link').href = data.link;
            document.getElementById('view_quantity').textContent = data.quantity;
            document.getElementById('view_start_counter').textContent = data.start_counter;
            document.getElementById('view_remains').textContent = data.remains;
            document.getElementById('view_provider').textContent = data.provider;
            document.getElementById('view_provider_order_id').textContent = data.provider_order_id;
            document.getElementById('view_api_response').textContent = data.api_response;

            // Show modal
            new bootstrap.Modal(document.getElementById('viewOrderModal')).show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading order details');
        })
        .finally(() => {
            hideLoader();
        });
}

// Function to check order status
function checkStatus(orderId) {
    showLoader('Checking order status...');
    
    fetch(`/manager/orders/${orderId}/check-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Order status updated successfully');
            location.reload();
        } else {
            alert(data.error || 'Error checking order status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error checking order status');
    })
    .finally(() => {
        hideLoader();
    });
}

// Function to resend order
function resendOrder(orderId) {
    if (!confirm('Are you sure you want to resend this order?')) return;
    
    showLoader('Resending order...');
    
    fetch(`/manager/orders/${orderId}/resend/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Order resent successfully');
            location.reload();
        } else {
            alert(data.error || 'Error resending order');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error resending order');
    })
    .finally(() => {
        hideLoader();
    });
}

// Function to cancel order
function cancelOrder(orderId) {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    
    showLoader('Canceling order...');
    
    fetch(`/manager/orders/${orderId}/cancel/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Order canceled successfully');
            location.reload();
        } else {
            alert(data.error || 'Error canceling order');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error canceling order');
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
    const searchForm = document.querySelector('#orderSearch').closest('form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchTerm = document.querySelector('#orderSearch').value;
            const searchType = document.querySelector('#searchType').value;
            window.location.href = `?search=${searchTerm}&type=${searchType}`;
        });
    }
}); 