"""
Module de validation pour les objets OpenBadge v3

Ce module fournit des fonctions pour valider la conformité des objets 
OpenBadge par rapport à la spécification v3.0 d'IMS Global.
"""

import json
import re
import requests
from typing import Dict, Any, List, Tuple, Union, Optional
from datetime import datetime

from ..models.profile import Profile
from ..models.achievement import Achievement
from ..models.credential import OpenBadgeCredential
from ..models.endorsement import EndorsementCredential


class ValidationError(Exception):
    """Exception levée en cas d'erreur de validation"""
    pass


class ValidationResult:
    """
    Classe représentant le résultat d'une validation
    
    Permet de stocker à la fois le statut de validation (succès/échec)
    et les messages d'erreur éventuels et des avertissements qui n'invalident pas le résultat.
    """
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        
        # Si nous avons des erreurs à l'initialisation, l'objet est invalide
        if errors and len(errors) > 0:
            self.is_valid = False
    
    def add_error(self, error: str) -> None:
        """Ajoute une erreur critique et marque le résultat comme invalide"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Ajoute un avertissement sans invalider le résultat"""
        self.warnings.append(warning)
    
    def __bool__(self) -> bool:
        """Permet d'utiliser le résultat directement dans les conditions"""
        return self.is_valid
    
    def __str__(self) -> str:
        """Représentation en chaîne du résultat pour le débogage"""
        if self.is_valid:
            if not self.warnings:
                return "Validation réussie"
            return f"Validation réussie avec {len(self.warnings)} avertissement(s)"
        return f"Validation échouée avec {len(self.errors)} erreur(s) et {len(self.warnings)} avertissement(s)"


def validate_url(url: str) -> ValidationResult:
    """
    Valide une URL selon les exigences d'OpenBadge
    
    Args:
        url (str): L'URL à valider
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Vérifier que l'URL est bien formée
    url_pattern = re.compile(
        r'^(https?):\/\/'  # http:// ou https://
        r'([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+' # domaine
        r'[a-zA-Z]{2,}'  # extension de domaine (.com, .org, etc.)
        r'(:\d{1,5})?'  # port optionnel
        r'(\/[^\s]*)?$'  # chemin optionnel
    )
    
    if not url_pattern.match(url):
        result.add_error(f"URL invalide: {url}")
        return result
    
    # Vérifier que l'URL utilise HTTPS (recommandé mais pas obligatoire)
    if not url.startswith("https://"):
        result.add_warning(f"URL non sécurisée (http): {url}. Il est recommandé d'utiliser https.")
    
    return result


def validate_json_ld(json_data: Dict[str, Any]) -> ValidationResult:
    """
    Valide la structure de base d'un objet JSON-LD pour OpenBadge v3
    
    Args:
        json_data (Dict): Les données JSON-LD à valider
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Vérifier la présence du contexte JSON-LD
    if "@context" not in json_data:
        result.add_warning("Le contexte JSON-LD (@context) est manquant")
        # Ne pas interrompre la validation
    else:
        # Vérifier que le contexte contient les valeurs requises
        context = json_data["@context"]
        if isinstance(context, list):
            context_values = set(context)
            if "https://www.w3.org/2018/credentials/v1" not in context_values and "https://w3id.org/openbadges/v3" not in context_values:
                result.add_warning("Le contexte JSON-LD devrait inclure 'https://www.w3.org/2018/credentials/v1' et/ou 'https://w3id.org/openbadges/v3'")
        elif isinstance(context, str):
            if context != "https://w3id.org/openbadges/v3":
                result.add_warning(f"Contexte JSON-LD '{context}' inattendu, 'https://w3id.org/openbadges/v3' recommandé")
            # Si le contexte est correct, on accepte
    
    # Vérifier la présence d'un identifiant
    if "id" not in json_data:
        result.add_warning("L'identifiant (id) est manquant")
    else:
        # Valider l'URL de l'identifiant si c'est une chaîne
        if isinstance(json_data["id"], str):
            id_result = validate_url(json_data["id"])
            if not id_result.is_valid:
                for error in id_result.errors:
                    result.add_warning(f"Potentielle erreur dans l'identifiant: {error}")
            for warning in id_result.warnings:
                result.add_warning(warning)
        else:  # Si c'est un objet HttpUrl ou autre chose
            result.add_warning("L'identifiant n'est pas une chaîne de caractères, impossible de valider le format URL")
    
    # Vérifier la présence d'un type
    if "type" not in json_data:
        result.add_error("Le type est manquant")
    
    return result


def validate_profile(profile: Union[Profile, Dict[str, Any]]) -> ValidationResult:
    """
    Valide un profil (émetteur) selon la spécification OpenBadge v3
    
    Args:
        profile: Le profil à valider, sous forme d'objet Profile ou de dictionnaire
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Convertir en dictionnaire si c'est un objet Profile
    if isinstance(profile, Profile):
        profile_dict = profile.model_dump(exclude_none=True)
        
        # Convertir les URLs en chaînes
        if 'id' in profile_dict and hasattr(profile_dict['id'], '__str__'):
            profile_dict['id'] = str(profile_dict['id'])
        if 'url' in profile_dict and hasattr(profile_dict['url'], '__str__'):
            profile_dict['url'] = str(profile_dict['url'])
            
    else:
        profile_dict = profile
    
    # Valider la structure JSON-LD de base
    json_ld_result = validate_json_ld(profile_dict)
    if not json_ld_result.is_valid:
        for error in json_ld_result.errors:
            result.add_error(error)
    for warning in json_ld_result.warnings:
        result.add_warning(warning)
    
    # Vérifier que le type inclut "Profile"
    if "type" in profile_dict:
        profile_type = profile_dict["type"]
        if isinstance(profile_type, list) and "Profile" not in profile_type:
            result.add_error("Le type doit inclure 'Profile'")
        elif isinstance(profile_type, str) and profile_type != "Profile":
            result.add_error("Le type doit être 'Profile'")
    
    # Vérifier la présence du nom
    if "name" not in profile_dict:
        result.add_error("Le nom (name) est obligatoire pour un Profile")
    
    # Vérifier l'URL du profil si présente
    if "url" in profile_dict:
        if isinstance(profile_dict["url"], str):
            url_result = validate_url(profile_dict["url"])
            if not url_result.is_valid:
                for error in url_result.errors:
                    result.add_warning(f"URL du profil potentiellement invalide: {error}")
        for warning in url_result.warnings:
            result.add_warning(warning)
    
    # Vérifier l'image si présente
    if "image" in profile_dict and isinstance(profile_dict["image"], dict):
        if "id" not in profile_dict["image"]:
            result.add_warning("L'image devrait avoir un identifiant (id)")
        else:
            image_url_result = validate_url(profile_dict["image"]["id"])
            if not image_url_result.is_valid:
                for error in image_url_result.errors:
                    result.add_warning(f"URL de l'image potentiellement invalide: {error}")
            for warning in image_url_result.warnings:
                result.add_warning(warning)
    
    return result


def validate_achievement(achievement: Union[Achievement, Dict[str, Any]]) -> ValidationResult:
    """
    Valide un achievement selon la spécification OpenBadge v3
    
    Args:
        achievement: L'achievement à valider, sous forme d'objet Achievement ou de dictionnaire
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Convertir en dictionnaire si c'est un objet Achievement
    if isinstance(achievement, Achievement):
        achievement_dict = achievement.model_dump(exclude_none=True)
        
        # Convertir les URLs en chaînes
        if 'id' in achievement_dict and hasattr(achievement_dict['id'], '__str__'):
            achievement_dict['id'] = str(achievement_dict['id'])
            
        # Convertir l'URL de l'issuer
        if 'issuer' in achievement_dict:
            if isinstance(achievement_dict['issuer'], dict) and 'id' in achievement_dict['issuer']:
                achievement_dict['issuer']['id'] = str(achievement_dict['issuer']['id'])
            elif hasattr(achievement_dict['issuer'], '__str__'):
                achievement_dict['issuer'] = str(achievement_dict['issuer'])
    else:
        achievement_dict = achievement
    
    # Valider la structure JSON-LD de base
    json_ld_result = validate_json_ld(achievement_dict)
    if not json_ld_result.is_valid:
        for error in json_ld_result.errors:
            result.add_error(error)
    for warning in json_ld_result.warnings:
        result.add_warning(warning)
    
    # Vérifier que le type inclut "Achievement"
    if "type" in achievement_dict:
        achievement_type = achievement_dict["type"]
        if isinstance(achievement_type, list) and "Achievement" not in achievement_type:
            result.add_error("Le type doit inclure 'Achievement'")
        elif isinstance(achievement_type, str) and achievement_type != "Achievement":
            result.add_error("Le type doit être 'Achievement'")
    
    # Vérifier la présence du nom
    if "name" not in achievement_dict:
        result.add_error("Le nom (name) est obligatoire pour un Achievement")
    
    # Vérifier la présence de l'émetteur
    if "issuer" not in achievement_dict:
        result.add_warning("L'émetteur (issuer) est normalement obligatoire pour un Achievement")
    else:
        # Si l'émetteur est un objet complet, le valider
        issuer = achievement_dict["issuer"]
        if isinstance(issuer, dict) and "id" in issuer:
            id_result = validate_url(issuer["id"])
            if not id_result.is_valid:
                for error in id_result.errors:
                    result.add_warning(f"URL de l'émetteur potentiellement invalide: {error}")
            for warning in id_result.warnings:
                result.add_warning(warning)
    
    # Vérifier l'image si présente
    if "image" in achievement_dict and isinstance(achievement_dict["image"], dict):
        if "id" not in achievement_dict["image"]:
            result.add_warning("L'image devrait avoir un identifiant (id)")
        else:
            image_url_result = validate_url(achievement_dict["image"]["id"])
            if not image_url_result.is_valid:
                for error in image_url_result.errors:
                    result.add_warning(f"URL de l'image potentiellement invalide: {error}")
            for warning in image_url_result.warnings:
                result.add_warning(warning)
    
    # Vérifier les alignements si présents
    if "alignment" in achievement_dict and isinstance(achievement_dict["alignment"], list):
        for i, alignment in enumerate(achievement_dict["alignment"]):
            if not isinstance(alignment, dict):
                result.add_error(f"Alignement #{i+1} doit être un objet")
                continue
            
            if "targetName" not in alignment:
                result.add_error(f"Alignement #{i+1} doit avoir un nom de cible (targetName)")
            
            if "targetUrl" not in alignment:
                result.add_error(f"Alignement #{i+1} doit avoir une URL de cible (targetUrl)")
            else:
                url_result = validate_url(alignment["targetUrl"])
                if not url_result.is_valid:
                    for error in url_result.errors:
                        result.add_error(f"URL de l'alignement #{i+1} invalide: {error}")
                for warning in url_result.warnings:
                    result.add_warning(warning)
    
    return result


def validate_credential(credential: Union[OpenBadgeCredential, Dict[str, Any]]) -> ValidationResult:
    """
    Valide un credential selon la spécification OpenBadge v3
    
    Args:
        credential: Le credential à valider, sous forme d'objet OpenBadgeCredential ou de dictionnaire
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Convertir en dictionnaire si c'est un objet OpenBadgeCredential
    if isinstance(credential, OpenBadgeCredential):
        credential_dict = credential.model_dump(exclude_none=True)
        
        # Convertir les URLs en chaînes
        if 'id' in credential_dict and hasattr(credential_dict['id'], '__str__'):
            credential_dict['id'] = str(credential_dict['id'])
            
        # Convertir les dates en chaînes ISO
        if 'issuanceDate' in credential_dict and isinstance(credential_dict['issuanceDate'], datetime):
            credential_dict['issuanceDate'] = credential_dict['issuanceDate'].isoformat()
        if 'expirationDate' in credential_dict and isinstance(credential_dict['expirationDate'], datetime):
            credential_dict['expirationDate'] = credential_dict['expirationDate'].isoformat()
            
        # Convertir l'URL de l'issuer
        if 'issuer' in credential_dict:
            if isinstance(credential_dict['issuer'], dict) and 'id' in credential_dict['issuer']:
                credential_dict['issuer']['id'] = str(credential_dict['issuer']['id'])
            elif hasattr(credential_dict['issuer'], '__str__'):
                credential_dict['issuer'] = str(credential_dict['issuer'])
                
        # Convertir credentialSubject
        if 'credentialSubject' in credential_dict and isinstance(credential_dict['credentialSubject'], dict):
            if 'id' in credential_dict['credentialSubject'] and hasattr(credential_dict['credentialSubject']['id'], '__str__'):
                credential_dict['credentialSubject']['id'] = str(credential_dict['credentialSubject']['id'])
            
            # Convertir achievement dans credentialSubject
            if 'achievement' in credential_dict['credentialSubject']:
                if isinstance(credential_dict['credentialSubject']['achievement'], dict) and 'id' in credential_dict['credentialSubject']['achievement']:
                    credential_dict['credentialSubject']['achievement']['id'] = str(credential_dict['credentialSubject']['achievement']['id'])
                elif hasattr(credential_dict['credentialSubject']['achievement'], '__str__'):
                    credential_dict['credentialSubject']['achievement'] = str(credential_dict['credentialSubject']['achievement'])
    else:
        credential_dict = credential
    
    # Valider la structure JSON-LD de base
    json_ld_result = validate_json_ld(credential_dict)
    if not json_ld_result.is_valid:
        for error in json_ld_result.errors:
            result.add_error(error)
    for warning in json_ld_result.warnings:
        result.add_warning(warning)
    
    # Vérifier que le type inclut les valeurs requises
    if "type" in credential_dict:
        credential_type = credential_dict["type"]
        if isinstance(credential_type, list):
            if "VerifiableCredential" not in credential_type:
                result.add_warning("Le type devrait inclure 'VerifiableCredential'")
            if "OpenBadgeCredential" not in credential_type:
                result.add_error("Le type doit inclure 'OpenBadgeCredential'")
        else:
            result.add_error("Le type doit être une liste incluant 'VerifiableCredential' et 'OpenBadgeCredential'")
    
    # Vérifier la présence de l'émetteur
    if "issuer" not in credential_dict:
        result.add_warning("L'émetteur (issuer) est normalement obligatoire pour un Credential")
    else:
        # Si l'émetteur est un objet complet, le valider
        issuer = credential_dict["issuer"]
        if isinstance(issuer, dict) and "id" in issuer:
            id_result = validate_url(issuer["id"])
            if not id_result.is_valid:
                for error in id_result.errors:
                    result.add_warning(f"URL de l'émetteur potentiellement invalide: {error}")
            for warning in id_result.warnings:
                result.add_warning(warning)
    
    # Vérifier la présence de la date d'émission
    if "issuanceDate" not in credential_dict:
        result.add_error("La date d'émission (issuanceDate) est obligatoire pour un Credential")
    else:
        # Vérifier le format de la date
        try:
            if isinstance(credential_dict["issuanceDate"], str):
                datetime.fromisoformat(credential_dict["issuanceDate"].replace('Z', '+00:00'))
        except ValueError:
            result.add_warning("La date d'émission devrait être au format ISO 8601")
    
    # Vérifier la date d'expiration si présente
    if "expirationDate" in credential_dict:
        try:
            if isinstance(credential_dict["expirationDate"], str):
                datetime.fromisoformat(credential_dict["expirationDate"].replace('Z', '+00:00'))
        except ValueError:
            result.add_warning("La date d'expiration devrait être au format ISO 8601")
    
    # Vérifier le sujet du credential
    if "credentialSubject" not in credential_dict:
        result.add_warning("Le sujet du credential (credentialSubject) est normalement obligatoire")
    else:
        subject = credential_dict["credentialSubject"]
        if not isinstance(subject, dict):
            result.add_warning("Le sujet du credential devrait être un objet")
        else:
            # Vérifier l'identifiant du sujet
            if "id" not in subject:
                result.add_warning("L'identifiant du sujet (id) est normalement obligatoire")
            
            # Vérifier le type du sujet
            if "type" not in subject:
                result.add_warning("Le type du sujet est normalement obligatoire")
            elif subject["type"] != "AchievementSubject":
                result.add_warning(f"Le type du sujet est '{subject['type']}', 'AchievementSubject' recommandé")
            
            # Vérifier la présence de l'achievement
            if "achievement" not in subject:
                result.add_warning("L'achievement est normalement obligatoire dans le sujet du credential")
            else:
                achievement = subject["achievement"]
                if isinstance(achievement, dict) and "id" in achievement:
                    id_result = validate_url(achievement["id"])
                    if not id_result.is_valid:
                        for error in id_result.errors:
                            result.add_warning(f"URL de l'achievement potentiellement invalide: {error}")
                    for warning in id_result.warnings:
                        result.add_warning(warning)
    
    # Vérifier les preuves si présentes
    if "evidence" in credential_dict and isinstance(credential_dict["evidence"], list):
        for i, evidence in enumerate(credential_dict["evidence"]):
            if not isinstance(evidence, dict):
                result.add_error(f"Preuve #{i+1} doit être un objet")
                continue
            
            if "type" not in evidence:
                result.add_error(f"Preuve #{i+1} doit avoir un type")
            elif evidence["type"] != "Evidence":
                result.add_warning(f"Le type de la preuve #{i+1} est '{evidence['type']}', 'Evidence' recommandé")
            
            if "id" in evidence:
                id_result = validate_url(evidence["id"])
                if not id_result.is_valid:
                    for error in id_result.errors:
                        result.add_error(f"URL de la preuve #{i+1} invalide: {error}")
                for warning in id_result.warnings:
                    result.add_warning(warning)
    
    return result


def validate_endorsement(endorsement: Union[EndorsementCredential, Dict[str, Any]]) -> ValidationResult:
    """
    Valide un endorsement selon la spécification OpenBadge v3
    
    Args:
        endorsement: L'endorsement à valider, sous forme d'objet EndorsementCredential ou de dictionnaire
        
    Returns:
        ValidationResult: Résultat de la validation
    """
    result = ValidationResult()
    
    # Convertir en dictionnaire si c'est un objet EndorsementCredential
    if isinstance(endorsement, EndorsementCredential):
        endorsement_dict = endorsement.model_dump(exclude_none=True)
        
        # Convertir les URLs en chaînes
        if 'id' in endorsement_dict and hasattr(endorsement_dict['id'], '__str__'):
            endorsement_dict['id'] = str(endorsement_dict['id'])
            
        # Convertir les dates en chaînes ISO
        if 'issuanceDate' in endorsement_dict and isinstance(endorsement_dict['issuanceDate'], datetime):
            endorsement_dict['issuanceDate'] = endorsement_dict['issuanceDate'].isoformat()
        if 'expirationDate' in endorsement_dict and isinstance(endorsement_dict['expirationDate'], datetime):
            endorsement_dict['expirationDate'] = endorsement_dict['expirationDate'].isoformat()
            
        # Convertir l'URL de l'issuer
        if 'issuer' in endorsement_dict:
            if isinstance(endorsement_dict['issuer'], dict) and 'id' in endorsement_dict['issuer']:
                endorsement_dict['issuer']['id'] = str(endorsement_dict['issuer']['id'])
            elif hasattr(endorsement_dict['issuer'], '__str__'):
                endorsement_dict['issuer'] = str(endorsement_dict['issuer'])
                
        # Convertir credentialSubject
        if 'credentialSubject' in endorsement_dict and isinstance(endorsement_dict['credentialSubject'], dict):
            if 'id' in endorsement_dict['credentialSubject'] and hasattr(endorsement_dict['credentialSubject']['id'], '__str__'):
                endorsement_dict['credentialSubject']['id'] = str(endorsement_dict['credentialSubject']['id'])
    else:
        endorsement_dict = endorsement
    
    # Valider la structure JSON-LD de base
    json_ld_result = validate_json_ld(endorsement_dict)
    if not json_ld_result.is_valid:
        for error in json_ld_result.errors:
            result.add_error(error)
    for warning in json_ld_result.warnings:
        result.add_warning(warning)
    
    # Vérifier que le type inclut les valeurs requises
    if "type" in endorsement_dict:
        endorsement_type = endorsement_dict["type"]
        if isinstance(endorsement_type, list):
            if "VerifiableCredential" not in endorsement_type:
                result.add_warning("Le type devrait inclure 'VerifiableCredential'")
            if "EndorsementCredential" not in endorsement_type:
                result.add_error("Le type doit inclure 'EndorsementCredential'")
        else:
            result.add_error("Le type doit être une liste incluant 'VerifiableCredential' et 'EndorsementCredential'")
    
    # Vérifier la présence de l'émetteur
    if "issuer" not in endorsement_dict:
        result.add_error("L'émetteur (issuer) est obligatoire pour un Endorsement")
    else:
        # Si l'émetteur est un objet complet, le valider
        issuer = endorsement_dict["issuer"]
        if isinstance(issuer, dict) and "id" in issuer:
            id_result = validate_url(issuer["id"])
            if not id_result.is_valid:
                for error in id_result.errors:
                    result.add_warning(f"URL de l'émetteur potentiellement invalide: {error}")
            for warning in id_result.warnings:
                result.add_warning(warning)
    
    # Vérifier la présence de la date d'émission
    if "issuanceDate" not in endorsement_dict:
        result.add_error("La date d'émission (issuanceDate) est obligatoire pour un Endorsement")
    else:
        # Vérifier le format de la date
        try:
            if isinstance(endorsement_dict["issuanceDate"], str):
                datetime.fromisoformat(endorsement_dict["issuanceDate"].replace('Z', '+00:00'))
        except ValueError:
            result.add_error("La date d'émission doit être au format ISO 8601")
    
    # Vérifier la date d'expiration si présente
    if "expirationDate" in endorsement_dict:
        try:
            if isinstance(endorsement_dict["expirationDate"], str):
                datetime.fromisoformat(endorsement_dict["expirationDate"].replace('Z', '+00:00'))
        except ValueError:
            result.add_warning("La date d'expiration devrait être au format ISO 8601")
    
    # Vérifier le sujet de l'endorsement
    if "credentialSubject" not in endorsement_dict:
        result.add_error("Le sujet de l'endorsement (credentialSubject) est obligatoire")
    else:
        subject = endorsement_dict["credentialSubject"]
        if not isinstance(subject, dict):
            result.add_error("Le sujet de l'endorsement doit être un objet")
        else:
            # Vérifier l'identifiant du sujet
            if "id" not in subject:
                result.add_error("L'identifiant du sujet (id) est obligatoire")
            else:
                id_result = validate_url(subject["id"])
                if not id_result.is_valid:
                    for error in id_result.errors:
                        result.add_error(f"URL du sujet invalide: {error}")
                for warning in id_result.warnings:
                    result.add_warning(warning)
            
            # Vérifier le type du sujet
            if "type" not in subject:
                result.add_error("Le type du sujet est obligatoire")
    
    return result
