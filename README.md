# PyOpenBadges

[![🇫🇷 Version française](https://img.shields.io/badge/🇫🇷_Version_française-blue.svg)](README.fr.md)
[![Tests](https://img.shields.io/github/actions/workflow/status/username/pyopenbadges/tests.yml?branch=main&label=tests)](https://github.com/username/pyopenbadges/actions)
[![Coverage](https://img.shields.io/codecov/c/github/username/pyopenbadges)](https://codecov.io/gh/username/pyopenbadges)

A modern Python library for creating, validating, and managing digital badges compliant with the IMS Global OpenBadge v3.0 specification.

More info about OpenBadges: https://openbadges.info/

## Features

- Complete implementation of the OpenBadge v3.0 specification
- Pydantic models with built-in validation
- Conversion to/from JSON-LD
- Advanced validation utilities
- Compatibility with Verifiable Credentials
- Cryptographic signing and verification of credentials
- Key management utilities (Ed25519, RSA)

## Verifiable Credentials

Verifiable Credentials are like digital identity cards that can be verified:

- They are digital documents that prove something about someone
- They are signed by a trusted entity (the issuer)
- They can be verified to ensure they are authentic and haven't been tampered with

In PyOpenBadges, digital badges are implemented as Verifiable Credentials:
- The badge issuer is the credential issuer
- The badge recipient is the credential subject
- The badge itself is represented as an Achievement
- The credential can be cryptographically verified for authenticity

## Installation

```bash
# With pip
pip install pyopenbadges

# With poetry (recommended)
poetry add pyopenbadges
```

## Quick Usage

```python
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject
from datetime import datetime

# Create an issuer (Profile)
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="My Organization",
    description="Organization that issues badges",
    url="https://example.org"
)

# Create a badge (Achievement)
badge = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Python Badge",
    description="For Python mastery",
    issuer=issuer
)

# Create a badge issuance (Credential)
credential = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer=issuer,
    issuanceDate=datetime.now(),
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        name="John Doe",
        achievement=badge
    )
)

# Convert to JSON-LD
json_ld = credential.to_json_ld()
print(json_ld)
```

## Documentation

For more details on using this library, check out the [tutorial](TUTORIAL.md) and the [complete documentation](DOCUMENTATION.md).

## Cryptographic Features

PyOpenBadges supports cryptographic signing and verification of credentials:

```python
from pyopenbadges.crypto import generate_keypair

# Generate a keypair
keypair = generate_keypair()

# Sign a credential
signed_credential = credential.sign(
    private_key=keypair.private_key,
    verification_method="https://example.org/issuers/1/keys/1"
)

# Verify a credential
is_valid = signed_credential.verify_signature(
    public_key=keypair.public_key
)
```

For a complete guide to the cryptographic features, see the [crypto tutorial](TUTORIAL.crypto.md).

## License

LGPL

