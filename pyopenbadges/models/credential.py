"""
Module définissant le modèle OpenBadgeCredential selon la spécification OpenBadge v3.0

Un OpenBadgeCredential représente l'attribution d'un badge spécifique à un destinataire.
C'est l'équivalent de l'Assertion dans OpenBadge v2.
"""

from typing import Optional, List, Dict, Any, Union, Annotated, TYPE_CHECKING, Literal
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID

# Utilisation de TYPE_CHECKING pour éviter les importations circulaires
if TYPE_CHECKING:
    from pyopenbadges.crypto.keys import PrivateKey, PublicKey

from .profile import Profile
from .achievement import Achievement


class CredentialSchema(BaseModel):
    """
    Classe représentant un schéma de validation pour un credential selon la spécification OpenBadge v3.0
    
    Un credentialSchema définit la structure et les règles de validation pour un type de credential.
    Il peut être utilisé pour vérifier qu'un credential est conforme à un schéma spécifique.
    """
    id: HttpUrl  # URI du schéma de validation
    type: str = "JsonSchemaValidator2019"  # Type de validateur de schéma
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "https://w3id.org/vc/status-list/2021/v1",
                    "type": "JsonSchemaValidator2019"
                }
            ]
        }
    }


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
    credentialSchema: Optional[CredentialSchema] = None  # Schéma de validation du credential
    
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
    
    def validate_schema(self) -> bool:
        """
        Valide le credential selon le schéma défini dans credentialSchema
        
        Cette méthode vérifie que le credential est conforme au schéma spécifié.
        Si aucun schéma n'est défini, la validation est considérée comme réussie.
        
        Returns:
            bool: True si le credential est conforme au schéma, False sinon
        
        Raises:
            ValueError: Si le schéma n'est pas accessible ou valide
        """
        if not self.credentialSchema:
            # Si aucun schéma n'est défini, le credential est considéré comme valide
            return True
            
        # Dans une implémentation complète, cette méthode devrait :
        # 1. Récupérer le schéma à partir de l'URL dans credentialSchema.id
        # 2. Valider le credential selon ce schéma
        # Pour l'instant, nous vérifions simplement que le type est correctement défini
        if self.credentialSchema.type == "JsonSchemaValidator2019":
            # Pour une validation réelle, nous devrions utiliser jsonschema
            # Exemple d'implémentation future:
            # import jsonschema
            # import requests
            # schema_response = requests.get(str(self.credentialSchema.id))
            # if schema_response.status_code == 200:
            #     schema = schema_response.json()
            #     try:
            #         jsonschema.validate(instance=self.model_dump(exclude_none=True), schema=schema)
            #         return True
            #     except jsonschema.exceptions.ValidationError:
            #         return False
            # raise ValueError(f"Impossible de récupérer le schéma: {self.credentialSchema.id}")
            return True
        else:
            raise ValueError(f"Type de schéma non pris en charge: {self.credentialSchema.type}")

    def is_valid(self) -> bool:
        """
        Vérifie si le credential est valide (non expiré et non révoqué)
        
        Cette méthode ne vérifie pas la signature cryptographique.
        Pour vérifier la signature, utilisez la méthode verify_signature().
        
        Returns:
            bool: True si le credential est valide, False sinon
        """
        if self.revoked:
            return False
        
        if self.expirationDate and self.expirationDate < datetime.now():
            return False
        
        # Vérifier la conformité au schéma
        try:
            if not self.validate_schema():
                return False
        except ValueError:
            # En cas d'erreur lors de la validation du schéma, on considère le credential comme invalide
            return False
            
        return True
    
    def sign(self, private_key: 'PrivateKey', verification_method: Union[str, HttpUrl]) -> 'OpenBadgeCredential':
        """
        Signe le credential avec la clé privée fournie.
        
        Args:
            private_key: La clé privée pour signer le credential
            verification_method: L'URL de la méthode de vérification (clé publique)
        
        Returns:
            OpenBadgeCredential: Le credential signé
        """
        # Import ici pour éviter les importations circulaires
        from pyopenbadges.crypto.signing import sign_credential as crypto_sign_credential
        
        return crypto_sign_credential(
            credential=self,
            private_key=private_key,
            verification_method=verification_method
        )
    
    def verify_signature(self, public_key: 'PublicKey') -> bool:
        """
        Vérifie la signature cryptographique du credential.
        
        Args:
            public_key: La clé publique pour vérifier la signature
        
        Returns:
            bool: True si la signature est valide, False sinon
        
        Raises:
            ValueError: Si le credential n'a pas de preuve
        """
        if self.proof is None:
            raise ValueError("Le credential ne possède pas de preuve")
        
        # Import ici pour éviter les importations circulaires
        from pyopenbadges.crypto.verification import verify_credential as crypto_verify_credential
        
        return crypto_verify_credential(
            credential=self,
            public_key=public_key
        )
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convertit le credential en format JSON-LD compatible avec OpenBadge v3.0
        
        Cette méthode ajoute les contextes JSON-LD nécessaires pour la compatibilité
        avec les outils de vérification OpenBadge et les systèmes Verifiable Credentials.
        
        Les contextes inclus sont :
        - https://www.w3.org/2018/credentials/v1 : Le vocabulaire principal de W3C Verifiable Credentials
          qui définit les termes de base comme VerifiableCredential, credentialSubject, issuer, etc.
        - https://w3id.org/openbadges/v3 : Le vocabulaire Open Badges v3.0 qui ajoute les termes
          spécifiques aux badges numériques comme Achievement, Profile, AchievementSubject, etc.
        
        En ajoutant ces contextes, le JSON-LD résultant peut être:
        1. Interprété correctement par les systèmes compatibles avec Open Badges v3.0
        2. Validé contre les schémas officiels
        3. Vérifié cryptographiquement (si signé)
        4. Échangé entre différents systèmes de manière interopérable
        
        Note: Pour une conformité totale, assurez-vous que tous les champs obligatoires sont renseignés
        selon la spécification (https://www.imsglobal.org/spec/ob/v3p0/).
        
        Returns:
            Dict: Le credential au format JSON-LD avec les contextes appropriés
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
        
        # Ajouter le schéma de credential s'il existe
        if self.credentialSchema:
            if 'credentialSchema' not in data:
                data['credentialSchema'] = {}
            data['credentialSchema']['id'] = str(self.credentialSchema.id)
            data['credentialSchema']['type'] = self.credentialSchema.type
            
        # Ajout des contextes JSON-LD requis par la spécification Open Badges v3.0
        # Le premier contexte définit le vocabulaire de base des Verifiable Credentials
        # Le second ajoute le vocabulaire spécifique à Open Badges v3.0
        data["@context"] = [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/openbadges/v3"
            # Ajoutez ici d'autres contextes personnalisés si nécessaire
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
