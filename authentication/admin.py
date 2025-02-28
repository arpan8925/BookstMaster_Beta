from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'ids', 'role', 'username', 'email', 'status', 'created', 'changed')  # Fields to display in the list view
    search_fields = ('first_name', 'last_name', 'email')  # Fields to search by in the admin panel
    list_filter = ('role', 'status')  # Filters to add on the right side of the admin panel for easier searching
    ordering = ('-created',)  # Order users by created date in descending order by default
    fields = ('ids', 'role', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'password', 'balance', 'custom_rate', 'level', 'status', 'created', 'changed')  # Fields to display on the edit form
    readonly_fields = ('ids', 'created', 'changed')  # Make the 'created' and 'changed' fields read-only

    # Optionally, you can customize the form layout, inline models, or add any other customization here

# Register the model with the admin interface
admin.site.register(User, UserAdmin)
