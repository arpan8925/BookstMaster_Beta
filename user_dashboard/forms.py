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