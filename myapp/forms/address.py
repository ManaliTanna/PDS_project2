from django import forms
from ..models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['apt_number', 'street_name', 'city', 'state', 'country', 'zip_code', 'latitude', 'longitude']
        widgets = {
            'apt_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment Number'}),
            'street_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude'}),
        }
