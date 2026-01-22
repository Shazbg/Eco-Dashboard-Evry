from django import forms
from .models import PurchaseData


class PurchaseDataForm(forms.ModelForm):
    """
    Formulaire de saisie des données d'achats.
    """
    
    class Meta:
        model = PurchaseData
        fields = ['year', 'service', 'category', 'description', 'amount_euros', 'notes']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '2026',
                'min': '2020',
                'max': '2030'
            }),
            'service': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Direction des Services Techniques'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Nettoyage des offices de restauration scolaire'
            }),
            'amount_euros': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '15000.00',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Notes ou commentaires (optionnel)'
            }),
        }
    
    def clean_amount_euros(self):
        """Validation du montant."""
        amount = self.cleaned_data.get('amount_euros')
        if amount and amount <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return amount
