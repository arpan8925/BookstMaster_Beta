// Category form submission handler
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('categorySearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterCategories();
        });
    }

    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterCategories();
        });
    }

    // Add Category Form Handler
    const addCategoryForm = document.getElementById('addCategoryForm');
    if (addCategoryForm) {
        addCategoryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoader('Creating category...');
            
            const formData = new FormData(this);
            const isActiveSwitch = document.querySelector('input[name="is_active"]');
            formData.set('is_active', isActiveSwitch.checked ? 'on' : 'off');
            
            fetch('/manager/categories/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Reload page to show new category
                    location.reload();
                } else {
                    alert(data.error || 'Error creating category');
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                alert('Error creating category');
            });
        });
    }

    // Edit Category Form Handler
    const editCategoryForm = document.getElementById('editCategoryForm');
    if (editCategoryForm) {
        editCategoryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            showLoader('Saving changes...');
            
            const formData = new FormData(this);
            const categoryId = formData.get('category_id');
            
            fetch(`/manager/categories/${categoryId}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Reload page to show updated category
                    location.reload();
                } else {
                    alert(data.error || 'Error updating category');
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                alert('Error updating category');
            });
        });
    }
});

// Edit Category
window.editCategory = function(categoryId) {
    showLoader('Loading category information...');
    
    fetch(`/manager/categories/get-info/${categoryId}/`)
        .then(response => response.json())
        .then(data => {
            hideLoader();
            document.getElementById('edit_category_id').value = categoryId;
            document.getElementById('edit_name').value = data.name;
            document.getElementById('edit_description').value = data.description || '';
            document.getElementById('edit_is_active').checked = data.is_active;
            
            new bootstrap.Modal(document.getElementById('editCategoryModal')).show();
        })
        .catch(error => {
            hideLoader();
            alert('Error fetching category information');
        });
};

// Delete Category
window.deleteCategory = function(categoryId) {
    if (confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
        showLoader('Deleting category...');
        
        fetch(`/manager/categories/${categoryId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (data.status === 'success') {
                location.reload();
            } else {
                alert(data.error || 'Error deleting category');
            }
        })
        .catch(error => {
            hideLoader();
            alert('Error deleting category');
        });
    }
};

// Toggle Category Status
window.toggleCategoryStatus = function(categoryId) {
    showLoader('Updating status...');
    
    fetch(`/manager/categories/${categoryId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.status === 'success') {
            // No need to reload, the switch will update automatically
        } else {
            alert(data.error || 'Error updating status');
            // Revert the switch if there was an error
            const switchElement = document.querySelector(`input[onchange="toggleCategoryStatus(${categoryId})"]`);
            if (switchElement) {
                switchElement.checked = !switchElement.checked;
            }
        }
    })
    .catch(error => {
        hideLoader();
        alert('Error updating status');
        // Revert the switch on error
        const switchElement = document.querySelector(`input[onchange="toggleCategoryStatus(${categoryId})"]`);
        if (switchElement) {
            switchElement.checked = !switchElement.checked;
        }
    });
};

// Filter categories function
function filterCategories() {
    const searchTerm = document.getElementById('categorySearch').value.toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const rows = document.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const description = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const isActive = row.querySelector('.form-check-input').checked;

        const matchesSearch = name.includes(searchTerm) || description.includes(searchTerm);
        const matchesStatus = status === '' || 
            (status === 'active' && isActive) || 
            (status === 'inactive' && !isActive);

        row.style.display = matchesSearch && matchesStatus ? '' : 'none';
    });
}

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