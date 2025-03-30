"""
Module de sérialisation/désérialisation pour les objets OpenBadge v3

Ce module fournit des fonctions pour convertir les objets OpenBadge v3
en JSON-LD et inversement.
"""

import json
from typing import Dict, Any, Union, Optional, Type, TypeVar, cast
from datetime import datetime
import uuid

from ..models.profile import Profile
from ..models.achievement import Achievement
from ..models.credential import OpenBadgeCredential
from ..models.endorsement import EndorsementCredential


T = TypeVar('T', Profile, Achievement, OpenBadgeCredential, EndorsementCredential)


def to_json_ld(obj: T) -> Dict[str, Any]:
    """
    Convertit un objet OpenBadge v3 en format JSON-LD
    
    Args:
        obj: L'objet à convertir (Profile, Achievement, OpenBadgeCredential, EndorsementCredential)
        
    Returns:
        Dict[str, Any]: L'objet au format JSON-LD
    """
    if hasattr(obj, 'to_json_ld') and callable(getattr(obj, 'to_json_ld')):
        return obj.to_json_ld()
    
    # Fallback si la méthode to_json_ld n'est pas disponible
    data = obj.dict(exclude_none=True)
    
    # Ajouter le contexte approprié
    if isinstance(obj, Profile) or isinstance(obj, Achievement):
        data["@context"] = "https://w3id.org/openbadges/v3"
    else:
        data["@context"] = [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/openbadges/v3"
        ]
    
    return data


def from_json_ld(json_data: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Convertit un objet JSON-LD en objet OpenBadge v3
    
    Args:
        json_data: Les données JSON-LD à convertir
        model_class: La classe de modèle à utiliser (Profile, Achievement, etc.)
        
    Returns:
        T: L'objet OpenBadge correspondant
    """
    # Supprimer la clé @context avant de créer l'objet
    data = json_data.copy()
    data.pop("@context", None)
    
    return model_class(**data)


def save_to_file(obj: T, file_path: str) -> None:
    """
    Sauvegarde un objet OpenBadge v3 dans un fichier JSON
    
    Args:
        obj: L'objet à sauvegarder
        file_path: Le chemin du fichier où sauvegarder l'objet
    """
    json_data = to_json_ld(obj)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


def load_from_file(file_path: str, model_class: Type[T]) -> T:
    """
    Charge un objet OpenBadge v3 depuis un fichier JSON
    
    Args:
        file_path: Le chemin du fichier à charger
        model_class: La classe de modèle à utiliser
        
    Returns:
        T: L'objet OpenBadge correspondant
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    return from_json_ld(json_data, model_class)


def generate_badge_id(domain: str, path_prefix: str = "achievements") -> str:
    """
    Génère un identifiant unique pour un badge
    
    Args:
        domain: Le domaine à utiliser (par exemple, 'example.org')
        path_prefix: Le préfixe de chemin à utiliser
        
    Returns:
        str: L'identifiant du badge
    """
    unique_id = str(uuid.uuid4())
    return f"https://{domain}/{path_prefix}/{unique_id}"


def generate_credential_id(domain: str, path_prefix: str = "credentials") -> str:
    """
    Génère un identifiant unique pour un credential
    
    Args:
        domain: Le domaine à utiliser (par exemple, 'example.org')
        path_prefix: Le préfixe de chemin à utiliser
        
    Returns:
        str: L'identifiant du credential
    """
    unique_id = str(uuid.uuid4())
    return f"https://{domain}/{path_prefix}/{unique_id}"
