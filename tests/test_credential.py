"""
Tests pour le modèle OpenBadgeCredential (anciennement Assertion) dans OpenBadges v3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

from pyopenbadges.models.profile import Profile
from pyopenbadges.models.achievement import Achievement
from pyopenbadges.models.credential import OpenBadgeCredential, AchievementSubject, Evidence, Proof
from pyopenbadges.utils.validators import validate_credential


def test_credential_creation_with_minimal_fields():
    """
    Test la création d'un OpenBadgeCredential avec les champs minimaux requis
    """
    # Création d'un OpenBadgeCredential avec seulement les champs obligatoires
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        )
    )
    
    # Vérification des valeurs
    assert str(credential.id) == "https://example.org/credentials/1"
    assert "VerifiableCredential" in credential.type
    assert "OpenBadgeCredential" in credential.type
    assert str(credential.issuer) == "https://example.org/issuers/1"
    assert isinstance(credential.issuanceDate, datetime)
    assert str(credential.credentialSubject.id) == "did:example:recipient123"
    assert credential.credentialSubject.type == "AchievementSubject"
    assert str(credential.credentialSubject.achievement) == "https://example.org/badges/1"
    assert credential.name is None
    assert credential.description is None
    assert credential.proof is None
    assert credential.expirationDate is None
    assert credential.revoked is None
    assert credential.evidence is None


def test_credential_creation_with_all_fields():
    """
    Test la création d'un OpenBadgeCredential avec tous les champs
    """
    # Création d'un Profile pour l'émetteur
    issuer = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple"
    )
    
    # Création d'un Achievement
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        issuer=issuer
    )
    
    # Date d'émission et d'expiration
    issuance_date = datetime.now()
    expiration_date = issuance_date + timedelta(days=365)
    
    # Création d'un OpenBadgeCredential complet
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        name="Credential Exemple",
        description="Un credential d'exemple pour tester la librairie",
        issuer=issuer,
        issuanceDate=issuance_date,
        expirationDate=expiration_date,
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            name="Jean Dupont",
            achievement=achievement
        ),
        proof=Proof(
            type="Ed25519Signature2020",
            created=issuance_date,
            verificationMethod="https://example.org/issuers/1/keys/1",
            proofPurpose="assertionMethod",
            proofValue="z58DAdFfa9SkqZMVPxAQpic7ndSayn5ADzJWiy6dVmSfGeRTm35kVcqp9p2C4QrhUBSK2R"
        ),
        evidence=[
            Evidence(
                id="https://example.org/evidence/1",
                type="Evidence",
                name="Projet Python",
                description="Projet final de la formation Python",
                narrative="Le candidat a développé une application web en utilisant Django."
            )
        ]
    )
    
    # Vérification des valeurs
    assert str(credential.id) == "https://example.org/credentials/1"
    assert "VerifiableCredential" in credential.type
    assert "OpenBadgeCredential" in credential.type
    assert credential.name == "Credential Exemple"
    assert credential.description == "Un credential d'exemple pour tester la librairie"
    assert credential.issuer == issuer
    assert credential.issuanceDate == issuance_date
    assert credential.expirationDate == expiration_date
    assert str(credential.credentialSubject.id) == "did:example:recipient123"
    assert credential.credentialSubject.type == "AchievementSubject"
    assert credential.credentialSubject.name == "Jean Dupont"
    assert credential.credentialSubject.achievement == achievement
    assert credential.proof.type == "Ed25519Signature2020"
    assert credential.proof.proofPurpose == "assertionMethod"
    assert len(credential.evidence) == 1
    assert str(credential.evidence[0].id) == "https://example.org/evidence/1"
    assert credential.evidence[0].name == "Projet Python"


def test_credential_with_object_references():
    """
    Test la création d'un OpenBadgeCredential avec des références d'objets
    """
    # Création d'un OpenBadgeCredential avec des références d'objets
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer={
            "id": "https://example.org/issuers/1",
            "type": "Profile"
        },
        issuanceDate=datetime.now(),
        credentialSubject={
            "id": "did:example:recipient123",
            "type": "AchievementSubject",
            "achievement": {
                "id": "https://example.org/badges/1",
                "type": "Achievement"
            }
        }
    )
    
    # Vérification des valeurs
    assert str(credential.id) == "https://example.org/credentials/1"
    assert "VerifiableCredential" in credential.type
    assert "OpenBadgeCredential" in credential.type
    assert str(credential.issuer["id"]) == "https://example.org/issuers/1"
    assert credential.issuer["type"] == "Profile"
    assert str(credential.credentialSubject.id) == "did:example:recipient123"
    assert str(credential.credentialSubject.achievement["id"]) == "https://example.org/badges/1"


def test_credential_validation_error():
    """
    Test les erreurs de validation lors de la création d'un OpenBadgeCredential
    """
    # Test avec un type invalide
    with pytest.raises(ValidationError):
        OpenBadgeCredential(
            id="https://example.org/credentials/1",
            type=["InvalidType"],
            issuer="https://example.org/issuers/1",
            issuanceDate=datetime.now(),
            credentialSubject=AchievementSubject(
                id="did:example:recipient123",
                type="AchievementSubject",
                achievement="https://example.org/badges/1"
            )
        )
    
    # Test sans date d'émission
    with pytest.raises(ValidationError):
        OpenBadgeCredential(
            id="https://example.org/credentials/1",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer="https://example.org/issuers/1",
            credentialSubject=AchievementSubject(
                id="did:example:recipient123",
                type="AchievementSubject",
                achievement="https://example.org/badges/1"
            )
        )
    
    # Test sans sujet
    with pytest.raises(ValidationError):
        OpenBadgeCredential(
            id="https://example.org/credentials/1",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer="https://example.org/issuers/1",
            issuanceDate=datetime.now()
        )
    
    # Test avec une URL invalide
    with pytest.raises(ValidationError):
        OpenBadgeCredential(
            id="invalid-url",
            type=["VerifiableCredential", "OpenBadgeCredential"],
            issuer="https://example.org/issuers/1",
            issuanceDate=datetime.now(),
            credentialSubject=AchievementSubject(
                id="did:example:recipient123",
                type="AchievementSubject",
                achievement="https://example.org/badges/1"
            )
        )


def test_credential_to_json_ld():
    """
    Test la conversion d'un OpenBadgeCredential en JSON-LD
    """
    # Création d'un Profile pour l'émetteur
    issuer = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple"
    )
    
    # Création d'un Achievement
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        issuer=issuer
    )
    
    # Création d'un OpenBadgeCredential
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        name="Credential Exemple",
        issuer=issuer,
        issuanceDate=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement=achievement
        )
    )
    
    # Conversion en JSON-LD
    json_ld = credential.to_json_ld()
    
    # Vérification des champs
    assert "@context" in json_ld
    assert "https://www.w3.org/2018/credentials/v1" in json_ld["@context"]
    assert "https://w3id.org/openbadges/v3" in json_ld["@context"]
    assert json_ld["id"] == "https://example.org/credentials/1"
    assert "VerifiableCredential" in json_ld["type"]
    assert "OpenBadgeCredential" in json_ld["type"]
    assert json_ld["name"] == "Credential Exemple"
    assert json_ld["issuer"]["id"] == "https://example.org/issuers/1"
    assert json_ld["issuer"]["type"] == "Profile"
    assert json_ld["issuanceDate"] == "2023-01-01T00:00:00+00:00"
    assert json_ld["credentialSubject"]["id"] == "did:example:recipient123"
    assert json_ld["credentialSubject"]["type"] == "AchievementSubject"
    assert json_ld["credentialSubject"]["achievement"]["id"] == "https://example.org/badges/1"
    assert json_ld["credentialSubject"]["achievement"]["type"] == "Achievement"


def test_credential_is_valid():
    """
    Test la méthode is_valid d'un OpenBadgeCredential
    """
    # Création d'un credential valide
    valid_credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        )
    )
    
    # Vérification que le credential est valide
    assert valid_credential.is_valid()
    
    # Création d'un credential expiré
    expired_credential = OpenBadgeCredential(
        id="https://example.org/credentials/2",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now() - timedelta(days=366),
        expirationDate=datetime.now() - timedelta(days=1),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        )
    )
    
    # Vérification que le credential expiré n'est pas valide
    assert not expired_credential.is_valid()
    
    # Création d'un credential révoqué
    revoked_credential = OpenBadgeCredential(
        id="https://example.org/credentials/3",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        revoked=True,
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        )
    )
    
    # Vérification que le credential révoqué n'est pas valide
    assert not revoked_credential.is_valid()


def test_credential_validator():
    """
    Test la fonction de validation d'OpenBadgeCredential
    """
    # Création d'un OpenBadgeCredential valide
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        )
    )
    
    # Validation du credential
    result = validate_credential(credential)
    
    # Vérification que la validation a réussi
    assert result.is_valid
    assert len(result.errors) == 0
    
    # Test avec un credential incomplet (sans date d'émission)
    incomplete_credential = {
        "id": "https://example.org/credentials/1",
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "issuer": {
            "id": "https://example.org/issuers/1",
            "type": "Profile"
        },
        "credentialSubject": {
            "id": "did:example:recipient123",
            "type": "AchievementSubject",
            "achievement": {
                "id": "https://example.org/badges/1",
                "type": "Achievement"
            }
        }
    }
    
    # Validation du credential incomplet
    result = validate_credential(incomplete_credential)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("date" in error.lower() for error in result.errors)
    
    # Test avec un type invalide
    invalid_type_credential = {
        "id": "https://example.org/credentials/1",
        "type": ["InvalidType"],
        "issuer": "https://example.org/issuers/1",
        "issuanceDate": "2023-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:recipient123",
            "type": "AchievementSubject",
            "achievement": "https://example.org/badges/1"
        }
    }
    
    # Validation du credential avec type invalide
    result = validate_credential(invalid_type_credential)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("type" in error.lower() for error in result.errors)
