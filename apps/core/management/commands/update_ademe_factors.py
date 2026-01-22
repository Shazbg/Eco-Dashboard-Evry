"""
Commande Django pour mettre à jour les facteurs ADEME depuis le CSV.
Usage: python manage.py update_ademe_factors [--dry-run] [--sectors vehicles buildings]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.core.models import ADEMEConfiguration
from apps.core.services.ademe_csv_parser import ADEMECSVParser
from apps.vehicles.models import EmissionFactor
from decimal import Decimal


class Command(BaseCommand):
    help = 'Met à jour les facteurs d\'émission ADEME depuis le CSV configuré'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les changements sans les appliquer'
        )
        parser.add_argument(
            '--sectors',
            nargs='+',
            help='Secteurs à mettre à jour (sinon, utilise active_sectors de la config)'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        requested_sectors = options['sectors']
        
        # Récupérer la configuration
        config = ADEMEConfiguration.get_config()
        
        # Déterminer les secteurs à traiter
        if requested_sectors:
            sectors = requested_sectors
        else:
            sectors = config.active_sectors
            if not sectors:
                raise CommandError("Aucun secteur actif configuré. Utilisez l'admin ou --sectors")
        
        self.stdout.write(self.style.SUCCESS(f"\n🌱 Mise à jour ADEME"))
        self.stdout.write(f"URL CSV: {config.csv_url}")
        self.stdout.write(f"Secteurs: {', '.join(sectors)}")
        if dry_run:
            self.stdout.write(self.style.WARNING("Mode DRY-RUN activé\n"))
        
        # Initialiser le parser
        parser = ADEMECSVParser(config.csv_url)
        
        try:
            # Télécharger et parser le CSV
            self.stdout.write("📥 Téléchargement du CSV...")
            csv_content = parser.download_csv()
            self.stdout.write(self.style.SUCCESS("✅ CSV téléchargé\n"))
            
            self.stdout.write("🔍 Parsing du CSV...")
            factors_by_sector = parser.parse_csv(csv_content, sectors=sectors)
            self.stdout.write(self.style.SUCCESS("✅ Parsing terminé\n"))
            
            # Statistiques globales
            total_created = 0
            total_updated = 0
            
            # Traiter chaque secteur
            for sector, factors in factors_by_sector.items():
                self.stdout.write(f"\n📊 Secteur: {sector.upper()}")
                self.stdout.write(f"   Facteurs trouvés: {len(factors)}")
                
                created, updated = self._process_sector_factors(
                    sector, factors, dry_run
                )
                
                total_created += created
                total_updated += updated
                
                self.stdout.write(f"   ✨ Créés: {created}")
                self.stdout.write(f"   🔄 Mis à jour: {updated}")
            
            # Résumé final
            self.stdout.write(self.style.SUCCESS(f"\n✅ Terminé!"))
            self.stdout.write(f"Total créés: {total_created}")
            self.stdout.write(f"Total mis à jour: {total_updated}")
            
            # Mettre à jour la config (sauf en dry-run)
            if not dry_run:
                config.last_update = timezone.now()
                # Extraire version du CSV si possible
                if 'V' in config.csv_url:
                    parts = config.csv_url.split('V')
                    if len(parts) > 1:
                        config.csv_version = 'V' + parts[-1].split('.')[0] + '.' + parts[-1].split('.')[1]
                config.save()
                self.stdout.write(self.style.SUCCESS(f"Configuration mise à jour"))
            
        except Exception as e:
            raise CommandError(f"Erreur: {e}")
    
    def _process_sector_factors(self, sector, factors, dry_run):
        """
        Traite les facteurs d'un secteur : création ou mise à jour.
        
        Returns:
            Tuple (nb_created, nb_updated)
        """
        created = 0
        updated = 0
        
        for factor_data in factors:
            # Créer une clé unique basée sur le nom et l'unité
            subcategory = self._generate_subcategory(factor_data['name'], sector)
            
            # Chercher un facteur existant
            existing = EmissionFactor.objects.filter(
                subcategory=subcategory,
                category=sector
            ).first()
            
            if existing:
                # Mise à jour si la valeur a changé
                if existing.factor_value != factor_data['value']:
                    if not dry_run:
                        existing.factor_value = factor_data['value']
                        existing.name = factor_data['name']
                        existing.is_active = True
                        existing.save()
                    updated += 1
            else:
                # Création
                if not dry_run:
                    EmissionFactor.objects.create(
                        name=factor_data['name'],
                        category=sector,
                        subcategory=subcategory,
                        unit=factor_data['unit'],
                        factor_value=factor_data['value'],
                        source='ADEME Base Carbone',
                        is_active=True
                    )
                created += 1
        
        return created, updated
    
    def _generate_subcategory(self, name, sector):
        """
        Génère une sous-catégorie unique à partir du nom.
        """
        # Nettoyer et normaliser le nom
        clean_name = name.lower()
        clean_name = clean_name.replace(' ', '_')
        clean_name = clean_name.replace('-', '_')
        clean_name = clean_name.replace('(', '').replace(')', '')
        clean_name = clean_name.replace('é', 'e').replace('è', 'e')
        clean_name = clean_name.replace('à', 'a').replace('ô', 'o')
        
        # Limiter la longueur
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
        
        return f"{sector}_{clean_name}"
