from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth import get_user_model

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=False,  # Can be empty if not provided
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=False,  # Can be empty if not provided
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,  # Can be empty if not provided
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        required=False,  # Can be empty if not provided
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    # Optional fields
    role = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'value': 'user'})  # Default role as 'user'
    )
    login_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'value': ''})  # Default empty
    )
    timezone = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'value': ''})  # Default empty
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'profile_picture', 'first_name', 'last_name', 'address', 'city', 'password1', 'password2', 'role', 'login_type', 'timezone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.address = self.cleaned_data['address']
        user.city = self.cleaned_data['city']
        user.phone = self.cleaned_data['phone']
        
        # Auto-generate values for fields that are hidden or not manually provided
        user.role = self.cleaned_data.get('role', 'user')  # Default to 'user'
        user.login_type = self.cleaned_data.get('login_type', '')
        user.timezone = self.cleaned_data.get('timezone', '')
        
        if commit:
            user.save()
        return user


User = get_user_model()

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    # Explicitly set the model for AuthenticationForm
    class Meta:
        model = User
        fields = ['username', 'password']

