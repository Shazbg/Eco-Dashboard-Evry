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
    Télécharge et extrait les facteurs d'émission pertinents pour chaque secteur.
    """
    
    # Mapping des secteurs vers les mots-clés et catégories ADEME
    SECTOR_MAPPING = {
        'vehicles': {
            'keywords': ['essence', 'sp95', 'sp98', 'gazole', 'diesel', 'voiture', 'véhicule'],
            'categories': ['Transport routier', 'Transports']
        },
        'buildings': {
            'keywords': ['électricité', 'gaz naturel', 'chauffage', 'fioul', 'climatisation'],
            'categories': ['Energie', 'Chauffage urbain']
        },
        'food': {
            'keywords': ['viande', 'poisson', 'légumes', 'fruits', 'pain', 'lait', 'fromage'],
            'categories': ['Alimentation']
        },
        'purchases': {
            'keywords': ['papier', 'carton', 'mobilier', 'ordinateur', 'textile', 'fourniture'],
            'categories': ['Produits', 'Services']
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
        Parse le contenu CSV et extrait les facteurs par secteur.
        
        Args:
            csv_content: Contenu du CSV
            sectors: Liste des secteurs à extraire (None = tous)
            
        Returns:
            Dictionnaire {secteur: [facteurs]}
        """
        if sectors is None:
            sectors = list(self.SECTOR_MAPPING.keys())
        
        logger.info(f"Parsing CSV pour secteurs: {sectors}")
        
        result = {sector: [] for sector in sectors}
        
        # Parser le CSV
        csv_reader = csv.DictReader(StringIO(csv_content), delimiter=';')
        
        for row in csv_reader:
            # Extraire les données pertinentes
            factor_data = self._extract_factor_from_row(row)
            if not factor_data:
                continue
            
            # Affecter au bon secteur
            for sector in sectors:
                if self._matches_sector(factor_data, sector):
                    result[sector].append(factor_data)
        
        # Logging
        for sector, factors in result.items():
            logger.info(f"Secteur '{sector}': {len(factors)} facteurs trouvés")
        
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
    
    def _matches_sector(self, factor_data: Dict, sector: str) -> bool:
        """
        Vérifie si un facteur correspond à un secteur donné.
        
        Args:
            factor_data: Données du facteur
            sector: Nom du secteur
            
        Returns:
            True si le facteur correspond au secteur
        """
        mapping = self.SECTOR_MAPPING.get(sector)
        if not mapping:
            return False
        
        name_lower = factor_data['name'].lower()
        category_lower = factor_data.get('category', '').lower()
        
        # Vérifier les mots-clés
        for keyword in mapping['keywords']:
            if keyword.lower() in name_lower:
                return True
        
        # Vérifier les catégories
        for cat in mapping['categories']:
            if cat.lower() in category_lower:
                return True
        
        return False
    
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
