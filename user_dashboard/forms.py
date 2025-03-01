from django import forms
from managerdashboard.models import PaymentMethod

class AddFundsForm(forms.Form):
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),  # Set in __init__
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
            'id': 'paymentMethod'
        })
    )
    amount = forms.DecimalField(
        min_value=10,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'USD',
            'id': 'amount',
            'min': '0'
        })
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'termsCheck'
        })
    )

    def __init__(self, *args, **kwargs):
        payment_methods = kwargs.pop('payment_methods', None)
        super().__init__(*args, **kwargs)
        if payment_methods is not None:
            self.fields['payment_method'].queryset = payment_methods


class OrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super().__init__(*args, **kwargs)
        
        # Set category choices
        category_choices = [('', 'Select a category')]
        if categories:
            category_choices += [
                (str(cat_id), cat_data['name'])  # Ensure string IDs
                for cat_id, cat_data in categories.items()
            ]
        self.fields['category'].choices = category_choices

        if self.is_bound:
            self.fields['quantity'].initial = self.data.get('quantity')

    category = forms.ChoiceField(
        label="Category",
        widget=forms.Select(attrs={
            'id': 'categorySelect',
            'class': 'form-select'
        })
    )
    
    service = forms.CharField(
        label="Service",
        widget=forms.Select(attrs={'id': 'serviceSelect', 'class': 'form-select'})
    )
    
    link = forms.CharField(
        label="Link",
        widget=forms.TextInput(attrs={
            'id': 'linkInput',
            'class': 'form-control',
            'placeholder': 'Enter link'
        })
    )
    
    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,  # Add basic validation
        error_messages={
            'required': 'Please enter quantity',
            'min_value': 'Quantity must be at least 1'
        }
    )