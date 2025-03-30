"""
Tests pour la validation via credentialSchema dans OpenBadges v3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from pyopenbadges.models.credential import OpenBadgeCredential, AchievementSubject, CredentialSchema


def test_credential_with_schema():
    """
    Test la création d'un OpenBadgeCredential avec un credentialSchema
    """
    # Création d'un OpenBadgeCredential avec un schéma de validation
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        ),
        credentialSchema=CredentialSchema(
            id="https://w3id.org/vc/status-list/2021/v1",
            type="JsonSchemaValidator2019"
        )
    )
    
    # Vérification des valeurs
    assert credential.credentialSchema is not None
    assert str(credential.credentialSchema.id) == "https://w3id.org/vc/status-list/2021/v1"
    assert credential.credentialSchema.type == "JsonSchemaValidator2019"


def test_schema_validation_success():
    """
    Test qu'un credential avec un schéma valide passe la validation
    """
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        ),
        credentialSchema=CredentialSchema(
            id="https://w3id.org/vc/status-list/2021/v1",
            type="JsonSchemaValidator2019"
        )
    )
    
    # Validation du schéma
    assert credential.validate_schema() is True
    # Le credential devrait être valide
    assert credential.is_valid() is True


def test_schema_validation_unsupported_type():
    """
    Test qu'un credential avec un type de schéma non pris en charge échoue à la validation
    """
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        ),
        credentialSchema=CredentialSchema(
            id="https://w3id.org/vc/status-list/2021/v1",
            type="UnsupportedSchemaType"
        )
    )
    
    # La validation doit lever une exception
    with pytest.raises(ValueError):
        credential.validate_schema()
    
    # Le credential ne devrait pas être valide à cause du schéma
    assert credential.is_valid() is False


def test_credential_json_ld_with_schema():
    """
    Test que le schéma est correctement inclus dans la représentation JSON-LD
    """
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/1",
        type=["VerifiableCredential", "OpenBadgeCredential"],
        issuer="https://example.org/issuers/1",
        issuanceDate=datetime.now(),
        credentialSubject=AchievementSubject(
            id="did:example:recipient123",
            type="AchievementSubject",
            achievement="https://example.org/badges/1"
        ),
        credentialSchema=CredentialSchema(
            id="https://w3id.org/vc/status-list/2021/v1",
            type="JsonSchemaValidator2019"
        )
    )
    
    # Conversion en JSON-LD
    json_ld = credential.to_json_ld()
    
    # Vérification que le schéma est présent
    assert "credentialSchema" in json_ld
    assert json_ld["credentialSchema"]["id"] == "https://w3id.org/vc/status-list/2021/v1"
    assert json_ld["credentialSchema"]["type"] == "JsonSchemaValidator2019"
