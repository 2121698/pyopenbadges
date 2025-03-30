# Tutoriel sur les fonctionnalités cryptographiques de PyOpenBadges

Ce tutoriel explique comment utiliser les fonctionnalités cryptographiques de PyOpenBadges pour signer et vérifier des OpenBadgeCredentials.

## Prérequis

Assurez-vous d'avoir installé PyOpenBadges :

```bash
pip install pyopenbadges
```

Ou avec Poetry :

```bash
poetry add pyopenbadges
```

## Génération de clés cryptographiques

La première étape consiste à générer une paire de clés (privée et publique) pour signer et vérifier les credentials :

```python
from pyopenbadges.crypto import generate_keypair

# Générer une paire de clés Ed25519 (par défaut)
keypair = generate_keypair()

# Ou générer une paire de clés RSA
# keypair = generate_keypair(algorithm="RSA", key_size=2048)

# Accéder aux clés
private_key = keypair.private_key
public_key = keypair.public_key
```

## Sauvegarde et chargement des clés

Vous pouvez sauvegarder et charger des clés pour une utilisation ultérieure :

```python
from pyopenbadges.crypto import load_keypair, load_public_key

# Sauvegarder la paire de clés
keypair.save_to_file("issuer_keys.json")

# Charger la paire de clés (privée + publique)
keypair = load_keypair("issuer_keys.json")

# Ou charger uniquement la clé publique
public_key = load_public_key("issuer_keys.json")
```

## Création d'un OpenBadgeCredential

Créons un OpenBadgeCredential simple :

```python
from datetime import datetime
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject

# Créer un émetteur (Profile)
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="Organisation Exemple"
)

# Créer un badge (Achievement)
badge = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Badge Exemple",
    description="Un badge d'exemple pour le tutoriel",
    issuer=issuer
)

# Créer un credential
credential = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer=issuer,
    issuanceDate=datetime.now(),
    credentialSubject=AchievementSubject(
        id="did:example:recipient",
        type="AchievementSubject",
        achievement=badge
    )
)
```

## Signature d'un OpenBadgeCredential

Une fois que vous avez créé un credential, vous pouvez le signer avec votre clé privée :

```python
# Signer le credential
signed_credential = credential.sign(
    private_key=keypair.private_key,
    verification_method="https://example.org/issuers/1/keys/1"
)

# Le credential signé contient maintenant une preuve cryptographique
print(f"Type de preuve: {signed_credential.proof.type}")
print(f"Méthode de vérification: {signed_credential.proof.verificationMethod}")
print(f"Valeur de la preuve: {signed_credential.proof.proofValue[:30]}...")
```

## Vérification d'un OpenBadgeCredential

Pour vérifier l'authenticité d'un credential signé, utilisez la clé publique correspondante :

```python
# Vérifier la signature du credential
is_valid = signed_credential.verify_signature(
    public_key=keypair.public_key
)

if is_valid:
    print("Le credential est authentique !")
else:
    print("Le credential n'est pas authentique ou a été modifié.")
```

## Détection de falsification

Les signatures cryptographiques permettent de détecter si un credential a été modifié après sa signature :

```python
# Créer une copie modifiée du credential
tampered_credential = signed_credential.model_copy(deep=True)
tampered_credential.credentialSubject.id = "did:example:hacker"

# Vérifier la signature du credential modifié
is_valid = tampered_credential.verify_signature(
    public_key=keypair.public_key
)

# Cette vérification échouera car le credential a été modifié
print(f"Credential modifié valide ? {is_valid}")  # Affichera False
```

## Utilisation avancée

### Utilisation directe des modules cryptographiques

Si vous avez besoin de plus de contrôle, vous pouvez utiliser directement les fonctions des modules cryptographiques :

```python
from pyopenbadges.crypto.signing import sign_credential, create_proof
from pyopenbadges.crypto.verification import verify_credential, verify_proof

# Créer une preuve pour un credential
proof = create_proof(
    credential_json=credential.model_dump(mode='json'),
    private_key=keypair.private_key,
    verification_method="https://example.org/issuers/1/keys/1"
)

# Signer un credential
signed_credential = sign_credential(
    credential=credential,
    private_key=keypair.private_key,
    verification_method="https://example.org/issuers/1/keys/1"
)

# Vérifier une preuve
is_valid_proof = verify_proof(
    credential_json=signed_credential.model_dump(mode='json'),
    proof=signed_credential.proof,
    public_key=keypair.public_key
)

# Vérifier un credential
is_valid_credential = verify_credential(
    credential=signed_credential,
    public_key=keypair.public_key
)
```

## Exemple complet

Voici un exemple complet qui montre comment générer des clés, créer un credential, le signer et le vérifier :

```python
from datetime import datetime
from pyopenbadges.crypto import generate_keypair
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject

# 1. Générer une paire de clés
keypair = generate_keypair(algorithm="Ed25519")

# 2. Créer un émetteur
issuer = Profile(
    id="https://example.org/issuers/1",
    type="Profile",
    name="Organisation Exemple"
)

# 3. Créer un badge
badge = Achievement(
    id="https://example.org/badges/1",
    type="Achievement",
    name="Badge Exemple",
    description="Un badge d'exemple pour le tutoriel",
    issuer=issuer
)

# 4. Créer un credential
credential = OpenBadgeCredential(
    id="https://example.org/credentials/1",
    type=["VerifiableCredential", "OpenBadgeCredential"],
    issuer=issuer,
    issuanceDate=datetime.now(),
    credentialSubject=AchievementSubject(
        id="did:example:recipient",
        type="AchievementSubject",
        achievement=badge
    )
)

# 5. Signer le credential
signed_credential = credential.sign(
    private_key=keypair.private_key,
    verification_method="https://example.org/issuers/1/keys/1"
)

# 6. Vérifier la signature
is_valid = signed_credential.verify_signature(
    public_key=keypair.public_key
)

print(f"Le credential est authentique : {is_valid}")

# 7. Convertir en JSON-LD pour l'interopérabilité
json_ld = signed_credential.to_json_ld()
```

Ce tutoriel couvre les bases de l'utilisation des fonctionnalités cryptographiques de PyOpenBadges. Pour plus d'informations, consultez la documentation complète.
