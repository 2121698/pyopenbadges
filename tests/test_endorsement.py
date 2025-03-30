"""
Tests pour le modèle EndorsementCredential dans OpenBadges v3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

from pyopenbadges.models.profile import Profile
from pyopenbadges.models.endorsement import EndorsementCredential, EndorsementSubject
from pyopenbadges.utils.validators import validate_endorsement


def test_endorsement_creation_with_minimal_fields():
    """
    Test la création d'un EndorsementCredential avec les champs minimaux requis
    """
    # Création d'un EndorsementCredential avec seulement les champs obligatoires
    endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement"
        )
    )
    
    # Vérification des valeurs
    assert str(endorsement.id) == "https://example.org/endorsements/1"
    assert "VerifiableCredential" in endorsement.type
    assert "EndorsementCredential" in endorsement.type
    assert str(endorsement.issuer) == "https://example.org/endorsers/1"
    assert isinstance(endorsement.issuanceDate, datetime)
    assert str(endorsement.credentialSubject.id) == "https://example.org/badges/1"
    assert endorsement.credentialSubject.type == "Achievement"
    assert endorsement.credentialSubject.endorsementComment is None
    assert endorsement.name is None
    assert endorsement.description is None
    assert endorsement.proof is None
    assert endorsement.expirationDate is None


def test_endorsement_creation_with_all_fields():
    """
    Test la création d'un EndorsementCredential avec tous les champs
    """
    # Création d'un Profile pour l'émetteur
    issuer = Profile(
        id="https://example.org/endorsers/1",
        type="Profile",
        name="Organisation Endorser"
    )
    
    # Date d'émission et d'expiration
    issuance_date = datetime.now()
    expiration_date = issuance_date + timedelta(days=365)
    
    # Création d'un EndorsementCredential complet
    endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        name="Endorsement Exemple",
        description="Un endorsement d'exemple pour tester la librairie",
        issuer=issuer,
        issuanceDate=issuance_date,
        expirationDate=expiration_date,
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement",
            endorsementComment="Ce badge respecte les standards de qualité de notre organisation."
        ),
        proof={
            "type": "Ed25519Signature2020",
            "created": issuance_date.isoformat(),
            "verificationMethod": "https://example.org/endorsers/1/keys/1",
            "proofPurpose": "assertionMethod",
            "proofValue": "z58DAdFfa9SkqZMVPxAQpic7ndSayn5ADzJWiy6dVmSfGeRTm35kVcqp9p2C4QrhUBSK2R"
        }
    )
    
    # Vérification des valeurs
    assert str(endorsement.id) == "https://example.org/endorsements/1"
    assert "VerifiableCredential" in endorsement.type
    assert "EndorsementCredential" in endorsement.type
    assert endorsement.name == "Endorsement Exemple"
    assert endorsement.description == "Un endorsement d'exemple pour tester la librairie"
    assert endorsement.issuer == issuer
    assert endorsement.issuanceDate == issuance_date
    assert endorsement.expirationDate == expiration_date
    assert str(endorsement.credentialSubject.id) == "https://example.org/badges/1"
    assert endorsement.credentialSubject.type == "Achievement"
    assert endorsement.credentialSubject.endorsementComment == "Ce badge respecte les standards de qualité de notre organisation."
    assert endorsement.proof["type"] == "Ed25519Signature2020"
    assert endorsement.proof["proofPurpose"] == "assertionMethod"


def test_endorsement_for_different_target_types():
    """
    Test la création d'un EndorsementCredential pour différents types de cibles
    """
    # Endorsement pour un badge (Achievement)
    badge_endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement",
            endorsementComment="Endorsement pour un badge"
        )
    )
    
    assert str(badge_endorsement.id) == "https://example.org/endorsements/1"
    assert str(badge_endorsement.issuer) == "https://example.org/endorsers/1"
    assert str(badge_endorsement.credentialSubject.id) == "https://example.org/badges/1"
    assert badge_endorsement.credentialSubject.type == "Achievement"
    
    # Endorsement pour un émetteur (Profile)
    profile_endorsement = EndorsementCredential(
        id="https://example.org/endorsements/2",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/issuers/1",
            type="Profile",
            endorsementComment="Endorsement pour un émetteur"
        )
    )
    
    assert str(profile_endorsement.id) == "https://example.org/endorsements/2"
    assert str(profile_endorsement.issuer) == "https://example.org/endorsers/1"
    assert str(profile_endorsement.credentialSubject.id) == "https://example.org/issuers/1"
    assert profile_endorsement.credentialSubject.type == "Profile"
    
    # Endorsement pour une credential
    credential_endorsement = EndorsementCredential(
        id="https://example.org/endorsements/3",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/credentials/1",
            type="OpenBadgeCredential",
            endorsementComment="Endorsement pour un credential"
        )
    )
    
    assert str(credential_endorsement.id) == "https://example.org/endorsements/3"
    assert str(credential_endorsement.issuer) == "https://example.org/endorsers/1"
    assert str(credential_endorsement.credentialSubject.id) == "https://example.org/credentials/1"
    assert credential_endorsement.credentialSubject.type == "OpenBadgeCredential"


def test_endorsement_validation_error():
    """
    Test les erreurs de validation lors de la création d'un EndorsementCredential
    """
    # Test avec un type invalide
    with pytest.raises(ValidationError):
        EndorsementCredential(
            id="https://example.org/endorsements/1",
            type=["InvalidType"],
            issuer="https://example.org/endorsers/1",
            issuanceDate=datetime.now(),
            credentialSubject=EndorsementSubject(
                id="https://example.org/badges/1",
                type="Achievement"
            )
        )
    
    # Test sans date d'émission
    with pytest.raises(ValidationError):
        EndorsementCredential(
            id="https://example.org/endorsements/1",
            type=["VerifiableCredential", "EndorsementCredential"],
            issuer="https://example.org/endorsers/1",
            credentialSubject=EndorsementSubject(
                id="https://example.org/badges/1",
                type="Achievement"
            )
        )
    
    # Test sans sujet
    with pytest.raises(ValidationError):
        EndorsementCredential(
            id="https://example.org/endorsements/1",
            type=["VerifiableCredential", "EndorsementCredential"],
            issuer="https://example.org/endorsers/1",
            issuanceDate=datetime.now()
        )
    
    # Test avec une URL invalide
    with pytest.raises(ValidationError):
        EndorsementCredential(
            id="invalid-url",
            type=["VerifiableCredential", "EndorsementCredential"],
            issuer="https://example.org/endorsers/1",
            issuanceDate=datetime.now(),
            credentialSubject=EndorsementSubject(
                id="https://example.org/badges/1",
                type="Achievement"
            )
        )


def test_endorsement_to_json_ld():
    """
    Test la conversion d'un EndorsementCredential en JSON-LD
    """
    # Création d'un Profile pour l'émetteur
    issuer = Profile(
        id="https://example.org/endorsers/1",
        type="Profile",
        name="Organisation Endorser"
    )
    
    # Création d'un EndorsementCredential
    endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        name="Endorsement Exemple",
        issuer=issuer,
        issuanceDate=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement",
            endorsementComment="Ce badge est validé par notre organisation."
        )
    )
    
    # Conversion en JSON-LD
    json_ld = endorsement.to_json_ld()
    
    # Vérification des champs
    assert "@context" in json_ld
    assert "https://www.w3.org/2018/credentials/v1" in json_ld["@context"]
    assert "https://w3id.org/openbadges/v3" in json_ld["@context"]
    assert json_ld["id"] == "https://example.org/endorsements/1"
    assert "VerifiableCredential" in json_ld["type"]
    assert "EndorsementCredential" in json_ld["type"]
    assert json_ld["name"] == "Endorsement Exemple"
    assert json_ld["issuer"]["id"] == "https://example.org/endorsers/1"
    assert json_ld["issuer"]["type"] == "Profile"
    assert json_ld["issuanceDate"] == "2023-01-01T00:00:00+00:00"
    assert json_ld["credentialSubject"]["id"] == "https://example.org/badges/1"
    assert json_ld["credentialSubject"]["type"] == "Achievement"
    assert json_ld["credentialSubject"]["endorsementComment"] == "Ce badge est validé par notre organisation."


def test_endorsement_is_valid():
    """
    Test la méthode is_valid d'un EndorsementCredential
    """
    # Création d'un endorsement valide
    valid_endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement"
        )
    )
    
    # Vérification que l'endorsement est valide
    assert valid_endorsement.is_valid()
    
    # Création d'un endorsement expiré
    expired_endorsement = EndorsementCredential(
        id="https://example.org/endorsements/2",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now() - timedelta(days=366),
        expirationDate=datetime.now() - timedelta(days=1),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement"
        )
    )
    
    # Vérification que l'endorsement expiré n'est pas valide
    assert not expired_endorsement.is_valid()


def test_endorsement_validator():
    """
    Test la fonction de validation d'EndorsementCredential
    """
    # Création d'un EndorsementCredential valide
    endorsement = EndorsementCredential(
        id="https://example.org/endorsements/1",
        type=["VerifiableCredential", "EndorsementCredential"],
        issuer="https://example.org/endorsers/1",
        issuanceDate=datetime.now(),
        credentialSubject=EndorsementSubject(
            id="https://example.org/badges/1",
            type="Achievement"
        )
    )
    
    # Validation de l'endorsement
    result = validate_endorsement(endorsement)
    
    # Vérification que la validation a réussi
    assert result.is_valid
    assert len(result.errors) == 0
    
    # Test avec un endorsement incomplet (sans date d'émission)
    incomplete_endorsement = {
        "id": "https://example.org/endorsements/1",
        "type": ["VerifiableCredential", "EndorsementCredential"],
        "issuer": {
            "id": "https://example.org/endorsers/1",
            "type": "Profile"
        },
        "credentialSubject": {
            "id": "https://example.org/badges/1",
            "type": "Achievement"
        }
    }
    
    # Validation de l'endorsement incomplet
    result = validate_endorsement(incomplete_endorsement)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("date" in error.lower() for error in result.errors)
    
    # Test avec un type invalide
    invalid_type_endorsement = {
        "id": "https://example.org/endorsements/1",
        "type": ["InvalidType"],
        "issuer": "https://example.org/endorsers/1",
        "issuanceDate": "2023-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "https://example.org/badges/1",
            "type": "Achievement"
        }
    }
    
    # Validation de l'endorsement avec type invalide
    result = validate_endorsement(invalid_type_endorsement)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("type" in error.lower() for error in result.errors)
