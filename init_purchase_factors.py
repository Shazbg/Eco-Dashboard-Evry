#!/usr/bin/env python
"""Script pour initialiser les facteurs d'émission pour les achats."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.purchases.models import PurchaseEmissionFactor

factors = [
    {'category_code': 'food_service', 'category_label': 'Restauration & Services légers', 'factor_kg_co2_per_keur': 100.00},
    {'category_code': 'insurance', 'category_label': 'Assurances & Cotisations', 'factor_kg_co2_per_keur': 110.00},
    {'category_code': 'it_telecom', 'category_label': 'IT & Téléphonie', 'factor_kg_co2_per_keur': 160.00},
    {'category_code': 'cleaning_maintenance', 'category_label': 'Nettoyage & Entretien & Espaces verts', 'factor_kg_co2_per_keur': 215.00},
    {'category_code': 'activities', 'category_label': 'Séjours & Activités', 'factor_kg_co2_per_keur': 270.00},
    {'category_code': 'laundry', 'category_label': 'Blanchisserie', 'factor_kg_co2_per_keur': 320.00},
    {'category_code': 'construction', 'category_label': 'Travaux & Construction', 'factor_kg_co2_per_keur': 360.00},
    {'category_code': 'transport', 'category_label': 'Transports', 'factor_kg_co2_per_keur': 560.00},
    {'category_code': 'equipment_rental', 'category_label': 'Location équipements', 'factor_kg_co2_per_keur': 600.00},
]

created = 0
for f in factors:
    obj, was_created = PurchaseEmissionFactor.objects.get_or_create(
        category_code=f['category_code'],
        defaults={
            'category_label': f['category_label'],
            'factor_kg_co2_per_keur': f['factor_kg_co2_per_keur'],
            'source': 'Excel Achats 30% - ADEME'
        }
    )
    if was_created:
        created += 1
        print(f"✓ Créé: {obj.category_label} ({obj.factor_kg_co2_per_keur} kgCO2e/k€)")
    else:
        print(f"  Existe: {obj.category_label}")

print(f"\n✅ {created} facteurs créés, {len(factors)-created} existants")
print(f"Total en base: {PurchaseEmissionFactor.objects.count()}")
