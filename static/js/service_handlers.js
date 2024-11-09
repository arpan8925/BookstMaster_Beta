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