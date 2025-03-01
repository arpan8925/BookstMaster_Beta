# user_dashboard/templatetags/order_filters.py

from django import template

register = template.Library()

@register.filter(name='status_class')
def status_class(status):
    status_mapping = {
        'completed': 'success',
        'pending': 'warning',
        'processing': 'info',
        'canceled': 'danger',
    }
    return status_mapping.get(status.lower(), 'secondary')