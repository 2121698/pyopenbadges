"""
Module définissant le modèle EndorsementCredential selon la spécification OpenBadge v3.0

Un EndorsementCredential représente une recommandation ou validation d'un élément 
(badge, émetteur, assertion) par un tiers.
"""

from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID

from .profile import Profile


class EndorsementSubject(BaseModel):
    """
    Classe représentant le sujet d'un endorsement
    
    Le sujet peut être un badge, un émetteur ou une assertion
    """
    id: HttpUrl  # URI de l'élément endorsé
    type: str  # Type de l'élément endorsé (Achievement, Profile, etc.)
    endorsementComment: Optional[str] = None  # Commentaire sur l'endorsement
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://example.org/badges/1",
                    "type": "Achievement",
                    "endorsementComment": "Ce badge répond aux critères de notre organisation et est reconnu comme valide."
                }
            ]
        }
    }


class EndorsementCredential(BaseModel):
    """
    Classe représentant un EndorsementCredential dans le standard OpenBadge v3
    
    Un EndorsementCredential est une recommandation ou validation d'un élément
    (badge, émetteur, assertion) par un tiers.
    """
    # Champs obligatoires
    id: HttpUrl  # URI unique qui identifie l'endorsement
    type: List[str] = ["VerifiableCredential", "EndorsementCredential"]  # Les types requis
    issuer: Union[HttpUrl, Dict[str, Any], Profile]  # L'émetteur de l'endorsement
    issuanceDate: datetime  # Date d'émission au format ISO
    credentialSubject: EndorsementSubject  # Information sur l'élément endorsé
    
    # Champs optionnels
    name: Optional[str] = None  # Nom de l'endorsement
    description: Optional[str] = None  # Description de l'endorsement
    proof: Optional[Dict[str, Any]] = None  # Preuve cryptographique de validité
    expirationDate: Optional[datetime] = None  # Date d'expiration
    
    @field_validator('type')
    def validate_type(cls, v):
        """
        Valide que le champ 'type' inclut les types requis
        
        Un EndorsementCredential doit avoir les types 'VerifiableCredential' et 'EndorsementCredential'
        """
        if not isinstance(v, list):
            v = [v]
        if "VerifiableCredential" not in v:
            raise ValueError("Le type doit inclure 'VerifiableCredential'")
        if "EndorsementCredential" not in v:
            raise ValueError("Le type doit inclure 'EndorsementCredential'")
        return v
    
    def is_valid(self) -> bool:
        """
        Vérifie si l'endorsement est valide (non expiré)
        
        Returns:
            bool: True si l'endorsement est valide, False sinon
        """
        if self.expirationDate and self.expirationDate < datetime.now():
            return False
        
        return True
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convertit l'endorsement en format JSON-LD compatible avec OpenBadge v3
        
        Cette méthode ajoute le contexte JSON-LD nécessaire pour la compatibilité
        avec les outils de vérification OpenBadge.
        
        Returns:
            Dict: L'endorsement au format JSON-LD
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
                    "id": "https://example.org/endorsements/1",
                    "type": ["VerifiableCredential", "EndorsementCredential"],
                    "issuer": {
                        "id": "https://example.org/endorsers/1",
                        "type": "Profile"
                    },
                    "issuanceDate": "2023-01-02T00:00:00Z",
                    "credentialSubject": {
                        "id": "https://example.org/badges/1",
                        "type": "Achievement",
                        "endorsementComment": "Ce badge répond aux critères de notre organisation."
                    }
                }
            ]
        }
    }
