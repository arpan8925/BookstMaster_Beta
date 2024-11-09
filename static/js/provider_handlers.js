// Provider form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const addProviderForm = document.getElementById('addProviderForm');
    if (addProviderForm) {
        addProviderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
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
                console.error('Error:', error);
                alert('Error creating provider');
            });
        });
    }
});

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