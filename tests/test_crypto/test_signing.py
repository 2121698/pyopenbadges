"""
Tests pour le module de signature des Verifiable Credentials
"""

import pytest
from datetime import datetime
from pydantic import HttpUrl, AnyUrl

from pyopenbadges.crypto.keys import generate_keypair
from pyopenbadges.crypto.signing import sign_credential, create_proof
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject
from pyopenbadges.models.credential import Proof


class TestSigningFunctions:
    """Tests pour les fonctions de signature"""

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

    def test_create_proof(self):
        """Test de création d'une preuve cryptographique"""
        # Créer une preuve
        proof = create_proof(
            credential_json=self.credential.model_dump(mode='json'),
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1",
            proof_type="Ed25519Signature2020"
        )
        
        # Vérifier le type
        assert isinstance(proof, Proof)
        
        # Vérifier les propriétés
        assert proof.type == "Ed25519Signature2020"
        assert isinstance(proof.created, datetime)
        assert str(proof.verificationMethod) == "https://example.org/issuers/1/keys/1"
        assert proof.proofPurpose == "assertionMethod"
        assert proof.proofValue is not None and isinstance(proof.proofValue, str)

    def test_sign_credential(self):
        """Test de signature d'un credential"""
        # Signer le credential
        signed_credential = sign_credential(
            credential=self.credential,
            private_key=self.keypair.private_key,
            verification_method="https://example.org/issuers/1/keys/1",
            proof_type="Ed25519Signature2020"
        )
        
        # Vérifier que le credential est signé
        assert signed_credential.proof is not None
        assert signed_credential.proof.type == "Ed25519Signature2020"
        assert isinstance(signed_credential.proof.created, datetime)
        assert str(signed_credential.proof.verificationMethod) == "https://example.org/issuers/1/keys/1"
        assert signed_credential.proof.proofPurpose == "assertionMethod"
        assert signed_credential.proof.proofValue is not None
        
        # Vérifier que le credential original n'a pas été modifié
        assert self.credential.proof is None

    def test_sign_credential_with_existing_proof(self):
        """Test de signature d'un credential qui a déjà une preuve"""
        # Ajouter une preuve au credential
        self.credential.proof = Proof(
            type="Ed25519Signature2020",
            created=datetime.now(),
            verificationMethod="https://example.org/issuers/1/keys/1",
            proofPurpose="assertionMethod",
            proofValue="invalid_signature"
        )
        
        # Tenter de signer le credential
        with pytest.raises(ValueError, match="Le credential possède déjà une preuve"):
            sign_credential(
                credential=self.credential,
                private_key=self.keypair.private_key,
                verification_method="https://example.org/issuers/1/keys/1",
                proof_type="Ed25519Signature2020"
            )

    def test_sign_credential_with_unsupported_algorithm(self):
        """Test de signature avec un algorithme non supporté"""
        with pytest.raises(ValueError, match="Type de preuve non supporté"):
            sign_credential(
                credential=self.credential,
                private_key=self.keypair.private_key,
                verification_method="https://example.org/issuers/1/keys/1",
                proof_type="UnsupportedSignature2020"
            )
