# PyOpenBadges

[![🇬🇧 English version](https://img.shields.io/badge/🇬🇧_English_version-blue.svg)](README.md)
[![Tests](https://img.shields.io/github/actions/workflow/status/username/pyopenbadges/tests.yml?branch=main&label=tests)](https://github.com/username/pyopenbadges/actions)
[![Coverage](https://img.shields.io/codecov/c/github/username/pyopenbadges)](https://codecov.io/gh/username/pyopenbadges)

Une librairie Python moderne pour la création, la validation et la gestion des badges numériques conformes à la spécification OpenBadge v3.0 de l'IMS Global.

Plus d'info sur les OpenBadges : https://openbadges.info/

## Caractéristiques

- Implémentation complète de la spécification OpenBadge v3.0
- Modèles Pydantic avec validation intégrée
- Conversion vers/depuis JSON-LD
- Utilitaires de validation avancés
- Compatibilité avec les Verifiable Credentials

## Installation

```bash
# Avec pip
pip install pyopenbadges

# Avec poetry (recommandé)
poetry add pyopenbadges
```

## Utilisation rapide

```python
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject
from datetime import datetime

# Créer un émetteur (Profile)
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="Mon Organisation",
    description="Organisation qui délivre des badges",
    url="https://example.org"
)

# Créer un badge (Achievement)
badge = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Badge Python",
    description="Pour la maîtrise de Python",
    issuer=issuer
)

# Créer une attribution de badge (Credential)
credential = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer=issuer,
    issuanceDate=datetime.now(),
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        name="Jean Dupont",
        achievement=badge
    )
)

# Convertir en JSON-LD
json_ld = credential.to_json_ld()
print(json_ld)
```

## Documentation

Pour plus de détails sur l'utilisation de cette librairie, consultez le [tutoriel](TUTORIAL.fr.md) et la [documentation complète](DOCUMENTATION.md).

## Licence

MIT

## Contributeurs

- Votre Nom - Développeur principal
