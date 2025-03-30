"""
Module définissant le modèle OpenBadgeCredential selon la spécification OpenBadge v3.0

Un OpenBadgeCredential représente l'attribution d'un badge spécifique à un destinataire.
C'est l'équivalent de l'Assertion dans OpenBadge v2.
"""

from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID

from .profile import Profile
from .achievement import Achievement


class Evidence(BaseModel):
    """
    Classe représentant une preuve justifiant l'obtention d'un badge
    
    Une preuve peut être un document, un projet, une évaluation, etc.
    """
    id: Optional[HttpUrl] = None  # URL optionnelle vers la preuve
    type: str = "Evidence"
    name: Optional[str] = None  # Titre de la preuve
    description: Optional[str] = None  # Description de la preuve
    narrative: Optional[str] = None  # Explication détaillée
    genre: Optional[str] = None  # Type de preuve
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://example.org/evidence/12345",
                    "type": "Evidence",
                    "name": "Projet Python",
                    "description": "Application web développée en Python",
                    "narrative": "Le candidat a développé une application web en utilisant Django et htmx.",
                    "genre": "Projet"
                }
            ]
        }
    }


class AchievementSubject(BaseModel):
    """
    Classe représentant le sujet d'un credential, c'est-à-dire le destinataire 
    et l'achievement qui lui est attribué
    """
    id: str  # Identifiant du destinataire (peut être une URL, un DID, etc.)
    type: str = "AchievementSubject"
    achievement: Union[HttpUrl, Dict[str, Any], Achievement]  # L'achievement attribué
    name: Optional[str] = None  # Nom du destinataire (optionnel)
    
    @field_validator('achievement')
    def validate_achievement(cls, v):
        """Valide que l'achievement est correctement référencé"""
        if isinstance(v, Achievement):
            return v
        elif isinstance(v, dict) and "id" in v:
            return v
        elif isinstance(v, str) or isinstance(v, HttpUrl):
            return v
        else:
            raise ValueError("L'achievement doit être une URL, un objet Achievement ou un dictionnaire avec un champ 'id'")
        return v


class Proof(BaseModel):
    """
    Classe représentant une preuve cryptographique de validité du credential
    
    Basée sur les standards de Verifiable Credentials
    """
    type: str  # Type de preuve (ex: Ed25519Signature2020)
    created: datetime  # Date de création de la preuve
    verificationMethod: HttpUrl  # Méthode de vérification
    proofPurpose: str = "assertionMethod"  # But de la preuve
    proofValue: str  # Valeur de la preuve (signature)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "Ed25519Signature2020",
                    "created": "2023-01-01T00:00:00Z",
                    "verificationMethod": "https://example.org/issuers/1/keys/1",
                    "proofPurpose": "assertionMethod",
                    "proofValue": "z58DAdFfa9SkqZMVPxAQpic7ndSayn5ADzJWiy6dVmSfGeRTm35kVcqp9p2C4QrhUBSK2R"
                }
            ]
        }
    }


class OpenBadgeCredential(BaseModel):
    """
    Classe représentant un OpenBadgeCredential dans le standard OpenBadge v3
    
    Un OpenBadgeCredential est l'équivalent de l'Assertion dans OpenBadge v2.
    Il représente l'attribution d'un badge spécifique à un destinataire.
    """
    # Champs obligatoires
    id: HttpUrl  # URI unique qui identifie le credential
    type: List[str] = ["VerifiableCredential", "OpenBadgeCredential"]  # Les types requis
    issuer: Union[HttpUrl, Dict[str, Any], Profile]  # L'émetteur du credential
    issuanceDate: datetime  # Date d'émission au format ISO
    credentialSubject: AchievementSubject  # Information sur le destinataire et l'achievement
    
    # Champs optionnels
    name: Optional[str] = None  # Nom du credential
    description: Optional[str] = None  # Description du credential
    proof: Optional[Proof] = None  # Preuve cryptographique de validité
    expirationDate: Optional[datetime] = None  # Date d'expiration
    revoked: Optional[bool] = None  # Indique si le credential a été révoqué
    revocationReason: Optional[str] = None  # Raison de la révocation
    evidence: Optional[List[Evidence]] = None  # Preuves justifiant l'obtention
    
    @field_validator('type')
    def validate_type(cls, v):
        """
        Valide que le champ 'type' inclut les types requis
        
        Un OpenBadgeCredential doit avoir les types 'VerifiableCredential' et 'OpenBadgeCredential'
        """
        if not isinstance(v, list):
            v = [v]
        if "VerifiableCredential" not in v:
            raise ValueError("Le type doit inclure 'VerifiableCredential'")
        if "OpenBadgeCredential" not in v:
            raise ValueError("Le type doit inclure 'OpenBadgeCredential'")
        return v
    
    @field_validator('issuer')
    def validate_issuer(cls, v):
        """Valide que l'émetteur est correctement référencé"""
        # Si l'issuer est un dictionnaire, on s'assure qu'il a les champs nécessaires
        if isinstance(v, dict) and 'type' in v and v['type'] == 'Profile' and 'id' in v and 'name' not in v:
            v['name'] = "Unnamed Issuer"  # Ajouter un nom par défaut
        return v
    
    def is_valid(self) -> bool:
        """
        Vérifie si le credential est valide (non expiré et non révoqué)
        
        Returns:
            bool: True si le credential est valide, False sinon
        """
        if self.revoked:
            return False
        
        if self.expirationDate and self.expirationDate < datetime.now():
            return False
        
        return True
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convertit le credential en format JSON-LD compatible avec OpenBadge v3
        
        Cette méthode ajoute le contexte JSON-LD nécessaire pour la compatibilité
        avec les outils de vérification OpenBadge.
        
        Returns:
            Dict: Le credential au format JSON-LD
        """
        data = self.model_dump(exclude_none=True)
        
        # Convertir les champs HttpUrl en chaînes de caractères
        if 'id' in data and hasattr(data['id'], '__str__'):
            data['id'] = str(data['id'])
            
        # Convertir les dates en chaînes ISO
        if 'issuanceDate' in data and isinstance(data['issuanceDate'], datetime):
            data['issuanceDate'] = data['issuanceDate'].isoformat()
        if 'expirationDate' in data and isinstance(data['expirationDate'], datetime):
            data['expirationDate'] = data['expirationDate'].isoformat()
            
        # Convertir l'émetteur en référence si c'est un objet Profile
        if isinstance(self.issuer, Profile):
            data["issuer"] = {
                "id": str(self.issuer.id),
                "type": self.issuer.type
            }
        elif 'issuer' in data and isinstance(data['issuer'], dict) and 'id' in data['issuer']:
            data['issuer']['id'] = str(data['issuer']['id'])
        
        # Convertir l'achievement en référence si c'est un objet Achievement
        if isinstance(self.credentialSubject.achievement, Achievement):
            data["credentialSubject"]["achievement"] = {
                "id": str(self.credentialSubject.achievement.id),
                "type": "Achievement"
            }
        elif 'credentialSubject' in data and 'achievement' in data['credentialSubject']:
            if isinstance(data['credentialSubject']['achievement'], dict) and 'id' in data['credentialSubject']['achievement']:
                data['credentialSubject']['achievement']['id'] = str(data['credentialSubject']['achievement']['id'])
            
        # Convertir l'id du credentialSubject en chaîne si nécessaire
        if 'credentialSubject' in data and 'id' in data['credentialSubject'] and hasattr(data['credentialSubject']['id'], '__str__'):
            data['credentialSubject']['id'] = str(data['credentialSubject']['id'])
            
        data["@context"] = [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/openbadges/v3"
        ]
        
        return data

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://example.org/assertions/1",
                    "type": ["VerifiableCredential", "OpenBadgeCredential"],
                    "issuer": {
                        "id": "https://example.org/issuers/1",
                        "type": "Profile"
                    },
                    "issuanceDate": "2023-01-01T00:00:00Z",
                    "credentialSubject": {
                        "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
                        "type": "AchievementSubject",
                        "achievement": {
                            "id": "https://example.org/badges/1",
                            "type": "Achievement"
                        }
                    }
                }
            ]
        }
    }
