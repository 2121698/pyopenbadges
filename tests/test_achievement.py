"""
Tests pour le modèle Achievement (anciennement BadgeClass) dans OpenBadges v3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from pyopenbadges.models.profile import Profile, Image
from pyopenbadges.models.achievement import Achievement, Criteria, Alignment
from pyopenbadges.utils.validators import validate_achievement


def test_achievement_creation_with_minimal_fields():
    """
    Test la création d'un Achievement avec les champs minimaux requis
    """
    # Création d'un Achievement avec seulement les champs obligatoires
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        issuer="https://example.org/issuers/1"
    )
    
    # Vérification des valeurs
    assert str(achievement.id) == "https://example.org/badges/1"
    assert achievement.type == "Achievement"
    assert achievement.name == "Badge Exemple"
    assert str(achievement.issuer) == "https://example.org/issuers/1"
    assert achievement.description is None
    assert achievement.criteria is None
    assert achievement.image is None
    assert achievement.tags is None
    assert achievement.alignment is None


def test_achievement_creation_with_all_fields():
    """
    Test la création d'un Achievement avec tous les champs
    """
    # Création d'un Profile pour l'émetteur
    issuer = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Organisation Exemple"
    )
    
    # Création d'un Achievement complet
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        description="Un badge d'exemple pour tester la librairie",
        issuer=issuer,
        criteria=Criteria(
            narrative="Pour obtenir ce badge, vous devez compléter les tests unitaires."
        ),
        image=Image(
            id="https://example.org/badges/1/image",
            type="Image",
            caption="Image du badge"
        ),
        tags=["test", "exemple", "badge"],
        alignment=[
            Alignment(
                targetName="Compétence test",
                targetUrl="https://example.org/frameworks/competence1",
                targetDescription="Une compétence de test",
                targetFramework="Cadre de compétences test",
                targetCode="TEST01"
            )
        ],
        created=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        updated=datetime.fromisoformat("2023-01-02T00:00:00+00:00")
    )
    
    # Vérification des valeurs
    assert str(achievement.id) == "https://example.org/badges/1"
    assert achievement.type == "Achievement"
    assert achievement.name == "Badge Exemple"
    assert achievement.description == "Un badge d'exemple pour tester la librairie"
    assert achievement.issuer == issuer
    assert achievement.criteria.narrative == "Pour obtenir ce badge, vous devez compléter les tests unitaires."
    assert str(achievement.image.id) == "https://example.org/badges/1/image"
    assert achievement.image.type == "Image"
    assert achievement.image.caption == "Image du badge"
    assert "test" in achievement.tags
    assert "exemple" in achievement.tags
    assert "badge" in achievement.tags
    assert len(achievement.alignment) == 1
    assert achievement.alignment[0].targetName == "Compétence test"
    assert str(achievement.alignment[0].targetUrl) == "https://example.org/frameworks/competence1"
    assert achievement.alignment[0].targetFramework == "Cadre de compétences test"
    assert achievement.created == datetime.fromisoformat("2023-01-01T00:00:00+00:00")
    assert achievement.updated == datetime.fromisoformat("2023-01-02T00:00:00+00:00")


def test_achievement_with_issuer_reference():
    """
    Test la création d'un Achievement avec une référence d'émetteur
    """
    # Création d'un Achievement avec une référence d'émetteur
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        issuer={
            "id": "https://example.org/issuers/1",
            "type": "Profile"
        }
    )
    
    # Vérification des valeurs
    assert str(achievement.id) == "https://example.org/badges/1"
    assert achievement.type == "Achievement"
    assert achievement.name == "Badge Exemple"
    assert str(achievement.issuer["id"]) == "https://example.org/issuers/1"
    assert achievement.issuer["type"] == "Profile"


def test_achievement_validation_error():
    """
    Test les erreurs de validation lors de la création d'un Achievement
    """
    # Test avec un type invalide
    with pytest.raises(ValidationError):
        Achievement(
            id="https://example.org/badges/1",
            type="InvalidType",
            name="Badge Exemple",
            issuer="https://example.org/issuers/1"
        )
    
    # Test sans émetteur
    with pytest.raises(ValidationError):
        Achievement(
            id="https://example.org/badges/1",
            type="Achievement",
            name="Badge Exemple"
        )
    
    # Test avec une URL invalide
    with pytest.raises(ValidationError):
        Achievement(
            id="invalid-url",
            type="Achievement",
            name="Badge Exemple",
            issuer="https://example.org/issuers/1"
        )


def test_achievement_to_json_ld():
    """
    Test la conversion d'un Achievement en JSON-LD
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
        description="Un badge d'exemple pour tester la librairie",
        issuer=issuer,
        criteria=Criteria(
            narrative="Pour obtenir ce badge, vous devez compléter les tests unitaires."
        ),
        image=Image(
            id="https://example.org/badges/1/image",
            type="Image"
        ),
        tags=["test", "exemple", "badge"]
    )
    
    # Conversion en JSON-LD
    json_ld = achievement.to_json_ld()
    
    # Vérification des champs
    assert json_ld["@context"] == "https://w3id.org/openbadges/v3"
    assert json_ld["id"] == "https://example.org/badges/1"
    assert json_ld["type"] == "Achievement"
    assert json_ld["name"] == "Badge Exemple"
    assert json_ld["description"] == "Un badge d'exemple pour tester la librairie"
    assert json_ld["issuer"]["id"] == "https://example.org/issuers/1"
    assert json_ld["issuer"]["type"] == "Profile"
    assert json_ld["criteria"]["narrative"] == "Pour obtenir ce badge, vous devez compléter les tests unitaires."
    assert json_ld["image"]["id"] == "https://example.org/badges/1/image"
    assert json_ld["image"]["type"] == "Image"
    assert "test" in json_ld["tags"]
    assert "exemple" in json_ld["tags"]
    assert "badge" in json_ld["tags"]


def test_achievement_validator():
    """
    Test la fonction de validation d'Achievement
    """
    # Création d'un Achievement valide
    achievement = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Exemple",
        issuer="https://example.org/issuers/1",
        description="Un badge d'exemple pour tester la librairie"
    )
    
    # Validation de l'Achievement
    result = validate_achievement(achievement)
    
    # Vérification que la validation a réussi
    assert result.is_valid
    assert len(result.errors) == 0
    
    # Test avec un Achievement incomplet (sans nom)
    incomplete_achievement = {
        "id": "https://example.org/badges/1",
        "type": "Achievement",
        "issuer": {
            "id": "https://example.org/issuers/1",
            "type": "Profile"
        }
    }
    
    # Validation de l'Achievement incomplet
    result = validate_achievement(incomplete_achievement)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("nom" in error.lower() for error in result.errors)
    
    # Test avec un type invalide
    invalid_type_achievement = {
        "id": "https://example.org/badges/1",
        "type": "InvalidType",
        "name": "Badge Exemple",
        "issuer": "https://example.org/issuers/1"
    }
    
    # Validation de l'Achievement avec type invalide
    result = validate_achievement(invalid_type_achievement)
    
    # Vérification que la validation a échoué
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("type" in error.lower() for error in result.errors)
