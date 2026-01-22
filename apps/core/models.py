from django.db import models
from django.core.validators import URLValidator


class ADEMEConfiguration(models.Model):
    """
    Configuration singleton pour les mises à jour automatiques des facteurs ADEME.
    Cette configuration permet de gérer l'URL du CSV, les secteurs actifs et les notifications.
    """
    
    # URL du CSV ADEME
    csv_url = models.URLField(
        max_length=500,
        default="https://data.ademe.fr/data-fair/api/v1/datasets/base-carboner/data-files/Base_Carbone_V23.6.csv",
        verbose_name="URL du fichier CSV ADEME",
        help_text="URL officielle du fichier CSV Base Carbone de l'ADEME"
    )
    
    # Fréquence de mise à jour (en mois)
    update_frequency_months = models.IntegerField(
        default=6,
        verbose_name="Fréquence de mise à jour (mois)",
        help_text="Nombre de mois entre deux mises à jour automatiques"
    )
    
    # Dernière mise à jour
    last_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière mise à jour",
        help_text="Date et heure de la dernière mise à jour réussie"
    )
    
    # Version du CSV
    csv_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Version du CSV",
        help_text="Version du CSV ADEME actuellement utilisée (ex: V23.6)"
    )
    
    # Email de notification
    notification_email = models.EmailField(
        blank=True,
        verbose_name="Email de notification",
        help_text="Adresse email pour recevoir les notifications de mise à jour"
    )
    
    # Activer notifications
    enable_notifications = models.BooleanField(
        default=True,
        verbose_name="Activer les notifications",
        help_text="Envoyer un email après chaque mise à jour"
    )
    
    # Secteurs à importer
    SECTORS_CHOICES = [
        ('vehicles', 'Véhicules'),
        ('buildings', 'Bâtiments & Énergies'),
        ('food', 'Alimentation'),
        ('purchases', 'Achats'),
    ]
    
    active_sectors = models.JSONField(
        default=list,
        verbose_name="Secteurs actifs",
        help_text="Liste des secteurs pour lesquels importer les facteurs d'émission"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    class Meta:
        verbose_name = "Configuration ADEME"
        verbose_name_plural = "Configuration ADEME"
    
    def __str__(self):
        return f"Configuration ADEME (dernière MAJ: {self.last_update or 'jamais'})"
    
    def save(self, *args, **kwargs):
        """
        Forcer un seul objet de configuration (singleton pattern).
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Empêcher la suppression de la configuration.
        """
        pass
    
    @classmethod
    def get_config(cls):
        """
        Récupérer ou créer la configuration unique.
        """
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'active_sectors': ['vehicles']  # Par défaut, seulement véhicules
            }
        )
        return config
    
    @property
    def is_update_needed(self):
        """
        Vérifie si une mise à jour est nécessaire selon la fréquence configurée.
        """
        if not self.last_update:
            return True
        
        from datetime import timedelta
        from django.utils import timezone
        
        next_update = self.last_update + timedelta(days=30 * self.update_frequency_months)
        return timezone.now() >= next_update
    
    @property
    def sectors_display(self):
        """
        Retourne les noms complets des secteurs actifs.
        """
        sectors_dict = dict(self.SECTORS_CHOICES)
        return [sectors_dict.get(sector, sector) for sector in self.active_sectors]
