# Intégration de la Stéganographie dans PyOpenBadges

*Date de création: 30/03/2025*

## Contexte

La spécification OpenBadge v3.0 mentionne dans sa section 8.3 (Embedded Proofs) la possibilité d'intégrer les preuves directement dans le badge. La stéganographie - l'art de cacher des informations dans d'autres données - offre une approche élégante pour intégrer l'ensemble des données d'un badge (métadonnées, preuves cryptographiques) directement dans l'image représentant visuellement ce badge.

## Avantages de la stéganographie pour les Open Badges

### 1. Portabilité améliorée
- Une image contenant son propre badge devient un fichier unique et autonome
- Facilite le partage sur les réseaux sociaux et autres plateformes qui acceptent les images mais pas les métadonnées complexes
- Élimine le problème de maintenir un lien entre l'image visuelle et les données du badge

### 2. Persistance du lien badge-visuel
- Dans un système traditionnel, l'image et les métadonnées du badge peuvent être séparées lors du partage
- Avec la stéganographie, même si l'image est copiée ou téléchargée, les données du badge restent intégrées
- Garantit l'intégrité conceptuelle du badge comme un objet unique

### 3. Vérification hors-ligne
- Si le badge complet (incluant sa preuve) est intégré dans l'image, il peut être vérifié sans accès au serveur d'origine
- Utile dans des contextes à connectivité limitée ou pour des vérifications rapides
- Réduit la dépendance aux services en ligne pour la validation

### 4. Conformité à la spécification
- Répond à l'intention de la section 8.3 de la spécification Open Badges v3.0 concernant les "Embedded Proofs"
- Offre une implémentation technique d'un concept important de la spécification

## Considérations techniques et défis

### 1. Taille des données
- Les badges complets avec preuves peuvent occuper plusieurs kilooctets de données
- La capacité de stéganographie d'une image est limitée par sa taille et le type d'algorithme utilisé
- Stratégies possibles:
  - Compression des données du badge avant intégration
  - Utilisation d'algorithmes à haute capacité d'intégration
  - Limitation du contenu intégré aux données essentielles uniquement

### 2. Robustesse
- Les modifications de l'image (redimensionnement, compression, recadrage) peuvent altérer ou détruire les données cachées
- Importance de la robustesse aux transformations courantes:
  - Algorithmes résistants à la compression JPEG
  - Techniques de redondance des données
  - Mécanismes de détection et correction d'erreurs

### 3. Sécurité et vie privée
- Si mal implémentée, la stéganographie pourrait exposer des données personnelles de manière non intentionnelle
- Considérations d'implémentation:
  - Chiffrement optionnel des données intégrées
  - Contrôle granulaire de ce qui est intégré (exclusion d'informations sensibles)
  - Documentation claire pour les utilisateurs sur ce qui est intégré dans l'image

### 4. Équilibre visuel
- L'intégration ne doit pas dégrader visiblement la qualité de l'image du badge
- Paramètres ajustables permettant de privilégier:
  - L'imperceptibilité (préservation visuelle)
  - La capacité (quantité de données intégrables)
  - La robustesse (résistance aux transformations)

## Proposition d'implémentation pour PyOpenBadges

### 1. Nouvelle classe `EmbeddedProof`

```python
from typing import Optional, Union
from PIL import Image
import io
from pydantic import BaseModel, Field
import json
import base64

class EmbeddedProof(BaseModel):
    """
    Représente une preuve intégrée dans une image via stéganographie
    
    Implémente la section 8.3 de la spécification OpenBadge v3.0
    """
    type: str = "EmbeddedProof2020"
    image_format: str = "png"  # Format de l'image (png recommandé pour la stéganographie)
    embedding_method: str = "lsb"  # Méthode d'intégration (LSB par défaut)
    
    @classmethod
    def create(cls, credential_data: dict, image_path: str, 
               method: str = "lsb", password: Optional[str] = None) -> 'EmbeddedProof':
        """
        Intègre les données d'un credential dans une image via stéganographie
        
        Args:
            credential_data: Données du credential à intégrer
            image_path: Chemin vers l'image dans laquelle intégrer les données
            method: Méthode de stéganographie à utiliser ('lsb', 'dct', 'dwt')
            password: Mot de passe optionnel pour chiffrer les données
            
        Returns:
            EmbeddedProof: L'objet preuve avec l'image intégrée
        """
        # Implémentation à définir
        pass
    
    def extract_credential(self, password: Optional[str] = None) -> dict:
        """
        Extrait les données du credential intégrées dans l'image
        
        Args:
            password: Mot de passe pour déchiffrer les données (si nécessaire)
            
        Returns:
            dict: Les données du credential extraites
            
        Raises:
            ValueError: Si les données ne peuvent pas être extraites
        """
        # Implémentation à définir
        pass
```

### 2. Extension de `OpenBadgeCredential`

```python
def embed_in_image(self, image_path: str, output_path: Optional[str] = None,
                  method: str = "lsb", password: Optional[str] = None) -> str:
    """
    Intègre le credential dans une image via stéganographie
    
    Args:
        image_path: Chemin vers l'image originale
        output_path: Chemin pour l'image résultante (si None, utilise image_path)
        method: Méthode de stéganographie ('lsb', 'dct', 'dwt')
        password: Mot de passe optionnel pour chiffrer les données
        
    Returns:
        str: Chemin vers l'image contenant le credential intégré
    """
    # Convertir le credential en JSON
    credential_json = self.model_dump_json()
    
    # Utiliser la bibliothèque de stéganographie pour intégrer les données
    # ...
    
    return output_path or image_path

@classmethod
def from_image(cls, image_path: str, password: Optional[str] = None) -> 'OpenBadgeCredential':
    """
    Extrait un credential d'une image via stéganographie
    
    Args:
        image_path: Chemin vers l'image contenant le credential
        password: Mot de passe pour déchiffrer les données (si nécessaire)
        
    Returns:
        OpenBadgeCredential: Le credential extrait
        
    Raises:
        ValueError: Si l'image ne contient pas de credential valide
    """
    # Extraire les données de l'image
    # ...
    
    # Convertir les données en credential
    return cls.model_validate_json(credential_json)
```

### 3. Implémentation des algorithmes de stéganographie

Plusieurs approches seraient implémentées, chacune avec ses propres avantages:

#### LSB (Least Significant Bit)
- **Description**: Modifie les bits de poids faible des pixels
- **Avantages**: Simple, bonne capacité
- **Inconvénients**: Peu robuste aux modifications

#### DCT (Discrete Cosine Transform)
- **Description**: Modifie les coefficients de la transformée en cosinus discrète
- **Avantages**: Plus robuste aux compressions JPEG
- **Inconvénients**: Capacité plus limitée

#### DWT (Discrete Wavelet Transform)
- **Description**: Modifie les coefficients de la transformée en ondelettes
- **Avantages**: Très robuste aux transformations
- **Inconvénients**: Complexité d'implémentation

### 4. Dépendances à ajouter

```toml
[tool.poetry.dependencies]
python = "^3.8"
pydantic = "^2.0.0"
Pillow = "^9.0.0"  # Pour la manipulation d'images
stegano = "^0.10.0"  # Bibliothèque de base pour la stéganographie
pywavelets = "^1.3.0"  # Pour la méthode DWT
numpy = "^1.23.0"  # Requis pour les transformations
cryptography = "^40.0.0"  # Pour le chiffrement des données
```

## Plan d'implémentation TDD

### 1. Tests de base

```python
def test_embed_and_extract_credential_lsb():
    """Teste l'intégration et l'extraction d'un credential avec la méthode LSB"""
    # Créer un credential
    credential = create_test_credential()
    
    # Intégrer dans une image
    output_path = credential.embed_in_image("test_images/badge.png", 
                                           "test_images/badge_with_data.png")
    
    # Extraire le credential
    extracted = OpenBadgeCredential.from_image(output_path)
    
    # Vérifier que le credential extrait correspond à l'original
    assert extracted.id == credential.id
    assert extracted.type == credential.type
    # etc.
```

### 2. Tests de robustesse

```python
def test_extract_after_resize():
    """Teste l'extraction après redimensionnement de l'image"""
    # Créer et intégrer
    # ...
    
    # Redimensionner l'image
    # ...
    
    # Tenter d'extraire
    # ...
```

### 3. Tests de limites

```python
def test_capacity_limits():
    """Teste les limites de capacité d'intégration"""
    # Créer un credential avec beaucoup de données
    # ...
    
    # Tenter d'intégrer dans une petite image
    # ...
```

## Considérations pour l'interface utilisateur

### 1. Interface en ligne de commande

```bash
# Intégrer un badge dans une image
python -m pyopenbadges embed --credential badge.json --image logo.png --output badge_embedded.png

# Extraire un badge d'une image
python -m pyopenbadges extract --image badge_embedded.png --output extracted_badge.json
```

### 2. Interface programmatique

```python
# Intégrer
credential.embed_in_image("logo.png", "badge_embedded.png")

# Extraire
credential = OpenBadgeCredential.from_image("badge_embedded.png")
```

## Conclusion

L'intégration de fonctionnalités de stéganographie dans PyOpenBadges ouvrirait de nouvelles possibilités pour le partage et la vérification des badges. Bien qu'il s'agisse d'une fonctionnalité avancée qui présente certains défis techniques, elle correspond parfaitement à l'esprit de la spécification OpenBadge v3.0 et pourrait devenir un différenciateur important pour cette bibliothèque.

Cette approche permettrait également d'enrichir l'écosystème des badges numériques en permettant leur partage dans des contextes où les métadonnées complexes ne sont généralement pas préservées, comme les plateformes de médias sociaux, élargissant ainsi la portée et l'utilité des Open Badges.
