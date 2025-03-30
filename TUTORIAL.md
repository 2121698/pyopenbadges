# PyOpenBadges Tutorial

[![🇫🇷 French version](https://img.shields.io/badge/🇫🇷_French_version-blue.svg)](TUTORIAL.fr.md)

This tutorial will guide you through the steps to effectively use the PyOpenBadges library to create, validate, and manage digital badges compliant with the OpenBadge v3.0 specification.

## Table of Contents

1. [Installation](#installation)
2. [Creating an Issuer (Profile)](#creating-an-issuer-profile)
3. [Creating a Badge (Achievement)](#creating-a-badge-achievement)
4. [Issuing a Badge (OpenBadgeCredential)](#issuing-a-badge-openbadgecredential)
5. [Validating Objects](#validating-objects)
6. [Serialization and Deserialization](#serialization-and-deserialization)
7. [Creating an Endorsement](#creating-an-endorsement)
8. [Integration with Django](#integration-with-django)
9. [Best Practices](#best-practices)

## Installation

To install PyOpenBadges, use pip or poetry:

```bash
# With pip
pip install pyopenbadges

# With poetry (recommended)
poetry add pyopenbadges
```

## Creating an Issuer (Profile)

In OpenBadge v3, issuers are represented by the `Profile` model. Let's start by creating an issuer profile:

```python
from pyopenbadges.models import Profile
from pyopenbadges.models.profile import Image

# Creating a minimal issuer profile
issuer_minimal = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="My Organization"
)

# Creating a complete issuer profile
issuer_complete = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="My Organization",
    description="Organization issuing programming skills badges",
    url="https://example.org",
    email="contact@example.org",
    telephone="+33123456789",
    image=Image(
        id="https://example.org/issuers/1/image",
        type="Image",
        caption="My Organization Logo"
    )
)

# Conversion to JSON-LD
issuer_json = issuer_complete.to_json_ld()
print(issuer_json)
```

## Creating a Badge (Achievement)

Once the issuer is created, you can define badges (Achievement):

```python
from pyopenbadges.models import Achievement, Profile
from pyopenbadges.models.achievement import Criteria, Alignment

# Create an issuer first (required)
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="My Organization"
)

# Creating a minimal badge
badge_minimal = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Python Beginner Badge",
    issuer=issuer  # Using the issuer object
)

# Creating a complete badge
badge_complete = Achievement(
    id="https://example.org/badges/2",
    type="Achievement",
    name="Python Beginner Badge",
    description="This badge certifies mastery of Python basics",
    issuer=issuer,  # Using the issuer object created above
    criteria=Criteria(
        narrative="To earn this badge, the candidate must demonstrate understanding of fundamental Python concepts, including variables, control structures, functions, and basic modules."
    ),
    image=Image(
        id="https://example.org/badges/1/image",
        type="Image",
        caption="Python Beginner Badge"
    ),
    tags=["python", "programming", "beginner"],
    alignment=[
        Alignment(
            targetName="Programming in Python",
            targetUrl="https://example.org/frameworks/python-skills/beginner",
            targetDescription="Ability to write simple Python programs",
            targetFramework="Digital Skills Framework",
            targetCode="PYTHON-BEG-01"
        )
    ]
)

# Conversion to JSON-LD
badge_json = badge_complete.to_json_ld()
print(badge_json)
```

## Issuing a Badge (OpenBadgeCredential)

To award a badge to a recipient, create an `OpenBadgeCredential`:

```python
from pyopenbadges.models import OpenBadgeCredential, AchievementSubject, Evidence
from datetime import datetime, timedelta

# Badge issuance date
issuance_date = datetime.now()
# Expiration date (optional)
expiration_date = issuance_date + timedelta(days=365)

# Creating a minimal credential
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

# Creating a complete credential
credential_complete = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    name="Python Beginner Certification for John Doe",
    description="Certification attesting to beginner-level Python skills",
    issuer=issuer_complete,
    issuanceDate=issuance_date,
    expirationDate=expiration_date,
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        name="John Doe",
        achievement=badge_complete
    ),
    evidence=[
        Evidence(
            id="https://example.org/evidence/1",
            type="Evidence",
            name="Python Project",
            description="Console application developed in Python",
            narrative="John developed a CLI application that demonstrates his understanding of loops, conditionals, and functions in Python."
        )
    ]
)

# Verifying the validity of the credential
is_valid = credential_complete.is_valid()
print(f"The credential is valid: {is_valid}")

# Conversion to JSON-LD
credential_json = credential_complete.to_json_ld()
print(credential_json)
```

## Validating Objects

PyOpenBadges provides utilities to validate objects according to the OpenBadge v3 specification:

```python
from pyopenbadges.utils.validators import (
    validate_profile,
    validate_achievement,
    validate_credential,
    validate_endorsement
)

# Validating a Profile
profile_validation = validate_profile(issuer_complete)
if profile_validation.is_valid:
    print("The profile is valid according to the OpenBadge v3 specification")
else:
    print("Profile validation errors:", profile_validation.errors)

# Validating an Achievement
achievement_validation = validate_achievement(badge_complete)
if achievement_validation.is_valid:
    print("The badge is valid according to the OpenBadge v3 specification")
else:
    print("Badge validation errors:", achievement_validation.errors)

# Validating an OpenBadgeCredential
credential_validation = validate_credential(credential_complete)
if credential_validation.is_valid:
    print("The credential is valid according to the OpenBadge v3 specification")
else:
    print("Credential validation errors:", credential_validation.errors)

# You can also validate objects from JSON-LD dictionaries
json_data = {
    "id": "https://example.org/badges/2",
    "type": "Achievement",
    "name": "Python Intermediate Badge",
    "issuer": "https://example.org/issuers/1"
}
validation_result = validate_achievement(json_data)
print(f"JSON validation: {validation_result.is_valid}")
```

## Serialization and Deserialization

PyOpenBadges allows you to easily convert objects to JSON-LD and vice versa:

```python
from pyopenbadges.utils.serializers import (
    save_object_to_file,
    load_object_from_file,
    json_ld_to_profile,
    json_ld_to_achievement,
    json_ld_to_credential,
    json_ld_to_endorsement
)

# Save an object to a file
save_object_to_file(credential_complete, "credential.json")

# Load an object from a file
loaded_credential = load_object_from_file("credential.json", "OpenBadgeCredential")

# Converting JSON-LD to Python objects
profile_json_ld = {
    "@context": "https://w3id.org/openbadges/v3",
    "id": "https://example.org/issuers/2",
    "type": "Profile",
    "name": "Another Organization"
}
profile_obj = json_ld_to_profile(profile_json_ld)

achievement_json_ld = {
    "@context": "https://w3id.org/openbadges/v3",
    "id": "https://example.org/badges/2",
    "type": "Achievement",
    "name": "Python Intermediate Badge",
    "issuer": "https://example.org/issuers/1"
}
achievement_obj = json_ld_to_achievement(achievement_json_ld)
```

## Creating an Endorsement

Endorsements allow third parties to validate and recognize badges, issuers, or credentials:

```python
from pyopenbadges.models import EndorsementCredential
from pyopenbadges.models.endorsement import EndorsementSubject

# Creating a profile for the endorsing organization
endorser = Profile(
    id="https://endorser.org/profiles/1",
    type="Profile",
    name="Accreditation Organization",
    description="Organization that accredits quality badges"
)

# Creating an endorsement for a badge
badge_endorsement = EndorsementCredential(
    id="https://endorser.org/endorsements/1",
    type=["VerifiableCredential", "EndorsementCredential"],
    name="Python Beginner Badge Endorsement",
    description="This badge is recognized by our organization as being of high quality",
    issuer=endorser,
    issuanceDate=datetime.now(),
    credentialSubject=EndorsementSubject(
        id="https://example.org/badges/1",
        type="Achievement",
        endorsementComment="This badge follows all good pedagogical practices and corresponds well to the beginner level in Python."
    )
)

# Creating an endorsement for an issuer
issuer_endorsement = EndorsementCredential(
    id="https://endorser.org/endorsements/2",
    type=["VerifiableCredential", "EndorsementCredential"],
    name="My Organization Endorsement",
    issuer=endorser,
    issuanceDate=datetime.now(),
    credentialSubject=EndorsementSubject(
        id="https://example.org/issuers/1",
        type="Profile",
        endorsementComment="This issuer is recognized for the quality of its certification programs."
    )
)

# Conversion to JSON-LD
endorsement_json = badge_endorsement.to_json_ld()
print(endorsement_json)
```

## Best Practices

Here are some recommendations for effectively using PyOpenBadges:

1. **Use persistent identifiers**: Ensure that the identifiers (URLs) of your badges, issuers, and credentials are persistent and accessible.

2. **Validate your data**: Always use the validation functions to ensure that your objects comply with the specification.

3. **Date management**: Use Python `datetime` objects for dates and avoid manual string manipulations.

4. **Public access**: Information about badges should be publicly accessible. Make sure that URLs used as identifiers are accessible.

5. **Testing**: Test your implementations with test cases covering common scenarios and edge cases.

```python
# Test example
import pytest
from pyopenbadges.models import Achievement
from pyopenbadges.utils.validators import validate_achievement

def test_achievement_validation():
    # Test with a valid badge
    valid_badge = Achievement(
        id="https://example.org/badges/1",
        type="Achievement",
        name="Test Badge",
        issuer="https://example.org/issuers/1"
    )
    result = validate_achievement(valid_badge)
    assert result.is_valid
    
    # Test with an invalid badge (without name)
    invalid_badge = {
        "id": "https://example.org/badges/1",
        "type": "Achievement",
        "issuer": "https://example.org/issuers/1"
    }
    result = validate_achievement(invalid_badge)
    assert not result.is_valid
```

By following this tutorial, you should now be able to effectively use the PyOpenBadges library to create, validate, and manage digital badges compliant with the IMS Global OpenBadge v3.0 specification.
