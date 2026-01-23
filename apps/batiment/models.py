from django.conf import settings
from django.db import models

class BuildingEnergyData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(verbose_name="Année")
    site_name = models.CharField(max_length=200, default="Site inconnu", verbose_name="Nom du site")
    surface_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="m²", verbose_name="Surface (m²)")
    construction_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Année de construction")
    
    # Energy Consumptions
    electricity_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Électricité (kWh)")
    gas_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Gaz Naturel (kWh)")
    heating_network_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Réseau de chaleur (kWh)")
    cooling_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Climatisation (kWh)")
    photovoltaic_production_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Production PV (kWh)")

    # Factors (kgCO2e / kWh) stored for historical record
    electricity_factor = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    gas_factor = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    heating_network_factor = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    cooling_factor = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    total_co2_kg = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    def compute_total(self):
        # Calculation: sum(consumption * factor)
        # Note: Photovoltaic production is tracked but does not subtract from footprint in this simplified mode
        total = (self.electricity_kwh * self.electricity_factor) + \
                (self.gas_kwh * self.gas_factor) + \
                (self.heating_network_kwh * self.heating_network_factor) + \
                (self.cooling_kwh * self.cooling_factor)
        return total

    def save(self, *args, **kwargs):
        self.total_co2_kg = self.compute_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.year} - {self.site_name} ({self.total_co2_kg} kgCO2e)"
