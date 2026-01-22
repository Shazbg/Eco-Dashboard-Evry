from django.contrib import admin
from .models import PurchaseData


@admin.register(PurchaseData)
class PurchaseDataAdmin(admin.ModelAdmin):
    """
    Interface admin pour les données d'achats.
    """
    
    list_display = ('year', 'category', 'description_short', 'amount_euros', 'total_co2_kg', 'user', 'created_at')
    list_filter = ('year', 'category', 'user')
    search_fields = ('description', 'service', 'notes')
    readonly_fields = ('emission_factor', 'total_co2_kg', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Métadonnées', {
            'fields': ('user', 'year', 'service')
        }),
        ('Données d\'achat', {
            'fields': ('category', 'description', 'amount_euros')
        }),
        ('Impact carbone', {
            'fields': ('emission_factor', 'total_co2_kg'),
            'description': 'Calculés automatiquement'
        }),
        ('Informations complémentaires', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        """Affiche une version cour

te de la description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
