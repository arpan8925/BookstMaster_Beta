// Provider form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const addProviderForm = document.getElementById('addProviderForm');
    if (addProviderForm) {
        addProviderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoader('Creating provider...');
            
            const formData = new FormData(this);
            
            // Add is_active value from switch
            const isActiveSwitch = document.querySelector('input[name="is_active"]');
            formData.set('is_active', isActiveSwitch.checked ? 'on' : 'off');
            
            fetch('/manager/providers/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addProviderModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Reload page to show new provider
                    location.reload();
                } else {
                    alert(data.error || 'Error creating provider');
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                alert('Error creating provider');
            });
        });
    }

    // Edit Provider
    window.editProvider = function(providerId) {
        showLoader('Loading provider information...');
        
        fetch(`/manager/providers/${providerId}/get-info/`)
            .then(response => response.json())
            .then(data => {
                hideLoader();
                document.getElementById('edit_provider_id').value = providerId;
                document.getElementById('edit_name').value = data.name;
                document.getElementById('edit_api_url').value = data.api_url;
                document.getElementById('edit_api_key').value = data.api_key;
                document.getElementById('edit_description').value = data.description || '';
                document.getElementById('edit_is_active').checked = data.is_active;
                
                new bootstrap.Modal(document.getElementById('editProviderModal')).show();
            })
            .catch(error => {
                hideLoader();
                alert('Error fetching provider information');
            });
    };

    // Edit Provider Form Handler
    const editProviderForm = document.getElementById('editProviderForm');
    if (editProviderForm) {
        editProviderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoader('Saving changes...');
            
            const formData = new FormData(this);
            const providerId = formData.get('provider_id');
            
            fetch(`/manager/providers/${providerId}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editProviderModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Reload page to show updated provider
                    location.reload();
                } else {
                    alert(data.error || 'Error updating provider');
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                alert('Error updating provider');
            });
        });
    }

    // Check Balance
    window.checkBalance = function(providerId) {
        showLoader('Checking balance...');
        
        fetch(`/manager/providers/${providerId}/check-balance/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (data.status === 'success') {
                // Update balance in UI
                const balanceElement = document.querySelector(`tr[data-provider-id="${providerId}"] .balance`);
                if (balanceElement) {
                    balanceElement.textContent = `$${parseFloat(data.balance).toFixed(2)}`;
                    // Add a flash effect to show the update
                    balanceElement.classList.add('balance-updated');
                    setTimeout(() => {
                        balanceElement.classList.remove('balance-updated');
                    }, 1000);
                }
            } else {
                alert(data.error || 'Error checking balance');
            }
        })
        .catch(error => {
            hideLoader();
            alert('Error checking balance');
        });
    };

    // Sync Services
    window.syncServices = function(providerId) {
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
            } else {
                alert(data.error || 'Error syncing services');
            }
        })
        .catch(error => {
            hideLoader();
            alert('Error syncing services');
        });
    };

    // View Services
    window.viewServices = function(providerId) {
        showLoader('Loading services...');
        window.location.href = `/manager/providers/${providerId}/services/`;
    };

    // Delete Provider
    window.deleteProvider = function(providerId) {
        if (confirm('Are you sure you want to delete this provider? This action cannot be undone.')) {
            showLoader('Deleting provider...');
            
            fetch(`/manager/providers/${providerId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert(data.error || 'Error deleting provider');
                }
            })
            .catch(error => {
                hideLoader();
                alert('Error deleting provider');
            });
        }
    };
});

// Loader functions
function showLoader(message = 'Please wait...') {
    const loader = document.createElement('div');
    loader.id = 'pageLoader';
    loader.innerHTML = `
        <div class="loader-overlay">
            <div class="loader-content">
                <div class="loader-spinner"></div>
                <p class="mt-2">${message}</p>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        loader.remove();
    }
}

// Helper function to get CSRF token
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