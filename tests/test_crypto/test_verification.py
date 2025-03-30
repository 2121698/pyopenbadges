"""
Tests pour le module de vérification des signatures des Verifiable Credentials
"""

import pytest
from datetime import datetime
from pydantic import HttpUrl

from pyopenbadges.crypto.keys import generate_keypair
from pyopenbadges.crypto.signing import sign_credential
from pyopenbadges.crypto.verification import verify_credential, verify_proof
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject
from pyopenbadges.models.credential import Proof


class TestVerificationFunctions:
    """Tests pour les fonctions de vérification"""

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
        
        # Signer le credential
        self.signed_credential = sign_credential(
            credential=self.credential,
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1",
            proof_type="Ed25519Signature2020"
        )

    def test_verify_proof(self):
        """Test de vérification d'une preuve cryptographique"""
        # Vérifier la preuve
        result = verify_proof(
            credential_json=self.signed_credential.model_dump(mode='json'),
            proof=self.signed_credential.proof,
            public_key=self.keypair.public_key
        )
        
        # La vérification doit réussir
        assert result is True

    def test_verify_proof_with_tampered_credential(self):
        """Test de vérification d'une preuve avec un credential modifié"""
        # Créer une copie modifiée du credential
        tampered_credential = self.signed_credential.model_copy(deep=True)
        tampered_credential.credentialSubject.id = "did:example:hacker"
        
        # Vérifier la preuve
        result = verify_proof(
            credential_json=tampered_credential.model_dump(mode='json'),
            proof=self.signed_credential.proof,
            public_key=self.keypair.public_key
        )
        
        # La vérification doit échouer
        assert result is False

    def test_verify_credential(self):
        """Test de vérification d'un credential complet"""
        # Vérifier le credential
        result = verify_credential(
            credential=self.signed_credential,
            public_key=self.keypair.public_key
        )
        
        # La vérification doit réussir
        assert result is True

    def test_verify_credential_with_no_proof(self):
        """Test de vérification d'un credential sans preuve"""
        # Vérifier le credential sans preuve
        with pytest.raises(ValueError, match="Le credential ne possède pas de preuve"):
            verify_credential(
                credential=self.credential,  # Non signé
                public_key=self.keypair.public_key
            )

    def test_verify_credential_with_wrong_key(self):
        """Test de vérification avec une mauvaise clé"""
        # Générer une autre paire de clés
        wrong_keypair = generate_keypair(algorithm="Ed25519")
        
        # Vérifier le credential avec la mauvaise clé
        result = verify_credential(
            credential=self.signed_credential,
            public_key=wrong_keypair.public_key
        )
        
        # La vérification doit échouer
        assert result is False

    def test_verify_credential_with_tampered_data(self):
        """Test de vérification avec des données modifiées"""
        # Créer une copie modifiée du credential
        tampered_credential = self.signed_credential.model_copy(deep=True)
        tampered_credential.credentialSubject.id = "did:example:hacker"
        
        # Vérifier le credential modifié
        result = verify_credential(
            credential=tampered_credential,
            public_key=self.keypair.public_key
        )
        
        # La vérification doit échouer
        assert result is False
