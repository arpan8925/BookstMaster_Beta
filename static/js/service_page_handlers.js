document.addEventListener('DOMContentLoaded', function() {
    // Search and Filter Handlers
    const searchInput = document.getElementById('serviceSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const providerFilter = document.getElementById('providerFilter');
    const statusFilter = document.getElementById('statusFilter');

    // Add event listeners for real-time filtering
    if (searchInput) {
        searchInput.addEventListener('input', filterServices);
    }
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterServices);
    }
    if (providerFilter) {
        providerFilter.addEventListener('change', filterServices);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', filterServices);
    }

    // Filter function
    function filterServices() {
        const searchTerm = searchInput.value.toLowerCase();
        const category = categoryFilter.value.toLowerCase();
        const provider = providerFilter.value;
        const status = statusFilter.value;
        
        const rows = document.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const id = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const providerCell = row.querySelector('td:nth-child(3)');
            const providerId = providerCell.getAttribute('data-provider-id');
            const categoryName = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
            const serviceStatus = row.querySelector('.form-check-input').checked ? 'active' : 'inactive';
            
            const matchesSearch = id.includes(searchTerm) || 
                                name.includes(searchTerm) || 
                                providerCell.textContent.toLowerCase().includes(searchTerm) ||
                                categoryName.includes(searchTerm);
                                
            const matchesCategory = !category || categoryName === category;
            const matchesProvider = !provider || providerId === provider;
            const matchesStatus = !status || serviceStatus === status.toLowerCase();
            
            row.style.display = matchesSearch && matchesCategory && matchesProvider && matchesStatus ? '' : 'none';
        });
    }

    // Add search button click handler
    const searchButton = document.querySelector('.input-group .btn-primary');
    if (searchButton) {
        searchButton.addEventListener('click', filterServices);
    }

    // Add keyboard enter key handler for search
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterServices();
            }
        });
    }
});

// Keep your existing form handlers and other functionality