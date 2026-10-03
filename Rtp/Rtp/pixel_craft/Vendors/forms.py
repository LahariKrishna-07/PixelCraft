from django import forms
from .models import Vendor, InventoryItem, Components

# 1. FORM FOR EDITING VENDOR PROFILE
class VendorProfileEditForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'shop_name', 
            'owner_name', 
            'phone', 
            'email', 
            'address', 
            'city', 
            'profile_image'
        ]
        
        widgets = {
            'shop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'placeholder': 'Enter your shop name'
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'placeholder': 'Enter owner name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'placeholder': '+1 (555) 000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'placeholder': 'shop@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'rows': 3,
                'placeholder': 'Full street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;',
                'placeholder': 'City'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
            }),
        }

# 2. FORM FOR ADDING NEW COMPONENTS (Unified Form)
class AddComponentFullForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'e.g. RTX 4090', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    brand = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'e.g. ASUS', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    category = forms.ChoiceField(choices=Components.CATEGORY_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control', 
        'rows': 2, 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={
        'class': 'form-control', 
        'placeholder': '0.00', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))
    stock_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Quantity', 
        'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
    }))

# 3. FORM FOR EDITING EXISTING INVENTORY (Fixes your ImportError)
class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['price', 'stock_quantity', 'is_active']
        widgets = {
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }