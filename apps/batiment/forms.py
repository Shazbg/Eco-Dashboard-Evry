from django import forms
from .models import BuildingEnergyData
import datetime

class BuildingEnergyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default year to current year if not bound
        if not self.is_bound and not self.instance.pk:
            self.initial['year'] = datetime.datetime.now().year
            
        # Clear default '0' values to ensure placeholders show up
        defaults_to_clear = [
            'surface_area', 'electricity_kwh', 'gas_kwh', 
            'heating_network_kwh', 'cooling_kwh', 'photovoltaic_production_kwh'
        ]
        for field in defaults_to_clear:
            if self.initial.get(field) == 0:
                self.initial[field] = None

    class Meta:
        model = BuildingEnergyData
        fields = [
            "year", "site_name", "surface_area", "construction_year",
            "electricity_kwh", "gas_kwh",
            "heating_network_kwh", "cooling_kwh",
            "photovoltaic_production_kwh",
            "notes",
        ]
        widgets = {
            "year": forms.NumberInput(attrs={"class": "form-input"}),
            "site_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ex: Mairie annexe"}),
            "surface_area": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "construction_year": forms.NumberInput(attrs={"class": "form-input", "placeholder": "Ex: 1990"}),
            "electricity_kwh": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "gas_kwh": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "heating_network_kwh": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "cooling_kwh": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "photovoltaic_production_kwh": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Commentaires optionnels..."}),
        }

    def clean(self):
        cleaned = super().clean()
        # Verify positive values for consumptions
        energy_fields = [
            "electricity_kwh", "gas_kwh", 
            "heating_network_kwh", "cooling_kwh", 
            "photovoltaic_production_kwh"
        ]
        for f in energy_fields:
            v = cleaned.get(f)
            if v is not None and v < 0:
                self.add_error(f, "La valeur doit être positive.")
        return cleaned
