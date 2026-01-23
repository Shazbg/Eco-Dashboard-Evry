from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class PurchaseEmissionFactor(models.Model):
    """
    Facteur d'émission modifiable pour une catégorie d'achat.
    Valeurs en kgCO2e par millier d'euros (kgCO2e/k€).
    """
    category_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code catégorie"
    )
    category_label = models.CharField(
        max_length=200,
        verbose_name="Libellé catégorie"
    )
    factor_kg_co2_per_keur = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Facteur d'émission (kgCO2e/k€)",
        help_text="kg CO2e par millier d'euros dépensés"
    )
    source = models.CharField(
        max_length=300,
        default="Excel Achats 30% - ADEME",
        verbose_name="Source"
    )
    
    class Meta:
        verbose_name = "Facteur d'émission achat"
        verbose_name_plural = "Facteurs d'émission achats"
        ordering = ['category_label']
    
    def __str__(self):
        return f"{self.category_label} ({self.factor_kg_co2_per_keur} kgCO2e/k€)"


class PurchaseData(models.Model):
    """
    Données d'achats/marchés municipaux avec calcul de l'empreinte carbone.
    """
    
    # Catégories d'achats (pour compatibilité avec formulaire)
    CATEGORY_CHOICES = [
        ('food_service', 'Restauration & Services légers'),
        ('insurance', 'Assurances & Cotisations'),
        ('it_telecom', 'IT & Téléphonie'),
        ('cleaning_maintenance', 'Nettoyage & Entretien & Espaces verts'),
        ('activities', 'Séjours & Activités'),
        ('laundry', 'Blanchisserie'),
        ('construction', 'Travaux & Construction'),
        ('transport', 'Transports'),
        ('equipment_rental', 'Location équipements'),
    ]
    
    # Métadonnées
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    
    year = models.IntegerField(
        default=2026,
        verbose_name="Année"
    )
    
    service = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Service/Direction",
        help_text="Service ou direction concerné"
    )
    
    # Données d'achat
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Catégorie d'achat"
    )
    
    description = models.CharField(
        max_length=500,
        verbose_name="Description du marché/service",
        help_text="Description détaillée du marché ou service"
    )
    
    amount_euros = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (€)",
        help_text="Montant total en euros"
    )
    
    # Facteur d'émission (récupéré depuis PurchaseEmissionFactor)
    emission_factor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Facteur d'émission (kgCO2e/k€)",
        help_text="Facteur automatique selon la catégorie"
    )
    
    # Impact carbone (calculé automatiquement)
    total_co2_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Total CO₂ (kg)",
        help_text="Impact carbone total calculé"
    )
    
    # Notes optionnelles
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Notes ou commentaires additionnels"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    class Meta:
        verbose_name = "Donnée d'achat"
        verbose_name_plural = "Données d'achats"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.description[:50]} ({self.year})"
    
    def save(self, *args, **kwargs):
        """
        Calcul automatique du facteur d'émission et du CO₂ total.
        """
        # Récupérer le facteur d'émission depuis la base de données
        try:
            factor_obj = PurchaseEmissionFactor.objects.get(category_code=self.category)
            self.emission_factor = factor_obj.factor_kg_co2_per_keur
        except PurchaseEmissionFactor.DoesNotExist:
            # Fallback sur valeurs par défaut si facteur non trouvé
            default_factors = {
                'food_service': Decimal('100.00'),
                'insurance': Decimal('110.00'),
                'it_telecom': Decimal('160.00'),
                'cleaning_maintenance': Decimal('215.00'),
                'activities': Decimal('270.00'),
                'laundry': Decimal('320.00'),
                'construction': Decimal('360.00'),
                'transport': Decimal('560.00'),
                'equipment_rental': Decimal('600.00'),
            }
            self.emission_factor = default_factors.get(self.category, Decimal('0.00'))
        
        # Calculer le CO₂ total : (montant / 1000) × facteur
        if self.amount_euros and self.emission_factor:
            amount_in_keuros = self.amount_euros / Decimal('1000.00')
            self.total_co2_kg = amount_in_keuros * self.emission_factor
        
        super().save(*args, **kwargs)
    
    @property
    def total_co2_tons(self):
        """Retourne le CO₂ en tonnes."""
        if self.total_co2_kg:
            return self.total_co2_kg / Decimal('1000.00')
        return Decimal('0.00')
