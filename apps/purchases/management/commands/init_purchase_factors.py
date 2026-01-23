from django.core.management.base import BaseCommand
from apps.purchases.models import PurchaseEmissionFactor


class Command(BaseCommand):
    help = 'Initialise les facteurs d\'émission pour les achats'

    def handle(self, *args, **options):
        factors = [
            {
                'category_code': 'food_service',
                'category_label': 'Restauration & Services légers',
                'factor_kg_co2_per_keur': 100.00,
            },
            {
                'category_code': 'insurance',
                'category_label': 'Assurances & Cotisations',
                'factor_kg_co2_per_keur': 110.00,
            },
            {
                'category_code': 'it_telecom',
                'category_label': 'IT & Téléphonie',
                'factor_kg_co2_per_keur': 160.00,
            },
            {
                'category_code': 'cleaning_maintenance',
                'category_label': 'Nettoyage & Entretien & Espaces verts',
                'factor_kg_co2_per_keur': 215.00,
            },
            {
                'category_code': 'activities',
                'category_label': 'Séjours & Activités',
                'factor_kg_co2_per_keur': 270.00,
            },
            {
                'category_code': 'laundry',
                'category_label': 'Blanchisserie',
                'factor_kg_co2_per_keur': 320.00,
            },
            {
                'category_code': 'construction',
                'category_label': 'Travaux & Construction',
                'factor_kg_co2_per_keur': 360.00,
            },
            {
                'category_code': 'transport',
                'category_label': 'Transports',
                'factor_kg_co2_per_keur': 560.00,
            },
            {
                'category_code': 'equipment_rental',
                'category_label': 'Location équipements',
                'factor_kg_co2_per_keur': 600.00,
            },
        ]
        
        created_count = 0
        for factor_data in factors:
            obj, created = PurchaseEmissionFactor.objects.get_or_create(
                category_code=factor_data['category_code'],
                defaults={
                    'category_label': factor_data['category_label'],
                    'factor_kg_co2_per_keur': factor_data['factor_kg_co2_per_keur'],
                    'source': 'Excel Achats 30% - ADEME'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Créé: {obj.category_label}'))
            else:
                self.stdout.write(f'  Existe déjà: {obj.category_label}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Total: {created_count} facteurs créés, {len(factors) - created_count} existants'))
