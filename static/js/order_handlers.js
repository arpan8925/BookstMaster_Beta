function showLoader(message) {
    // You can implement a proper loader UI here
    console.log(message);
}

function hideLoader() {
    // Hide your loader UI
    console.log('Loading complete');
}

function viewOrder(orderId) {
    // Show the modal immediately with loading state
    const modal = new bootstrap.Modal(document.getElementById('viewOrderModal'));
    modal.show();
    
    // Set loading state
    setModalLoadingState();
    
    // Fetch order details
    fetch(`/managerdashboard/orders/${orderId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            updateModalWithData(data);
            
            // Update action buttons based on status
            const actionButtons = document.getElementById('order-action-buttons');
            actionButtons.innerHTML = '';
            
            if (data.status === 'pending') {
                actionButtons.innerHTML = `
                    <button class="btn btn-success" onclick="completeOrder(${orderId})">
                        <i class="bi bi-check-circle me-2"></i>Complete Order
                    </button>
                    <button class="btn btn-danger" onclick="cancelOrder(${orderId})">
                        <i class="bi bi-x-circle me-2"></i>Cancel Order
                    </button>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            setModalErrorState();
        });
}

// Helper function to set loading state
function setModalLoadingState() {
    const loadingText = 'Loading...';
    document.getElementById('modal-order-id').textContent = loadingText;
    document.getElementById('modal-order-status').innerHTML = '<span class="badge bg-secondary">Loading...</span>';
    document.getElementById('modal-order-date').textContent = loadingText;
    document.getElementById('modal-order-updated').textContent = loadingText;
    document.getElementById('modal-service-name').textContent = loadingText;
    document.getElementById('modal-order-quantity').textContent = loadingText;
    document.getElementById('modal-order-price').textContent = loadingText;
    document.getElementById('modal-order-link').textContent = loadingText;
    document.getElementById('modal-user-email').textContent = loadingText;
}

// Helper function to update modal with data
function updateModalWithData(data) {
    document.getElementById('modal-order-id').textContent = `#${data.id}`;
    document.getElementById('modal-order-status').innerHTML = getStatusBadge(data.status);
    document.getElementById('modal-order-date').textContent = formatDate(data.created_at);
    document.getElementById('modal-order-updated').textContent = formatDate(data.updated_at);
    document.getElementById('modal-service-name').textContent = data.service;
    document.getElementById('modal-order-quantity').textContent = data.quantity;
    document.getElementById('modal-order-price').textContent = `$${data.charge}`;
    document.getElementById('modal-order-link').textContent = data.link;
    document.getElementById('modal-order-link').href = data.link;
    document.getElementById('modal-user-email').textContent = data.user_email;
}

// Helper function to set error state
function setModalErrorState() {
    document.getElementById('modal-order-id').textContent = 'Error loading data';
    document.getElementById('modal-order-status').innerHTML = '<span class="badge bg-danger">Error</span>';
    document.getElementById('modal-order-date').textContent = 'Error';
    document.getElementById('modal-order-updated').textContent = 'Error';
    document.getElementById('modal-service-name').textContent = 'Error loading service details';
    document.getElementById('modal-order-quantity').textContent = 'Error';
    document.getElementById('modal-order-price').textContent = 'Error';
    document.getElementById('modal-order-link').textContent = 'Error loading link';
    document.getElementById('modal-user-email').textContent = 'Error loading user details';
}

// Helper function to format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Helper function to generate status badge HTML
function getStatusBadge(status) {
    const badges = {
        'completed': '<span class="badge bg-success-subtle text-success">Completed</span>',
        'pending': '<span class="badge bg-warning-subtle text-warning">Pending</span>',
        'processing': '<span class="badge bg-info-subtle text-info">Processing</span>',
        'canceled': '<span class="badge bg-danger-subtle text-danger">Canceled</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
        'refunded': '<span class="badge bg-secondary">Refunded</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
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
    
    fetch(`/managerdashboard/orders/${orderId}/cancel/`, {
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

function completeOrder(orderId) {
    if (!confirm('Are you sure you want to mark this order as completed?')) {
        return;
    }

    fetch(`/managerdashboard/orders/${orderId}/complete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Show success message
            alert('Order completed successfully');
            // Refresh the page to show updated status
            location.reload();
        } else {
            alert(data.message || 'Failed to complete the order');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while completing the order');
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