from django.contrib import admin
from .models import PurchaseData, PurchaseEmissionFactor


@admin.register(PurchaseEmissionFactor)
class PurchaseEmissionFactorAdmin(admin.ModelAdmin):
    """
    Interface admin pour les facteurs d'émission des achats.
    """
    list_display = ('category_label', 'category_code', 'factor_kg_co2_per_keur', 'source')
    search_fields = ('category_label', 'category_code')
    ordering = ('category_label',)


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
        """Affiche une version courte de la description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
