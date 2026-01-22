"""
Service de parsing du CSV ADEME Base Carbone.
Télécharge et extrait les facteurs d'émission pour tous les secteurs.
"""

import requests
import csv
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ADEMECSVParser:
    """
    Parser pour le fichier CSV ADEME Base Carbone.
    Télécharge et extrait UNIQUEMENT les facteurs d'émission essentiels.
    """
    
    # Facteurs essentiels à extraire (liste blanche ultra-stricte)
    # Basé sur les noms exacts de la Base Carbone ADEME
    ESSENTIAL_FACTORS = {
        'vehicles': {
            'essence_sp95_sp98': {
                'all_keywords': ['essence', 'pompe'],  # "Essence à la pompe"
                'exclude': ['bio', 'france métropolitaine'],
                'unit': 'litre',
                'max_results': 1
            },
            'gazole_routier': {
                'all_keywords': ['gazole'],  # "Gazole routier" ou "Gazole non routier"
                'exclude': ['bio', 'france métropolitaine'],  
                'unit': 'litre',
                'max_results': 2  # Routier + non routier
            },
            'voiture_thermique_km': {
                'all_keywords': ['voiture', 'particulière'],
                'exclude': ['électrique', 'hybride', 'france'],
                'any_of': ['thermique', 'moyenne'],  # Au moins un de ceux-ci
                'unit': 'km',
                'max_results': 1
            },
            'voiture_electrique_km': {
                'all_keywords': ['voiture', 'électrique'],
                'exclude': ['hybride', 'france'],
                'unit': 'km',
                'max_results': 1
            }
        }
    }
    
    def __init__(self, csv_url: str):
        """
        Initialise le parser avec l'URL du CSV.
        
        Args:
            csv_url: URL du fichier CSV ADEME
        """
        self.csv_url = csv_url
        self.timeout = 30  # secondes
        self.max_size = 50 * 1024 * 1024  # 50 MB
    
    def download_csv(self) -> str:
        """
        Télécharge le fichier CSV depuis l'URL configurée.
        
        Returns:
            Contenu du CSV en string
            
        Raises:
            requests.RequestException: En cas d'erreur de téléchargement
            ValueError: Si le fichier est trop volumineux
        """
        logger.info(f"Téléchargement du CSV depuis {self.csv_url}")
        
        try:
            response = requests.get(
                self.csv_url,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Vérifier la taille
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > self.max_size:
                raise ValueError(f"Fichier trop volumineux: {int(content_length) / 1024 / 1024:.1f} MB")
            
            # Télécharger le contenu
            content = response.content.decode('latin-1')  # ADEME utilise latin-1
            
            logger.info(f"CSV téléchargé: {len(content)} caractères")
            return content
            
        except requests.RequestException as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            raise
    
    def parse_csv(self, csv_content: str, sectors: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Parse le contenu CSV et extrait UNIQUEMENT les facteurs essentiels par secteur.
        
        Args:
            csv_content: Contenu du CSV
            sectors: Liste des secteurs à extraire (None = tous)
            
        Returns:
            Dictionnaire {secteur: [facteurs]}
        """
        if sectors is None:
            sectors = list(self.ESSENTIAL_FACTORS.keys())
        
        logger.info(f"Parsing CSV pour secteurs: {sectors}")
        
        result = {sector: [] for sector in sectors}
        
        # Tracker pour limiter le nombre de résultats par facteur
        found_counts = {sector: {} for sector in sectors}
        
        # Parser le CSV
        csv_reader = csv.DictReader(StringIO(csv_content), delimiter=';')
        
        for row in csv_reader:
            # Extraire les données pertinentes
            factor_data = self._extract_factor_from_row(row)
            if not factor_data:
                continue
            
            # Affecter au bon secteur
            for sector in sectors:
                match_result = self._matches_sector(factor_data, sector)
                if match_result:
                    factor_key, max_results = match_result
                    
                    # Vérifier si on a déjà atteint le max pour ce facteur
                    current_count = found_counts[sector].get(factor_key, 0)
                    if current_count < max_results:
                        result[sector].append(factor_data)
                        found_counts[sector][factor_key] = current_count + 1
        
        # Logging
        for sector, factors in result.items():
            logger.info(f"Secteur '{sector}': {len(factors)} facteurs trouvés")
            for factor_key, count in found_counts.get(sector, {}).items():
                logger.info(f"  - {factor_key}: {count} facteur(s)")
        
        return result
    
    def _extract_factor_from_row(self, row: Dict[str, str]) -> Optional[Dict]:
        """
        Extrait les données d'un facteur depuis une ligne CSV.
        
        Args:
            row: Ligne du CSV (dictionnaire)
            
        Returns:
            Dictionnaire avec les données du facteur ou None
        """
        try:
            # Colonnes importantes
            name = row.get('Nom base français', '').strip()
            unit = row.get('Unité français', '').strip()
            value_str = row.get('Total poste non décomposé', '').strip()
            status = row.get('Statut de l\'élément', '').strip() 
            location = row.get('Localisation géographique', '').strip()
            category = row.get('Catégorie de l\'élément', '').strip()
            
            # Filtres de base
            if not name or not value_str:
                return None
            
            # Ne garder que les éléments valides pour France continentale
            if status and 'archivé' in status.lower():
                return None
            
            if location and 'france' not in location.lower() and location.lower() != 'fr':
                # Accepter aussi les éléments sans localisation (génériques)
                if location.strip():  # Si localisation renseignée et pas France, skip
                    return None
            
            # Parser la valeur
            try:
                value = Decimal(value_str.replace(',', '.'))
                if value <= 0 or value > 10000:  # Filtrer les valeurs aberrantes
                    return None
            except (InvalidOperation, ValueError):
                return None
            
            return {
                'name': name,
                'unit': unit,
                'value': value,
                'category': category,
                'status': status,
                'location': location
            }
            
        except Exception as e:
            logger.debug(f"Erreur extraction ligne: {e}")
            return None
    
    def _matches_sector(self, factor_data: Dict, sector: str):
        """
        Vérifie si un facteur correspond STRICTEMENT aux facteurs essentiels du secteur.
        
        Args:
            factor_data: Données du facteur
            sector: Nom du secteur
            
        Returns:
            Tuple (factor_key, max_results) si match, None sinon
        """
        if sector not in self.ESSENTIAL_FACTORS:
            return None
        
        name_lower = factor_data['name'].lower()
        unit_lower = factor_data['unit'].lower()
        
        # Vérifier chaque facteur essentiel
        for factor_key, criteria in self.ESSENTIAL_FACTORS[sector].items():
            # Vérifier l'unité
            if criteria['unit'] not in unit_lower:
                continue
            
            # Vérifier que TOUS les mots-clés sont présents
            all_keywords_present = all(
                kw.lower() in name_lower for kw in criteria['all_keywords']
            )
            if not all_keywords_present:
                continue
            
            # Vérifier any_of si spécifié (au moins un doit être présent)
            if 'any_of' in criteria:
                any_of_present = any(
                    kw.lower() in name_lower for kw in criteria['any_of']
                )
                if not any_of_present:
                    continue
            
            # Vérifier les exclusions
            has_exclusion = any(
                excl.lower() in name_lower for excl in criteria['exclude']
            )
            if has_exclusion:
                continue
            
            # Toutes les conditions sont remplies
            return (factor_key, criteria['max_results'])
        
        return None
    
    def get_factors_for_sector(self, sector: str) -> List[Dict]:
        """
        Télécharge et parse le CSV pour un secteur spécifique.
        
        Args:
            sector: Nom du secteur
            
        Returns:
            Liste des facteurs pour ce secteur
        """
        csv_content = self.download_csv()
        result = self.parse_csv(csv_content, sectors=[sector])
        return result.get(sector, [])
