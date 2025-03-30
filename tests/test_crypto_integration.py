"""
Test d'intégration pour les fonctionnalités cryptographiques de PyOpenBadges

Ce test simule un scénario complet d'utilisation des fonctionnalités cryptographiques :
1. Génération de clés
2. Création d'un credential
3. Signature du credential
4. Vérification de la signature
5. Détection de falsification
"""

import pytest
import json
from datetime import datetime

from pyopenbadges.crypto import generate_keypair
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject


class TestCryptoIntegration:
    """Test d'intégration des fonctionnalités cryptographiques"""

    def test_complete_crypto_workflow(self):
        """
        Test du flux complet de travail avec les fonctionnalités cryptographiques :
        génération de clés, création, signature et vérification d'un credential
        """
        # 1. Générer une paire de clés Ed25519
        keypair = generate_keypair(algorithm="Ed25519")
        assert keypair.algorithm == "Ed25519"
        assert keypair.private_key is not None
        assert keypair.public_key is not None

        # 2. Créer un émetteur (Profile)
        issuer = Profile(
            id="https://example.org/issuers/1",
            type="Profile",
            name="Université Exemple",
            description="Une université fictive pour l'exemple",
            url="https://example.org"
        )
        assert issuer.name == "Université Exemple"

        # 3. Créer un badge (Achievement)
        badge = Achievement(
            id="https://example.org/badges/python-dev",
            type="Achievement",
            name="Développeur Python Certifié",
            description="Ce badge certifie que le détenteur maîtrise le développement en Python",
            issuer=issuer
        )
        assert badge.name == "Développeur Python Certifié"

        # 4. Créer un credential
        credential = OpenBadgeCredential(
            id="https://example.org/credentials/12345",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer=issuer,
            issuanceDate=datetime.now(),
            credentialSubject=AchievementSubject(
                id="did:example:recipient123",
                type="AchievementSubject",
                name="Jean Dupont",
                achievement=badge
            )
        )
        assert credential.credentialSubject.name == "Jean Dupont"
        assert credential.proof is None  # Pas encore signé

        # 5. Signer le credential
        signed_credential = credential.sign(
            private_key=keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )
        assert signed_credential.proof is not None
        assert signed_credential.proof.type == "Ed25519Signature2020"
        assert str(signed_credential.proof.verificationMethod) == "https://example.org/issuers/1/keys/1"
        assert len(signed_credential.proof.proofValue) > 0

        # 6. Vérifier la signature
        is_valid = signed_credential.verify_signature(
            public_key=keypair.public_key
        )
        assert is_valid is True

        # 7. Créer une copie falsifiée
        tampered_credential = signed_credential.model_copy(deep=True)
        tampered_credential.credentialSubject.id = "did:example:hacker456"
        
        # Vérifier que les IDs sont différents
        assert signed_credential.credentialSubject.id == "did:example:recipient123"
        assert tampered_credential.credentialSubject.id == "did:example:hacker456"

        # 8. Vérifier la signature de la copie falsifiée
        is_tampered_valid = tampered_credential.verify_signature(
            public_key=keypair.public_key
        )
        assert is_tampered_valid is False

        # 9. Convertir en JSON-LD
        json_ld = signed_credential.to_json_ld()
        assert isinstance(json_ld, dict)
        assert "@context" in json_ld
        assert "id" in json_ld
        assert "proof" in json_ld

    def test_json_serialization(self):
        """Test de la sérialisation JSON d'un credential signé"""
        # Classe pour encoder les objets datetime et Pydantic en JSON
        class CustomJSONEncoder(json.JSONEncoder):
            """Encodeur JSON personnalisé pour gérer les objets datetime et Pydantic"""
            def default(self, obj):
                # Gérer les objets datetime
                if isinstance(obj, datetime):
                    return obj.isoformat()
                
                # Gérer les objets Pydantic (comme HttpUrl)
                if hasattr(obj, "__str__"):
                    try:
                        return str(obj)
                    except:
                        pass
                        
                # Gérer les objets Pydantic BaseModel
                if hasattr(obj, "model_dump"):
                    try:
                        return obj.model_dump()
                    except:
                        pass
                        
                return super().default(obj)

        # 1. Générer une paire de clés et créer un credential
        keypair = generate_keypair()
        issuer = Profile(id="https://example.org/issuers/1", type="Profile", name="Test Issuer")
        badge = Achievement(id="https://example.org/badges/1", type="Achievement", name="Test Badge", issuer=issuer)
        credential = OpenBadgeCredential(
            id="https://example.org/credentials/1",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer=issuer,
            issuanceDate=datetime.now(),
            credentialSubject=AchievementSubject(
                id="did:example:recipient",
                type="AchievementSubject",
                achievement=badge
            )
        )

        # 2. Signer le credential
        signed_credential = credential.sign(
            private_key=keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )

        # 3. Convertir en JSON-LD
        json_ld = signed_credential.to_json_ld()

        # 4. Sérialiser en JSON
        json_str = json.dumps(json_ld, cls=CustomJSONEncoder)
        
        # 5. Vérifier que la sérialisation a réussi
        assert isinstance(json_str, str)
        assert len(json_str) > 0
        
        # 6. Vérifier que le JSON peut être désérialisé
        parsed_json = json.loads(json_str)
        assert isinstance(parsed_json, dict)
        assert "id" in parsed_json
        assert "proof" in parsed_json
