// Global loading state
let isLoading = false;

// Show loader function
function showLoader(message = 'Please wait...') {
    if (isLoading) return; // Prevent multiple loaders
    
    isLoading = true;
    document.body.classList.add('loading');
    
    const loader = document.createElement('div');
    loader.className = 'loader-overlay';
    loader.innerHTML = `
        <div class="loader-content">
            <div class="loader-spinner"></div>
            <p class="mt-2">${message}</p>
        </div>
    `;
    document.body.appendChild(loader);
}

// Hide loader function
function hideLoader() {
    isLoading = false;
    document.body.classList.remove('loading');
    const loader = document.querySelector('.loader-overlay');
    if (loader) {
        loader.remove();
    }
}

// Add loading state to all fetch requests
function fetchWithLoader(url, options = {}, loadingMessage = 'Please wait...') {
    showLoader(loadingMessage);
    
    return fetch(url, options)
        .finally(() => {
            hideLoader();
        });
}

// Update the edit service function
function editService(serviceId) {
    showLoader('Loading service information...');
    
    fetchWithLoader(`/manager/services/${serviceId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            // Populate the edit modal with service data
            document.getElementById('edit_service_id').value = serviceId;
            document.getElementById('edit_name').value = data.name;
            
            // Find and select the correct category option
            const categorySelect = document.getElementById('edit_category');
            const categoryOptions = categorySelect.options;
            for (let i = 0; i < categoryOptions.length; i++) {
                if (categoryOptions[i].text === data.category) {
                    categorySelect.selectedIndex = i;
                    break;
                }
            }
            
            document.getElementById('edit_rate').value = data.rate;
            document.getElementById('edit_min_order').value = data.min_order;
            document.getElementById('edit_max_order').value = data.max_order;
            document.getElementById('edit_description').value = data.description;
            document.getElementById('edit_is_active').checked = data.status === 'active';
            document.getElementById('edit_is_drip_feed').checked = data.is_drip_feed;

            // Show the modal
            new bootstrap.Modal(document.getElementById('editServiceModal')).show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading service information');
        });
}

// Add debounce function to prevent rapid firing of events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update event listeners to use debounce
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality with debounce
    const searchInput = document.getElementById('serviceSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterServices();
        }, 300));
    }

    // Add error handling for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (isLoading) {
                e.preventDefault();
                return;
            }
        });
    });

    // Add error handling for all interactive elements
    document.addEventListener('click', function(e) {
        if (isLoading) {
            e.preventDefault();
            return;
        }
    }, true);
});

// Add cleanup function for modals
function cleanupModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            // Clear form fields
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }
            
            // Remove any error messages
            const errorMessages = modal.querySelectorAll('.invalid-feedback');
            errorMessages.forEach(el => el.remove());
            
            // Remove any validation classes
            const inputs = modal.querySelectorAll('.is-invalid, .is-valid');
            inputs.forEach(input => {
                input.classList.remove('is-invalid', 'is-valid');
            });
        });
    }
}

// Initialize cleanup for all modals
document.addEventListener('DOMContentLoaded', function() {
    cleanupModal('editServiceModal');
    cleanupModal('addServiceModal');
    cleanupModal('viewServiceModal');
});

// Service handlers
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('serviceSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterServices();
        });
    }

    // Category filter
    const categorySelect = document.getElementById('serviceCategory');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            filterServices();
        });
    }

    // Select all services
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.service-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    // Service form submission handler
    const addServiceForm = document.getElementById('addServiceForm');
    if (addServiceForm) {
        addServiceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            console.log('Form submitted'); // Debug log
            
            const formData = new FormData(this);
            
            // Log form data for debugging
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
            
            fetch('/manager/services/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                console.log('Response status:', response.status); // Debug log
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // Debug log
                if (data.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addServiceModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Reload page to show new service
                    location.reload();
                } else {
                    alert(data.error || 'Error creating service');
                }
            })
            .catch(error => {
                console.error('Error:', error); // Debug log
                alert('Error creating service');
            });
        });
    }

    // Edit Service Form Handler
    const editServiceForm = document.getElementById('editServiceForm');
    if (editServiceForm) {
        editServiceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const serviceId = document.getElementById('edit_service_id').value;
            const formData = new FormData(this);

            fetch(`/manager/services/${serviceId}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert(data.error || 'Error updating service');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

// Filter services based on search and category
function filterServices() {
    const searchTerm = document.getElementById('serviceSearch').value.toLowerCase();
    const category = document.getElementById('serviceCategory').value.toLowerCase();
    const rows = document.querySelectorAll('#servicesTableBody tr');

    rows.forEach(row => {
        const name = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        const serviceCategory = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
        const matchesSearch = name.includes(searchTerm);
        const matchesCategory = category === '' || serviceCategory.includes(category);
        row.style.display = matchesSearch && matchesCategory ? '' : 'none';
    });
}

// Import selected services
function importSelectedServices() {
    const selectedServices = [];
    document.querySelectorAll('.service-select:checked').forEach(checkbox => {
        selectedServices.push(checkbox.value);
    });

    if (selectedServices.length === 0) {
        alert('Please select services to import');
        return;
    }

    showLoader('Importing services...');

    fetch('/manager/providers/import-services/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            provider_id: currentProviderId,
            service_ids: selectedServices
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.status === 'success') {
            alert(`Successfully imported ${data.imported} services`);
            location.reload();
        } else {
            alert(data.error || 'Error importing services');
        }
    })
    .catch(error => {
        hideLoader();
        alert('Error importing services');
    });
}

// Sync services
function syncServices(providerId) {
    showLoader('Syncing services...');
    
    fetch(`/manager/providers/${providerId}/sync-services/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.status === 'success') {
            alert(`Successfully synced ${data.added} new services, updated ${data.updated} services, and removed ${data.removed} services.`);
            location.reload();
        } else {
            alert(data.error || 'Error syncing services');
        }
    })
    .catch(error => {
        hideLoader();
        alert('Error syncing services');
    });
}

// Helper functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to view service
function viewService(serviceId) {
    fetch(`/manager/services/${serviceId}/get-info/`)
        .then(response => response.json())
        .then(data => {
            // Populate the view modal with service data
            document.getElementById('view_name').textContent = data.name;
            document.getElementById('view_category').textContent = data.category;
            document.getElementById('view_rate').textContent = data.rate;
            document.getElementById('view_min').textContent = data.min_order;
            document.getElementById('view_max').textContent = data.max_order;
            document.getElementById('view_description').textContent = data.description;
            document.getElementById('view_status').textContent = data.status;

            // Show the modal
            new bootstrap.Modal(document.getElementById('viewServiceModal')).show();
        })
        .catch(error => console.error('Error:', error));
}

// Function to delete service
function deleteService(serviceId) {
    if (confirm('Are you sure you want to delete this service?')) {
        fetch(`/manager/services/${serviceId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove the service row from the table
                document.querySelector(`tr[data-service-id="${serviceId}"]`).remove();
            } else {
                alert(data.error || 'Error deleting service');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Function to toggle service status
function toggleServiceStatus(serviceId) {
    fetch(`/manager/services/${serviceId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the switch state if needed
            const switchElement = document.querySelector(`tr[data-service-id="${serviceId}"] .form-check-input`);
            switchElement.checked = data.is_active;
        } else {
            alert(data.error || 'Error toggling service status');
        }
    })
    .catch(error => console.error('Error:', error));
} 