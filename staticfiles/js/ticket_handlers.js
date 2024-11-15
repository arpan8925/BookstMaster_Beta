let currentTicketId = null;

function viewTicket(ticketId) {
    currentTicketId = ticketId;
    fetch(`/manager/tickets/${ticketId}/view/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('view_ticket_subject').textContent = data.subject;
            document.getElementById('view_ticket_user').textContent = data.user_email;
            document.getElementById('view_ticket_created').textContent = data.created_at;
            document.getElementById('view_ticket_status').textContent = data.status;
            document.getElementById('view_ticket_priority').textContent = data.priority;
            document.getElementById('view_ticket_updated').textContent = data.updated_at || 'Never';
            document.getElementById('view_ticket_content').textContent = data.content;
            
            new bootstrap.Modal(document.getElementById('viewTicketModal')).show();
        });
}

function replyTicket(ticketId) {
    currentTicketId = ticketId;
    document.getElementById('replyTicketForm').action = `/manager/tickets/${ticketId}/reply/`;
    new bootstrap.Modal(document.getElementById('replyTicketModal')).show();
}

function closeTicket(ticketId) {
    if (confirm('Are you sure you want to close this ticket?')) {
        fetch(`/manager/tickets/${ticketId}/close/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert('Error closing ticket');
            }
        });
    }
}

// Add form submit handlers
document.addEventListener('DOMContentLoaded', function() {
    // Reply ticket form handler
    document.getElementById('replyTicketForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert(data.error || 'Error sending reply');
            }
        });
    });

    // Add ticket form handler
    const addTicketForm = document.getElementById('addTicketForm');
    if (addTicketForm) {
        addTicketForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Validate form data
            const user_id = formData.get('user_id');
            const subject = formData.get('subject');
            const content = formData.get('content');
            
            if (!user_id || !subject || !content) {
                alert('Please fill in all required fields');
                return;
            }
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addTicketModal'));
                    modal.hide();
                    
                    // Show success message
                    alert('Ticket created successfully');
                    
                    // Reload the page to show the new ticket
                    location.reload();
                } else {
                    alert(data.error || 'Error creating ticket');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating ticket');
            });
        });
    }
});

// Function to get CSRF token
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