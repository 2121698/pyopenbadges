"""
Module définissant le modèle Profile (émetteur) selon la spécification OpenBadge v3.0

Un Profile représente l'entité qui émet les badges (organisation, institution, etc.)
"""

from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID


class Image(BaseModel):
    """
    Classe représentant une image dans le contexte OpenBadge
    
    Une image peut être liée à un Profile, un Achievement ou un autre élément
    """
    id: HttpUrl  # URL vers l'image
    type: str = "Image"
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class Profile(BaseModel):
    """
    Classe représentant un émetteur (Issuer) dans le standard OpenBadge v3
    
    Un Profile est une entité qui peut émettre des badges, comme une organisation,
    une institution éducative, ou un individu autorisé.
    """
    # Champs obligatoires
    id: HttpUrl  # URI unique qui identifie le profil
    type: Union[str, List[str]] = "Profile"  # Le type doit inclure "Profile"
    name: str  # Nom lisible par un humain
    
    # Champs recommandés
    url: Optional[HttpUrl] = None  # Site web du profil
    email: Optional[EmailStr] = None  # Email de contact
    description: Optional[str] = None  # Description du profil
    image: Optional[Image] = None  # Image/logo du profil
    
    # Champs optionnels
    telephone: Optional[str] = None  # Numéro de téléphone
    publicKey: Optional[Dict[str, Any]] = None  # Clé publique pour vérification
    parentOrg: Optional[Union[HttpUrl, Dict[str, Any]]] = None  # Organisation parente
    
    # Métadonnées
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @field_validator('type')
    def validate_type(cls, v):
        """
        Valide que le champ 'type' inclut 'Profile'
        
        Un Profile dans OpenBadge v3 doit avoir le type 'Profile'
        """
        if isinstance(v, str):
            if v != "Profile":
                raise ValueError("Le type doit inclure 'Profile'")
        elif isinstance(v, list):
            if "Profile" not in v:
                raise ValueError("Le type doit inclure 'Profile'")
        return v
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convertit le Profile en format JSON-LD compatible avec OpenBadge v3
        
        Cette méthode ajoute le contexte JSON-LD nécessaire pour la compatibilité
        avec les outils de vérification OpenBadge.
        
        Returns:
            Dict: Le profil au format JSON-LD
        """
        data = self.model_dump(exclude_none=True)
        
        # Convertir les champs HttpUrl en chaînes de caractères
        if 'id' in data and hasattr(data['id'], '__str__'):
            data['id'] = str(data['id'])
            
        # Convertir l'URL en chaîne si présente
        if 'url' in data and hasattr(data['url'], '__str__'):
            data['url'] = str(data['url'])
            
        # Convertir les URLs dans image si présent
        if 'image' in data and isinstance(data['image'], dict) and 'id' in data['image']:
            data['image']['id'] = str(data['image']['id'])
            
        # Convertir parentOrg en chaîne si c'est une URL
        if 'parentOrg' in data:
            if isinstance(data['parentOrg'], dict) and 'id' in data['parentOrg']:
                data['parentOrg']['id'] = str(data['parentOrg']['id'])
            elif hasattr(data['parentOrg'], '__str__'):
                data['parentOrg'] = str(data['parentOrg'])
                
        data["@context"] = "https://w3id.org/openbadges/v3"
        return data

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://example.org/issuers/1",
                    "type": "Profile",
                    "name": "Organisation Exemple",
                    "url": "https://example.org",
                    "email": "contact@example.org",
                    "description": "Une organisation qui délivre des badges",
                    "image": {
                        "id": "https://example.org/logo.png",
                        "type": "Image"
                    }
                }
            ]
        }
    }
