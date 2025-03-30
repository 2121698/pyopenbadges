"""
Tests pour le modèle Profile (anciennement Issuer) dans OpenBadges v3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from pyopenbadges.models.profile import Profile, Image
from pyopenbadges.utils.validators import validate_profile


def test_profile_creation_with_minimal_fields():
    """
    Test la création d'un Profile avec les champs minimaux requis
    """
    # Création d'un Profile avec seulement les champs obligatoires
    profile = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple"
    )
    
    # Vérification des valeurs
    assert str(profile.id) == "https://example.org/issuers/1"
    assert profile.type == "Profile"
    assert profile.name == "Organisation Exemple"
    assert profile.description is None
    assert profile.url is None
    assert profile.email is None
    assert profile.image is None


def test_profile_creation_with_all_fields():
    """
    Test la création d'un Profile avec tous les champs
    """
    # Création d'un Profile complet
    profile = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple",
        description="Une organisation qui délivre des badges",
        url="https://example.org",
        email="contact@example.org",
        telephone="+33123456789",
        image=Image(
            id="https://example.org/logo.png",
            type="Image",
            caption="Logo de l'organisation"
        ),
        created=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        updated=datetime.fromisoformat("2023-01-02T00:00:00+00:00")
    )
    
    # Vérification des valeurs
    assert str(profile.id) == "https://example.org/issuers/1"
    assert profile.type == "Profile"
    assert profile.name == "Organisation Exemple"
    assert profile.description == "Une organisation qui délivre des badges"
    # Normalisation de l'URL en retirant le slash final s'il existe
    assert str(profile.url).rstrip('/') == "https://example.org"
    assert profile.email == "contact@example.org"
    assert profile.telephone == "+33123456789"
    assert str(profile.image.id) == "https://example.org/logo.png"
    assert profile.image.type == "Image"
    assert profile.image.caption == "Logo de l'organisation"
    assert profile.created == datetime.fromisoformat("2023-01-01T00:00:00+00:00")
    assert profile.updated == datetime.fromisoformat("2023-01-02T00:00:00+00:00")


def test_profile_validation_error():
    """
    Test les erreurs de validation lors de la création d'un Profile
    """
    # Test avec un type invalide
    with pytest.raises(ValidationError):
        Profile(
            id="https://example.org/issuers/1",
            type="InvalidType",
            name="Organisation Exemple"
        )
    
    # Test avec un email invalide
    with pytest.raises(ValidationError):
        Profile(
            id="https://example.org/issuers/1",
            type="Profile",
            name="Organisation Exemple",
            email="invalid-email"
        )
    
    # Test avec une URL invalide
    with pytest.raises(ValidationError):
        Profile(
            id="invalid-url",
            type="Profile",
            name="Organisation Exemple"
        )


def test_profile_to_json_ld():
    """
    Test la conversion d'un Profile en JSON-LD
    """
    # Création d'un Profile
    profile = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple",
        description="Une organisation qui délivre des badges",
        url="https://example.org",
        email="contact@example.org",
        image=Image(
            id="https://example.org/logo.png",
            type="Image"
        )
    )
    
    # Conversion en JSON-LD
    json_ld = profile.to_json_ld()
    
    # Vérification des champs
    assert json_ld["@context"] == "https://w3id.org/openbadges/v3"
    assert json_ld["id"] == "https://example.org/issuers/1"
    assert json_ld["type"] == "Profile"
    assert json_ld["name"] == "Organisation Exemple"
    assert json_ld["description"] == "Une organisation qui délivre des badges"
    # Normalisation de l'URL en retirant le slash final s'il existe
    assert json_ld["url"].rstrip('/') == "https://example.org"
    assert json_ld["email"] == "contact@example.org"
    assert json_ld["image"]["id"] == "https://example.org/logo.png"
    assert json_ld["image"]["type"] == "Image"


def test_profile_validator():
    """
    Test la fonction de validation de Profile
    """
    # Création d'un Profile valide
    profile = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple",
        url="https://example.org",
        email="contact@example.org"
    )
    
    # Validation du Profile
    result = validate_profile(profile)
    
    # Vérification que la validation a réussi
    assert result.is_valid
    assert len(result.errors) == 0
    
    # Test avec un Profile incomplet (sans nom)
    incomplete_profile = {
        "id": "https://example.org/issuers/1",
        "type": "Profile"
    }
    
    # Validation du Profile incomplet
    result = validate_profile(incomplete_profile)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("nom" in error.lower() for error in result.errors)
    
    # Test avec un type invalide
    invalid_type_profile = {
        "id": "https://example.org/issuers/1",
        "type": "InvalidType",
        "name": "Organisation Exemple"
    }
    
    # Validation du Profile avec type invalide
    result = validate_profile(invalid_type_profile)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("type" in error.lower() for error in result.errors)
