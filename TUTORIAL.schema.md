# Schema Validation in PyOpenBadges

Ce tutoriel explique comment utiliser la validation via `credentialSchema` dans PyOpenBadges pour s'assurer que vos credentials sont conformes à la spécification OpenBadge v3.0.

## Introduction à la validation de schéma

Dans la spécification OpenBadge v3.0, la validation de schéma permet de s'assurer qu'un credential respecte une structure spécifique définie par un schéma JSON. Cela garantit l'interopérabilité et la conformité aux standards.

La propriété `credentialSchema` est un élément important de la spécification Verifiable Credentials qui donne des informations sur la structure et les règles de validation d'un credential.

## Créer un credential avec validation de schéma

Pour utiliser la validation de schéma, vous devez inclure un objet `CredentialSchema` lors de la création de votre credential:

```python
from pyopenbadges.models import OpenBadgeCredential, AchievementSubject, CredentialSchema
from datetime import datetime

# Création d'un credential avec validation de schéma
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
    # Définition du schéma de validation
    credentialSchema=CredentialSchema(
        id="https://w3id.org/openbadges/v3/schema/3.0.0",
        type="JsonSchemaValidator2019"
    )
)
```

## Types de schémas pris en charge

PyOpenBadges prend actuellement en charge le type de schéma suivant:

- `JsonSchemaValidator2019`: Pour la validation via JSON Schema

## Valider un credential selon son schéma

Une fois que vous avez créé un credential avec un schéma, vous pouvez valider explicitement sa conformité:

```python
# Validation directe contre le schéma
try:
    is_valid_schema = credential.validate_schema()
    print(f"Le credential est conforme au schéma: {is_valid_schema}")
except ValueError as e:
    print(f"Erreur de validation: {e}")
```

La méthode `is_valid()` vérifie également automatiquement la conformité au schéma:

```python
# is_valid() inclut la validation du schéma
is_valid = credential.is_valid()
print(f"Le credential est valide: {is_valid}")
```

## Validation JSON-LD

Lorsque vous convertissez un credential en JSON-LD, le schéma est automatiquement inclus dans la sortie:

```python
# Conversion en JSON-LD avec inclusion du schéma
json_ld = credential.to_json_ld()
print(json_ld["credentialSchema"])
```

## Validation personnalisée

Pour les besoins avancés, vous pouvez créer des schémas personnalisés:

```python
import json
import requests
from jsonschema import validate, ValidationError

def validate_with_custom_schema(credential, schema_url):
    """
    Valide un credential selon un schéma externe
    
    Args:
        credential: Le credential à valider
        schema_url: L'URL du schéma JSON
    
    Returns:
        bool: True si le credential est conforme au schéma
    """
    response = requests.get(schema_url)
    if response.status_code == 200:
        schema = response.json()
        try:
            validate(instance=credential.model_dump(exclude_none=True), schema=schema)
            return True
        except ValidationError:
            return False
    raise ValueError(f"Impossible de récupérer le schéma: {schema_url}")
```

## Bonnes pratiques

1. **Utiliser des schémas officiels**: Privilégiez les schémas officiels provenant d'organisations reconnues comme IMS Global ou W3C.

2. **Versionner vos schémas**: Si vous créez des schémas personnalisés, assurez-vous de les versionner.

3. **Validation précoce**: Validez vos credentials au moment de leur création plutôt qu'au moment de leur utilisation.

4. **Gérer les erreurs**: Traitez correctement les erreurs de validation pour fournir des informations utiles aux utilisateurs.

## Exemple complet

Voici un exemple complet incluant la création, validation et conversion d'un credential avec schéma:

```python
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject, CredentialSchema
from datetime import datetime

# Création de l'émetteur
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="My Organization"
)

# Création du badge
badge = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Python Badge"
)

# Création du credential avec schéma
credential = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer=issuer,
    issuanceDate=datetime.now(),
    credentialSubject=AchievementSubject(
        id="did:example:recipient123",
        type="AchievementSubject",
        achievement=badge
    ),
    credentialSchema=CredentialSchema(
        id="https://w3id.org/openbadges/v3/schema/3.0.0", 
        type="JsonSchemaValidator2019"
    )
)

# Validation
try:
    # Validation directe du schéma
    schema_valid = credential.validate_schema()
    print(f"Schéma valide: {schema_valid}")
    
    # Validation complète du credential
    credential_valid = credential.is_valid()
    print(f"Credential valide: {credential_valid}")
    
    # Conversion en JSON-LD
    json_ld = credential.to_json_ld()
    print("Schema dans JSON-LD:", json_ld["credentialSchema"])
    
except Exception as e:
    print(f"Erreur: {e}")
```

## Résolution des problèmes courants

- **Schéma inaccessible**: Vérifiez que l'URL du schéma est accessible et retourne un JSON valide.
- **Format de schéma incorrect**: Assurez-vous que le type de schéma est supporté (actuellement `JsonSchemaValidator2019`).
- **Erreurs de validation**: Utilisez des bibliothèques comme `jsonschema` pour obtenir des informations détaillées sur les erreurs de validation.

## Pour aller plus loin

- [Documentation Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)
- [JSON Schema](https://json-schema.org/)
- [Spécification OpenBadge v3.0](https://www.imsglobal.org/spec/ob/v3p0/)
