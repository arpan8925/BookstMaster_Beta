// Service form submission handler
document.addEventListener('DOMContentLoaded', function() {
    // Add Service Form Handler
    const addServiceForm = document.getElementById('addServiceForm');
    if (addServiceForm) {
        addServiceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const isActiveSwitch = document.querySelector('input[name="is_active"]');
            const isDripFeedSwitch = document.querySelector('input[name="is_drip_feed"]');
            
            formData.set('is_active', isActiveSwitch.checked ? 'on' : 'off');
            formData.set('is_drip_feed', isDripFeedSwitch.checked ? 'on' : 'off');
            
            // Debug log
            console.log('Submitting form...');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
            
            fetch('/manager/services/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.status === 'success') {
                    alert(data.message);
                    window.location.reload();
                } else {
                    alert(data.error || 'Error creating service');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating service');
            });
        });
    }
}); 