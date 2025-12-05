from django import forms
from .models import FraudAlert

class TransactionForm(forms.ModelForm):
    class Meta:
        model = FraudAlert
        # These fields MUST exist in models.py
        fields = ['customer_name', 'vehicle_number', 'transaction_id', 
                  'fuel_dispensed', 'bill_amount', 'payment_screenshot', 'pump_image']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'fuel_dispensed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bill_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_screenshot': forms.FileInput(attrs={'class': 'form-control'}),
            'pump_image': forms.FileInput(attrs={'class': 'form-control'}),
        }