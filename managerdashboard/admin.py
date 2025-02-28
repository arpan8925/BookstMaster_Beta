from django.contrib import admin
from .models import ServiceCategory, Service, PaymentMethod, Transactions
from django import forms
from django.utils.html import format_html

class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'status', 'created', 'changed', 'sort')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cate_id', 'price', 'status', 'add_type', 'dripfeed')
    list_filter = ('status', 'add_type', 'cate_id')
    search_fields = ('name', 'cate_id__name', 'api_service_id')
    readonly_fields = ('id', 'ids', 'created', 'changed')
    raw_id_fields = ('cate_id',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'ids', 'cate_id', 'min', 'max')
        }),
        ('Service Details', {
            'fields': (
                'name', 'desc', 
                ('price', 'original_price')
            )
        }),
        ('Service Configuration', {
            'fields': (
                'add_type', 'type',
                'api_service_id', 'api_provider_id',
                'dripfeed', 'status'
            )
        }),
        ('Timestamps', {
            'fields': ('created', 'changed'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cate_id')

admin.site.register(ServiceCategory, ServiceCategoryAdmin)



class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        widgets = {
            'client_id': forms.PasswordInput(render_value=True),
            'client_secret': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        cleaned_data = super().clean()
        fee_type = cleaned_data.get('fee_type')
        fee_percentage = cleaned_data.get('fee_percentage')
        fee_fixed = cleaned_data.get('fee_fixed')

        # Validate fee fields based on fee type
        if fee_type == 'percentage' and (fee_percentage is None or fee_percentage <= 0):
            raise forms.ValidationError("Percentage fee must be greater than 0 when using percentage fee type")
        if fee_type == 'fixed' and (fee_fixed is None or fee_fixed <= 0):
            raise forms.ValidationError("Fixed fee must be greater than 0 when using fixed amount fee type")


        return cleaned_data

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    form = PaymentMethodForm
    list_display = ('name', 'type', 'is_active', 'test_mode', 'min_amount', 'icon_preview')
    list_filter = ('is_active', 'test_mode', 'type', 'fee_type')
    search_fields = ('name', 'client_id')
    readonly_fields = ('created_at', 'updated_at', 'icon_preview')
    fieldsets = (
        (None, {
            'fields': (
                'name', 'type', 'is_active', 'test_mode', 'icon', 'min_amount', 'exchng_rate', 'fee_type', 'desc'
            )
        }),
        ('Fee Configuration', {
            'fields': (
                ('fee_percentage', 'fee_fixed'),
            ),
            'classes': ('collapse',)
        }),
        ('API Credentials', {
            'fields': ('client_id', 'client_secret'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.icon.url)
        return "No icon uploaded"
    icon_preview.short_description = 'Icon Preview'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # Hide timestamps when creating new object
            fieldsets = [fieldset for fieldset in fieldsets if fieldset[0] != 'Timestamps']
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj:  # Hide preview when creating new object
            return [f for f in readonly_fields if f != 'icon_preview']
        return readonly_fields
    

class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'uid', 'amount', 'status', 'payment_method', 'created', 'updated')
    list_filter = ('status', 'payment_method', 'created')
    search_fields = ('transaction_id', 'uid__email')  # Allow searching by email
    actions = ['mark_as_completed']

    # Define action to mark the transaction as completed
    def mark_as_completed(self, request, queryset):
        updated_count = queryset.update(status='completed')
        self.message_user(request, f'{updated_count} transactions marked as completed.')
        
        # Update the user's balance after marking completed
        for transaction in queryset:
            user = transaction.uid
            user.balance += transaction.total_amount
            user.save()

    mark_as_completed.short_description = 'Mark selected transactions as completed'

admin.site.register(Transactions, TransactionsAdmin)