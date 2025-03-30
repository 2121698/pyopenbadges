# TODO: Implémentation du Support JWT dans PyOpenBadges

*Date de création: 30/03/2025*

## Contexte

La spécification OpenBadge v3.0 indique explicitement dans la section 8.2 (https://www.imsglobal.org/spec/ob/v3p0/#jwt-proof) que le format JWT peut être utilisé comme alternative aux Linked Data Proofs pour garantir l'authenticité et l'intégrité des badges. Bien que PyOpenBadges implémente déjà le support pour les Linked Data Proofs, l'ajout du support JWT augmenterait considérablement la compatibilité avec d'autres écosystèmes.

> **Commentaire de l'ingénieur IMS Global**: 
> 
> "L'intégration des JWT dans la spécification OpenBadge v3.0 n'était pas un choix anodin. Nous avons observé que de nombreux systèmes d'identité numérique et de vérification s'appuient fortement sur les JWT (JSON Web Tokens). En incluant explicitement cette option dans la spécification, nous facilitons l'adoption de la norme par un plus grand nombre d'acteurs et augmentons l'interopérabilité avec les écosystèmes existants. Le format JWT offre également l'avantage d'être compact et facilement transportable, ce qui est particulièrement utile pour les environnements mobiles et les applications web modernes."

## Implémentation technique

### 1. Création d'une classe JwtProof

```python
from typing import Optional, Dict, Any, Union
from datetime import datetime
import jwt
from pydantic import BaseModel, Field, HttpUrl

class JwtProof(BaseModel):
    """
    Représente une preuve au format JWT pour un OpenBadgeCredential
    
    Implémente la section 8.2 de la spécification OpenBadge v3.0
    """
    type: str = "JwtProof2020"
    jwt: str
    
    @classmethod
    def create(cls, credential_data: Dict[str, Any], private_key: str, 
               algorithm: str = "RS256", key_id: Optional[str] = None) -> 'JwtProof':
        """
        Crée une preuve JWT pour un credential
        
        Args:
            credential_data: Données du credential à signer
            private_key: Clé privée au format PEM ou JWK
            algorithm: Algorithme de signature (par défaut RS256)
            key_id: Identifiant de la clé utilisée
            
        Returns:
            JwtProof: L'objet preuve JWT créé
        """
        header = {
            "alg": algorithm,
            "typ": "JWT"
        }
        
        if key_id:
            header["kid"] = key_id
            
        # Création de la signature JWT
        token = jwt.encode(
            payload=credential_data,
            key=private_key,
            algorithm=algorithm,
            headers=header
        )
        
        return cls(type="JwtProof2020", jwt=token)
    
    def verify(self, public_key: str, algorithms: Union[str, list] = None) -> Dict[str, Any]:
        """
        Vérifie la signature JWT et retourne le contenu décodé
        
        Args:
            public_key: Clé publique pour vérifier la signature
            algorithms: Liste des algorithmes acceptés
            
        Returns:
            Dict: Le contenu décodé du JWT
            
        Raises:
            jwt.exceptions.InvalidSignatureError: Si la signature est invalide
            jwt.exceptions.ExpiredSignatureError: Si le token est expiré
            jwt.exceptions.DecodeError: Si le token ne peut pas être décodé
        """
        if algorithms is None:
            algorithms = ["RS256", "ES256", "EdDSA"]
            
        return jwt.decode(
            jwt=self.jwt,
            key=public_key,
            algorithms=algorithms,
            options={"verify_signature": True}
        )
```

> **Commentaire de l'ingénieur IMS Global**: 
> 
> "Pour la compatibilité maximale, nous recommandons de supporter au minimum les algorithmes RS256, ES256 et EdDSA, car ils sont largement adoptés dans l'écosystème des identités numériques. Le type 'JwtProof2020' est conforme aux pratiques actuelles des Verifiable Credentials, mais pensez à surveiller les évolutions des standards W3C dans ce domaine qui pourraient influencer les prochaines versions de la spécification OpenBadge."

### 2. Mise à jour de la classe OpenBadgeCredential

```python
# Dans pyopenbadges/models/credential.py

from typing import Optional, Union
from .proof import Proof, JwtProof  # Ajout de l'import JwtProof

class OpenBadgeCredential(BaseModel):
    # ... code existant ...
    
    # Modifier le champ proof pour supporter JwtProof
    proof: Optional[Union[Proof, JwtProof]] = None
    
    def sign_jwt(self, private_key: str, algorithm: str = "RS256", 
                 key_id: Optional[str] = None) -> 'OpenBadgeCredential':
        """
        Signe le credential avec la clé privée fournie au format JWT
        
        Args:
            private_key: La clé privée pour signer le credential
            algorithm: L'algorithme de signature à utiliser
            key_id: L'identifiant de la clé à inclure dans l'en-tête JWT
            
        Returns:
            OpenBadgeCredential: Le credential signé avec une preuve JWT
        """
        # Convertir d'abord en JSON-LD sans la preuve
        credential_data = self.model_dump(exclude={"proof"})
        
        # Créer la preuve JWT
        jwt_proof = JwtProof.create(
            credential_data=credential_data,
            private_key=private_key,
            algorithm=algorithm,
            key_id=key_id
        )
        
        # Créer une copie du credential avec la preuve
        signed_credential = self.model_copy()
        signed_credential.proof = jwt_proof
        
        return signed_credential
    
    def verify_jwt(self, public_key: str, algorithms: Union[str, list] = None) -> bool:
        """
        Vérifie la preuve JWT du credential
        
        Args:
            public_key: La clé publique pour vérifier la signature
            algorithms: Les algorithmes acceptés pour la vérification
            
        Returns:
            bool: True si la signature est valide, False sinon
            
        Raises:
            ValueError: Si le credential n'a pas de preuve JWT
        """
        if self.proof is None or not isinstance(self.proof, JwtProof):
            raise ValueError("Le credential ne possède pas de preuve JWT")
            
        try:
            decoded = self.proof.verify(public_key, algorithms)
            
            # Vérifier que le contenu décodé correspond au credential
            credential_data = self.model_dump(exclude={"proof"})
            
            # Vérification des champs essentiels
            return (decoded.get("id") == credential_data.get("id") and
                    decoded.get("type") == credential_data.get("type"))
        except Exception as e:
            return False
```

> **Commentaire de l'ingénieur IMS Global**: 
> 
> "Lors du développement de la spécification v3.0, nous avons accordé une attention particulière à la rétrocompatibilité et à l'interopérabilité. L'implémentation dual-mode (Linked Data Proofs et JWT) est exactement ce que nous avions en tête. Notez que pour une conformité totale, votre implémentation devrait permettre la sérialisation complète du credential en JWT (pas seulement la preuve), comme indiqué dans la section 8.2.3. Cela permet à des systèmes tiers de vérifier le badge sans avoir besoin de comprendre le format JSON-LD."

## Étapes d'implémentation

1. **Dépendances**
   - Ajouter PyJWT et cryptography au fichier pyproject.toml
   ```toml
   [tool.poetry.dependencies]
   python = "^3.8"
   pydantic = "^2.0.0"
   pyjwt = "^2.6.0"
   cryptography = "^40.0.0"  # Pour les algorithmes de chiffrement
   ```

2. **Structure de fichiers**
   - Créer ou mettre à jour `pyopenbadges/models/proof.py` pour inclure JwtProof
   - Mettre à jour `pyopenbadges/models/__init__.py` pour exposer JwtProof
   - Mettre à jour `pyopenbadges/models/credential.py` pour intégrer le support JWT

3. **Tests**
   - Créer `tests/test_jwt_proof.py` avec des tests couvrant:
     - Création de JwtProof
     - Signature d'un credential avec JWT
     - Vérification de la signature JWT
     - Tests avec différents algorithmes (RS256, ES256, EdDSA)
     - Cas d'erreur et exceptions

4. **Documentation**
   - Mettre à jour le README.md pour mentionner le support JWT
   - Ajouter un nouveau tutoriel: TUTORIAL.jwt.md
   - Mettre à jour la documentation existante pour inclure des exemples JWT

> **Commentaire de l'ingénieur IMS Global**: 
> 
> "Un aspect souvent négligé dans les implémentations de la spécification concerne le support des différentes transformations entre formats (JSON-LD ⟷ JWT). Pour une implémentation robuste, assurez-vous de tester non seulement la création et la vérification des JWT, mais aussi la transformation bidirectionnelle entre les formats. Cela est essentiel pour garantir l'interopérabilité avec les différents systèmes de l'écosystème. Les développeurs apprécieront également des exemples clairs montrant comment ces transformations s'intègrent dans des flux d'utilisation courants."

## Considérations de sécurité

1. **Gestion des clés**
   - Fournir des utilitaires pour générer des paires de clés compatibles JWT
   - Documenter les bonnes pratiques pour la rotation et le stockage sécurisé des clés

2. **Algorithmes recommandés**
   - Documenter les algorithmes à privilégier (RS256, ES256, EdDSA)
   - Inclure des avertissements concernant les algorithmes moins sécurisés (e.g., HS256 sans contexte approprié)

3. **Validation des champs critiques**
   - S'assurer que la vérification JWT comprend la validation de l'émetteur, de l'expiration et de l'audience

> **Commentaire de l'ingénieur IMS Global**: 
> 
> "La gestion des clés cryptographiques est un aspect critique dans tout système utilisant des JWT. Notre expérience montre que c'est souvent le maillon faible des implémentations. Au-delà de la simple signature et vérification, envisagez de fournir des utilitaires pour la gestion du cycle de vie des clés (génération, rotation, révocation) et documentez clairement les meilleures pratiques. La sécurité de l'écosystème des badges dépend de l'implémentation correcte de ces aspects par chaque acteur."

## Ressources et références

1. Spécification OpenBadge v3.0:
   - https://www.imsglobal.org/spec/ob/v3p0/
   - Section JWT spécifique: https://www.imsglobal.org/spec/ob/v3p0/#jwt-proof

2. Standards JWT:
   - RFC 7519 (JWT): https://tools.ietf.org/html/rfc7519
   - RFC 7515 (JWS): https://tools.ietf.org/html/rfc7515
   - RFC 7518 (JWA): https://tools.ietf.org/html/rfc7518

3. Bibliothèques Python:
   - PyJWT: https://pyjwt.readthedocs.io/
   - cryptography: https://cryptography.io/

> **Commentaire final de l'ingénieur IMS Global**: 
> 
> "L'implémentation du support JWT dans votre bibliothèque PyOpenBadges est une étape importante pour renforcer l'écosystème OpenBadge. En tant qu'organisme de standardisation, nous sommes ravis de voir des développeurs investir dans l'implémentation complète de la spécification, y compris les fonctionnalités avancées comme le support JWT.
> 
> Une suggestion pour l'avenir : envisagez également d'implémenter la section 8.3 de la spécification qui concerne les 'Embedded Proofs'. Cette approche permet d'intégrer des preuves directement dans des formats comme PNG ou SVG, ce qui est particulièrement utile pour les badges visuels.
> 
> Merci de contribuer à l'écosystème OpenBadge et n'hésitez pas à nous contacter via nos canaux officiels pour toute clarification sur la spécification."
