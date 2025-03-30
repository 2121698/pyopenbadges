# Tutoriel PyOpenBadges

[![🇫🇷 Version française](https://img.shields.io/badge/🇫🇷_Version_française-blue.svg)](TUTORIAL.fr.md)

Ce tutoriel vous guidera à travers les étapes pour utiliser efficacement la bibliothèque PyOpenBadges pour créer, valider et gérer des badges numériques conformes à la spécification OpenBadge v3.0.

## Table des matières

1. [Installation](#installation)
2. [Création d'un émetteur (Profile)](#création-dun-émetteur-profile)
3. [Création d'un badge (Achievement)](#création-dun-badge-achievement)
4. [Émission d'un badge (OpenBadgeCredential)](#émission-dun-badge-openbadgecredential)
5. [Validation des objets](#validation-des-objets)
6. [Sérialisation et désérialisation](#sérialisation-et-désérialisation)
7. [Création d'un endorsement](#création-dun-endorsement)
8. [Intégration avec Django](#intégration-avec-django)
9. [Bonnes pratiques](#bonnes-pratiques)

## Installation

Pour installer PyOpenBadges, utilisez pip ou poetry :

```bash
# Avec pip
pip install pyopenbadges

# Avec poetry (recommandé)
poetry add pyopenbadges
```

## Création d'un émetteur (Profile)

Dans OpenBadge v3, les émetteurs sont représentés par le modèle `Profile`. Commençons par créer un profil d'émetteur :

```python
from pyopenbadges.models.profile import Profile, Image, Address

# Création d'un profil émetteur minimal
issuer_minimal = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="Mon Organisation"
)

# Création d'un profil émetteur complet
issuer_complete = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="Mon Organisation",
    description="Organisation délivrant des badges de compétences en programmation",
    url="https://example.org",
    email="contact@example.org",
    telephone="+33123456789",
    image=Image(
        id="https://example.org/issuers/1/image",
        type="Image",
        caption="Logo de Mon Organisation"
    ),
    address=Address(
        streetAddress="123 Rue Exemple",
        addressLocality="Lyon",
        addressRegion="Auvergne-Rhône-Alpes",
        postalCode="69000",
        addressCountry="FR"
    )
)

# Conversion en JSON-LD
issuer_json = issuer_complete.to_json_ld()
print(issuer_json)
```

## Création d'un badge (Achievement)

Une fois l'émetteur créé, vous pouvez définir des badges (Achievement) :

```python
from pyopenbadges.models.achievement import Achievement, Criteria, Alignment

# Création d'un badge minimal
badge_minimal = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Badge Python Débutant",
    issuer="https://example.org/issuers/1"  # Référence à l'émetteur par son ID
)

# Création d'un badge complet
badge_complete = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Badge Python Débutant",
    description="Ce badge certifie la maîtrise des bases de Python",
    issuer=issuer_complete,  # Utilisation de l'objet issuer directement
    criteria=Criteria(
        narrative="Pour obtenir ce badge, le candidat doit démontrer sa compréhension des concepts fondamentaux de Python, incluant les variables, les structures de contrôle, les fonctions et les modules de base."
    ),
    image=Image(
        id="https://example.org/badges/1/image",
        type="Image",
        caption="Badge Python Débutant"
    ),
    tags=["python", "programmation", "débutant"],
    alignment=[
        Alignment(
            targetName="Programmer en Python",
            targetUrl="https://example.org/frameworks/python-skills/beginner",
            targetDescription="Capacité à écrire des programmes Python simples",
            targetFramework="Cadre de compétences numériques",
            targetCode="PYTHON-BEG-01"
        )
    ]
)

# Conversion en JSON-LD
badge_json = badge_complete.to_json_ld()
print(badge_json)
```

## Émission d'un badge (OpenBadgeCredential)

Pour attribuer un badge à un destinataire, créez un `OpenBadgeCredential` :

```python
from pyopenbadges.models.credential import OpenBadgeCredential, AchievementSubject, Evidence
from datetime import datetime, timedelta

# Date d'émission du badge
issuance_date = datetime.now()
# Date d'expiration (optionnelle)
expiration_date = issuance_date + timedelta(days=365)

# Création d'un credential minimal
credential_minimal = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer="https://example.org/issuers/1",
    issuanceDate=issuance_date,
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        achievement="https://example.org/badges/1"
    )
)

# Création d'un credential complet
credential_complete = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    name="Certification Python Débutant pour Jean Dupont",
    description="Certification attestant des compétences en Python de niveau débutant",
    issuer=issuer_complete,
    issuanceDate=issuance_date,
    expirationDate=expiration_date,
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        name="Jean Dupont",
        achievement=badge_complete
    ),
    evidence=[
        Evidence(
            id="https://example.org/evidence/1",
            type="Evidence",
            name="Projet Python",
            description="Application console développée en Python",
            narrative="Jean a développé une application CLI qui démontre sa compréhension des boucles, conditionnels et fonctions en Python."
        )
    ]
)

# Vérification de la validité du credential
is_valid = credential_complete.is_valid()
print(f"Le credential est valide : {is_valid}")

# Conversion en JSON-LD
credential_json = credential_complete.to_json_ld()
print(credential_json)
```

## Validation des objets

PyOpenBadges fournit des utilitaires pour valider les objets selon la spécification OpenBadge v3 :

```python
from pyopenbadges.utils.validators import (
    validate_profile,
    validate_achievement,
    validate_credential,
    validate_endorsement
)

# Valider un Profile
profile_validation = validate_profile(issuer_complete)
if profile_validation.is_valid:
    print("Le profil est valide selon la spécification OpenBadge v3")
else:
    print("Erreurs de validation du profil :", profile_validation.errors)

# Valider un Achievement
achievement_validation = validate_achievement(badge_complete)
if achievement_validation.is_valid:
    print("Le badge est valide selon la spécification OpenBadge v3")
else:
    print("Erreurs de validation du badge :", achievement_validation.errors)

# Valider un OpenBadgeCredential
credential_validation = validate_credential(credential_complete)
if credential_validation.is_valid:
    print("Le credential est valide selon la spécification OpenBadge v3")
else:
    print("Erreurs de validation du credential :", credential_validation.errors)

# Vous pouvez également valider des objets à partir de dictionnaires JSON-LD
json_data = {
    "id": "https://example.org/badges/2",
    "type": "Achievement",
    "name": "Badge Python Intermédiaire",
    "issuer": "https://example.org/issuers/1"
}
validation_result = validate_achievement(json_data)
print(f"Validation du JSON : {validation_result.is_valid}")
```

## Sérialisation et désérialisation

PyOpenBadges permet de convertir facilement les objets en JSON-LD et vice versa :

```python
from pyopenbadges.utils.serializers import (
    save_object_to_file,
    load_object_from_file,
    json_ld_to_profile,
    json_ld_to_achievement,
    json_ld_to_credential,
    json_ld_to_endorsement
)

# Sauvegarder un objet dans un fichier
save_object_to_file(credential_complete, "credential.json")

# Charger un objet depuis un fichier
loaded_credential = load_object_from_file("credential.json", "OpenBadgeCredential")

# Conversion JSON-LD vers objets Python
profile_json_ld = {
    "@context": "https://w3id.org/openbadges/v3",
    "id": "https://example.org/issuers/2",
    "type": "Profile",
    "name": "Autre Organisation"
}
profile_obj = json_ld_to_profile(profile_json_ld)

achievement_json_ld = {
    "@context": "https://w3id.org/openbadges/v3",
    "id": "https://example.org/badges/2",
    "type": "Achievement",
    "name": "Badge Python Intermédiaire",
    "issuer": "https://example.org/issuers/1"
}
achievement_obj = json_ld_to_achievement(achievement_json_ld)
```

## Création d'un endorsement

Les endorsements permettent à des tiers de valider et de reconnaître des badges, des émetteurs ou des credentials :

```python
from pyopenbadges.models.endorsement import EndorsementCredential, EndorsementSubject

# Création d'un profil pour l'organisme d'endorsement
endorser = Profile(
    id="https://endorser.org/profiles/1",
    type="Profile",
    name="Organisme d'Accréditation",
    description="Organisme qui accrédite les badges de qualité"
)

# Création d'un endorsement pour un badge
badge_endorsement = EndorsementCredential(
    id="https://endorser.org/endorsements/1",
    type=["VerifiableCredential", "EndorsementCredential"],
    name="Endorsement du Badge Python Débutant",
    description="Ce badge est reconnu par notre organisme comme étant de haute qualité",
    issuer=endorser,
    issuanceDate=datetime.now(),
    credentialSubject=EndorsementSubject(
        id="https://example.org/badges/1",
        type="Achievement",
        endorsementComment="Ce badge suit toutes les bonnes pratiques pédagogiques et correspond bien au niveau débutant en Python."
    )
)

# Création d'un endorsement pour un émetteur
issuer_endorsement = EndorsementCredential(
    id="https://endorser.org/endorsements/2",
    type=["VerifiableCredential", "EndorsementCredential"],
    name="Endorsement de Mon Organisation",
    issuer=endorser,
    issuanceDate=datetime.now(),
    credentialSubject=EndorsementSubject(
        id="https://example.org/issuers/1",
        type="Profile",
        endorsementComment="Cet émetteur est reconnu pour la qualité de ses programmes de certification."
    )
)

# Conversion en JSON-LD
endorsement_json = badge_endorsement.to_json_ld()
print(endorsement_json)
```

## Bonnes pratiques

Voici quelques recommandations pour utiliser efficacement PyOpenBadges :

1. **Utilisez des identifiants persistants** : Assurez-vous que les identifiants (URLs) de vos badges, émetteurs et credentials sont persistants et accessibles.

2. **Validez vos données** : Utilisez toujours les fonctions de validation pour vous assurer que vos objets sont conformes à la spécification.

3. **Gestion des dates** : Utilisez des objets `datetime` Python pour les dates et évitez les manipulations manuelles de chaînes.

4. **Accès public** : Les informations sur les badges doivent être accessibles publiquement. Assurez-vous que les URLs utilisées comme identifiants sont accessibles.

5. **Tests** : Testez vos implémentations avec des cas de test couvrant les scénarios courants et les cas limites.

```python
# Exemple de test
import pytest
from pyopenbadges.models import Achievement
from pyopenbadges.utils.validators import validate_achievement

def test_achievement_validation():
    # Test avec un badge valide
    valid_badge = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Badge Test",
        issuer="https://example.org/issuers/1"
    )
    result = validate_achievement(valid_badge)
    assert result.is_valid
    
    # Test avec un badge invalide (sans nom)
    invalid_badge = {
        "id": "https://example.org/badges/1",
        "type": "Achievement",
        "issuer": "https://example.org/issuers/1"
    }
    result = validate_achievement(invalid_badge)
    assert not result.is_valid
```

En suivant ce tutoriel, vous devriez maintenant être en mesure d'utiliser efficacement la bibliothèque PyOpenBadges pour créer, valider et gérer des badges numériques conformes à la spécification OpenBadge v3.0 de l'IMS Global.
