from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    is_vendor = forms.BooleanField(
        required=False,
        label="Register as Vendor"
    )

    class Meta(UserCreationForm.Meta): # Inheriting Meta is best practice here
        model = User
        # Removed password1 and password2!
        fields = ['username', 'email', 'is_vendor'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
from django import forms
from .models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Fields the user is allowed to edit
        fields = ['full_name', 'email', 'phone_number', 'address'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);'
            })