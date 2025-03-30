"""
Module définissant le modèle Achievement selon la spécification OpenBadge v3.0

Un Achievement représente la définition d'un badge qui peut être attribué.
"""

from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID

from .profile import Image, Profile


class Criteria(BaseModel):
    """
    Classe représentant les critères pour obtenir un badge
    
    Définit les conditions à remplir pour obtenir un achievement
    """
    id: Optional[HttpUrl] = None  # URI optionnel pour les critères
    narrative: Optional[str] = None  # Texte décrivant les critères
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "narrative": "Pour obtenir ce badge, le candidat doit démontrer sa maîtrise de Python "
                                "en développant une application fonctionnelle avec au moins trois fonctionnalités."
                }
            ]
        }
    }


class Alignment(BaseModel):
    """
    Classe représentant l'alignement d'un badge avec un référentiel de compétences externe
    
    Permet d'associer un badge à des standards ou cadres de compétences
    """
    targetName: str  # Nom du référentiel
    targetUrl: HttpUrl  # URL du référentiel
    targetDescription: Optional[str] = None  # Description du référentiel
    targetFramework: Optional[str] = None  # Nom du cadre de compétences
    targetCode: Optional[str] = None  # Code de la compétence dans le référentiel
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "targetName": "Compétence Python avancée",
                    "targetUrl": "https://example.org/frameworks/python-skills",
                    "targetDescription": "Maîtrise des concepts avancés de Python",
                    "targetFramework": "Référentiel de compétences en développement",
                    "targetCode": "PY301"
                }
            ]
        }
    }


class Achievement(BaseModel):
    """
    Classe représentant un Achievement (BadgeClass) dans le standard OpenBadge v3
    
    Un Achievement définit un type de badge qui peut être attribué à un destinataire.
    Il contient les informations sur le badge, les critères pour l'obtenir, etc.
    """
    # Champs obligatoires
    id: HttpUrl  # URI unique qui identifie l'achievement
    type: Union[str, List[str]] = "Achievement"  # Le type doit inclure "Achievement"
    name: str  # Nom lisible par un humain
    issuer: Union[HttpUrl, Profile, Dict[str, Any]]  # Référence à l'émetteur (Profile)
    
    # Champs recommandés
    description: Optional[str] = None  # Description du badge
    criteria: Optional[Criteria] = None  # Critères d'obtention
    image: Optional[Image] = None  # Image représentant le badge
    
    # Champs optionnels
    tags: Optional[List[str]] = None  # Tags pour catégoriser le badge
    alignment: Optional[List[Alignment]] = None  # Alignements avec des référentiels
    
    # Métadonnées
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    
    @field_validator('type')
    def validate_type(cls, v):
        """
        Valide que le champ 'type' inclut 'Achievement'
        
        Un Achievement dans OpenBadge v3 doit avoir le type 'Achievement'
        """
        if isinstance(v, str):
            if v != "Achievement":
                raise ValueError("Le type doit inclure 'Achievement'")
        elif isinstance(v, list):
            if "Achievement" not in v:
                raise ValueError("Le type doit inclure 'Achievement'")
        return v
    
    @field_validator('issuer')
    def validate_issuer(cls, v):
        """
        Valide que l'émetteur est soit une URL soit un objet Profile ou un dictionnaire
        
        L'émetteur peut être référencé par son URL ou inclus comme objet complet
        """
        if isinstance(v, dict) and 'id' in v and 'type' in v:
            if v["type"] == "Profile" and "name" not in v:
                v["name"] = "Unnamed Profile"  # Ajouter un nom par défaut pour les dictionnaires convertis
                
        if not isinstance(v, (HttpUrl, Profile, dict, str)):
            raise ValueError("L'émetteur doit être une URL ou un objet Profile")
        return v
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convertit l'Achievement en format JSON-LD compatible avec OpenBadge v3
        
        Cette méthode ajoute le contexte JSON-LD nécessaire pour la compatibilité
        avec les outils de vérification OpenBadge.
        
        Returns:
            Dict: L'achievement au format JSON-LD
        """
        data = self.model_dump(exclude_none=True)
        
        # Convertir les champs HttpUrl en chaînes de caractères
        if 'id' in data and hasattr(data['id'], '__str__'):
            data['id'] = str(data['id'])
            
        # Convertir l'émetteur en référence si c'est un objet Profile
        if isinstance(self.issuer, Profile):
            data["issuer"] = {
                "id": str(self.issuer.id),
                "type": self.issuer.type
            }
        elif 'issuer' in data and isinstance(data['issuer'], dict) and 'id' in data['issuer']:
            data['issuer']['id'] = str(data['issuer']['id'])
            
        # Convertir les URLs dans image si présent
        if 'image' in data and isinstance(data['image'], dict) and 'id' in data['image']:
            data['image']['id'] = str(data['image']['id'])
        
        data["@context"] = "https://w3id.org/openbadges/v3"
        return data

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://example.org/badges/1",
                    "type": "Achievement",
                    "name": "Maîtrise de Python",
                    "description": "Ce badge certifie la maîtrise avancée du langage Python",
                    "criteria": {
                        "narrative": "Pour obtenir ce badge, le candidat doit développer une application Python."
                    },
                    "image": {
                        "id": "https://example.org/badges/1/image",
                        "type": "Image"
                    },
                    "issuer": {
                        "id": "https://example.org/issuers/1",
                        "type": "Profile"
                    },
                    "tags": ["programmation", "python", "développement"]
                }
            ]
        }
    }
