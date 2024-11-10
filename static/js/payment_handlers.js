document.getElementById('addPaymentMethodForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form data and log it
    const formData = new FormData(this);
    console.log('Form Data:');
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('CSRF Token:', csrftoken);

    fetch('/manager/settings/payment-methods/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'success') {
            alert('Payment method added successfully!');
            location.reload();
        } else {
            alert(data.message || 'Error adding payment method');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding payment method');
    });
});

// Show/hide API credentials based on payment type
document.querySelector('select[name="type"]').addEventListener('change', function() {
    const apiCredentials = document.querySelector('.api-credentials');
    apiCredentials.style.display = this.value === 'automatic' ? 'block' : 'none';
    console.log('Payment type changed to:', this.value);
});

function togglePaymentMethod(id) {
    fetch(`/manager/settings/payment-methods/${id}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Payment method status toggled successfully');
        } else {
            alert(data.message || 'Error toggling payment method status');
            // Revert the toggle if there was an error
            const toggle = document.querySelector(`input[onchange="togglePaymentMethod(${id})"]`);
            toggle.checked = !toggle.checked;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error toggling payment method status');
    });
}

function deletePaymentMethod(id) {
    if (confirm('Are you sure you want to delete this payment method?')) {
        fetch(`/manager/settings/payment-methods/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert(data.message || 'Error deleting payment method');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting payment method');
        });
    }
}

function editPaymentMethod(id) {
    console.log('Editing payment method:', id);
    
    // Fetch payment method details
    fetch(`/manager/settings/payment-methods/${id}/get/`)
        .then(response => response.json())
        .then(data => {
            console.log('Payment method data:', data);
            
            // Populate the edit form
            document.getElementById('edit_method_id').value = id;
            document.getElementById('edit_name').value = data.name;
            document.getElementById('edit_type').value = data.type;
            document.getElementById('edit_min_amount').value = data.min_amount;
            document.getElementById('edit_max_amount').value = data.max_amount;
            document.getElementById('edit_fee_type').value = data.fee_type;
            document.getElementById('edit_fee_amount').value = data.fee_percentage;
            document.getElementById('edit_is_active').checked = data.is_active;
            document.getElementById('edit_test_mode').checked = data.test_mode;
            
            // Show the modal
            new bootstrap.Modal(document.getElementById('editPaymentMethodModal')).show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error fetching payment method details');
        });
}

// Add edit form submit handler
document.getElementById('editPaymentMethodForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const methodId = formData.get('method_id');
    
    console.log('Submitting edit form for method:', methodId);
    console.log('Form data:', Object.fromEntries(formData));
    
    fetch(`/manager/settings/payment-methods/${methodId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response:', data);
        if (data.status === 'success') {
            location.reload();
        } else {
            alert(data.message || 'Error updating payment method');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating payment method');
    });
}); 