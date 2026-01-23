from django.contrib import admin
from .models import BuildingEnergyData

@admin.register(BuildingEnergyData)
class BuildingEnergyDataAdmin(admin.ModelAdmin):
    """
    Interface admin pour les données énergétiques des bâtiments.
    """
    list_display = ('year', 'site_name', 'surface_area', 'total_kwh', 'total_co2_kg', 'user', 'created_at')
    list_filter = ('year', 'user')
    search_fields = ('site_name', 'notes')
    readonly_fields = ('total_co2_kg', 'created_at')
    
    fieldsets = (
        ('Identification', {
            'fields': ('user', 'year', 'site_name', 'surface_area', 'construction_year')
        }),
        ('Consommations énergétiques (kWh)', {
            'fields': ('electricity_kwh', 'gas_kwh', 'heating_network_kwh', 'cooling_kwh', 'photovoltaic_production_kwh')
        }),
        ('Facteurs dé mission (kgCO2e/kWh)', {
            'fields': ('electricity_factor', 'gas_factor', 'heating_network_factor', 'cooling_factor'),
            'description': 'Facteurs ADEME pour le calcul CO2'
        }),
        ('Impact carbone', {
            'fields': ('total_co2_kg',),
            'description': 'Calculé automatiquement'
        }),
        ('Informations complémentaires', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_kwh(self, obj):
        """Affiche la consommation totale en kWh."""
        total = obj.electricity_kwh + obj.gas_kwh + obj.heating_network_kwh + obj.cooling_kwh
        return f"{total:,.0f} kWh"
    total_kwh.short_description = 'Conso. totale'
