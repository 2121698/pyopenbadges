"""
Tests pour les fonctionnalités cryptographiques intégrées dans OpenBadgeCredential
"""

import pytest
from datetime import datetime
from pydantic import HttpUrl

from pyopenbadges.crypto.keys import generate_keypair
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject


class TestCredentialCrypto:
    """Tests pour les méthodes cryptographiques de OpenBadgeCredential"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        # Générer une paire de clés pour les tests
        self.keypair = generate_keypair(algorithm="Ed25519")
        
        # Créer un émetteur (Profile)
        self.issuer = Profile(
            id="https://example.org/issuers/1",
            type="Profile",
            name="Test Organization"
        )
        
        # Créer un badge (Achievement)
        self.badge = Achievement(
            id="https://example.org/badges/1",
            type="Achievement",
            name="Test Badge",
            issuer=self.issuer
        )
        
        # Créer un credential
        self.credential = OpenBadgeCredential(
            id="https://example.org/credentials/1",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer=self.issuer,
            issuanceDate=datetime.now(),
            credentialSubject=AchievementSubject(
                id="did:example:recipient",
                type="AchievementSubject",
                achievement=self.badge
            )
        )

    def test_sign_credential(self):
        """Test de la méthode sign du credential"""
        # Signer le credential
        signed_credential = self.credential.sign(
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )
        
        # Vérifier que le credential est signé
        assert signed_credential.proof is not None
        assert signed_credential.proof.type == "Ed25519Signature2020"
        assert isinstance(signed_credential.proof.created, datetime)
        assert str(signed_credential.proof.verificationMethod) == "https://example.org/issuers/1/keys/1"
        assert signed_credential.proof.proofPurpose == "assertionMethod"
        assert signed_credential.proof.proofValue is not None

    def test_verify_signature(self):
        """Test de la méthode verify_signature du credential"""
        # Signer le credential
        signed_credential = self.credential.sign(
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )
        
        # Vérifier la signature
        result = signed_credential.verify_signature(
            public_key=self.keypair.public_key
        )
        
        # La vérification doit réussir
        assert result is True

    def test_verify_signature_with_wrong_key(self):
        """Test de vérification avec une mauvaise clé"""
        # Signer le credential
        signed_credential = self.credential.sign(
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )
        
        # Générer une autre paire de clés
        wrong_keypair = generate_keypair(algorithm="Ed25519")
        
        # Vérifier la signature avec la mauvaise clé
        result = signed_credential.verify_signature(
            public_key=wrong_keypair.public_key
        )
        
        # La vérification doit échouer
        assert result is False

    def test_verify_signature_with_no_proof(self):
        """Test de vérification d'un credential sans preuve"""
        # Vérifier le credential sans preuve
        with pytest.raises(ValueError, match="Le credential ne possède pas de preuve"):
            self.credential.verify_signature(
                public_key=self.keypair.public_key
            )

    def test_tampered_credential(self):
        """Test de vérification avec un credential modifié"""
        # Signer le credential
        signed_credential = self.credential.sign(
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1"
        )
        
        # Créer une copie modifiée du credential
        tampered_credential = signed_credential.model_copy(deep=True)
        tampered_credential.credentialSubject.id = "did:example:hacker"
        
        # Vérifier la signature du credential modifié
        result = tampered_credential.verify_signature(
            public_key=self.keypair.public_key
        )
        
        # La vérification doit échouer
        assert result is False
