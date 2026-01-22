from django.contrib import admin
from .models import ADEMEConfiguration


@admin.register(ADEMEConfiguration)
class ADEMEConfigurationAdmin(admin.ModelAdmin):
    """
    Interface admin pour la configuration ADEME.
    """
    
    fieldsets = (
        ('Source des données', {
            'fields': ('csv_url', 'csv_version'),
            'description': 'URL et version du fichier CSV ADEME Base Carbone'
        }),
        ('Paramètres de mise à jour', {
            'fields': ('update_frequency_months', 'last_update', 'active_sectors'),
            'description': 'Fréquence de mise à jour et secteurs actifs'
        }),
        ('Notifications', {
            'fields': ('enable_notifications', 'notification_email'),
            'description': 'Configuration des notifications par email'
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('last_update', 'csv_version', 'created_at', 'updated_at')
    
    list_display = ('__str__', 'csv_version', 'update_frequency_months', 'enable_notifications')
    
    def has_add_permission(self, request):
        """
        Empêcher création de multiples configurations (singleton).
        """
        return not ADEMEConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """
        Empêcher suppression de la configuration.
        """
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Personnaliser le formulaire pour afficher les choix de secteurs.
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Ajouter un widget pour active_sectors avec checkboxes
        if 'active_sectors' in form.base_fields:
            form.base_fields['active_sectors'].help_text = (
                'Sélectionnez les secteurs pour lesquels importer les facteurs ADEME. '
                'Format JSON, exemple: ["vehicles", "buildings"]'
            )
        
        return form
