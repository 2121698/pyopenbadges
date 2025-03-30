# Spécification OpenBadge v3.0

[![🇬🇧 English version](https://img.shields.io/badge/🇬🇧_English_version-blue.svg)](SPECIFICATION.md)

Ce document résume les spécifications OpenBadge v3.0 selon les standards IMS Global. Il servira de guide pour l'implémentation de notre librairie Python.

## 1. Introduction

OpenBadges v3.0 est un format standard pour représenter et vérifier des badges numériques. La version 3.0 est basée sur les Verifiable Credentials du W3C et apporte plusieurs améliorations par rapport à la v2.0.

## 2. Structure Générale

Un badge OpenBadge v3.0 est composé de plusieurs éléments interconnectés :

- **Profile** (anciennement Issuer) : L'entité qui émet le badge
- **Achievement** (anciennement BadgeClass) : La définition du badge
- **Credential** (anciennement Assertion) : L'attribution d'un badge spécifique à un destinataire
- **Endorsement** : Une recommandation ou validation par un tiers

Ces éléments sont représentés au format JSON-LD (JSON avec contexte Linked Data).

## 3. Composants Principaux

### 3.1 Profile (Émetteur)

Représente l'entité qui émet les badges.

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "id": "https://example.org/issuers/1",
  "type": "Profile",
  "name": "Nom de l'organisation",
  "url": "https://example.org",
  "email": "contact@example.org",
  "description": "Description de l'organisation",
  "image": {
    "id": "https://example.org/logo.png",
    "type": "Image"
  }
}
```

#### Propriétés obligatoires :
- `id`: URI unique qui identifie l'émetteur
- `type`: Doit inclure "Profile"
- `name`: Nom lisible de l'émetteur

#### Propriétés recommandées :
- `url`: Site web de l'émetteur
- `email`: Email de contact
- `description`: Description de l'émetteur
- `image`: Image/logo de l'émetteur

### 3.2 Achievement (Classe de Badge)

Définit un type spécifique de badge qui peut être attribué.

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "id": "https://example.org/badges/1",
  "type": ["Achievement"],
  "name": "Nom du badge",
  "description": "Description détaillée du badge",
  "criteria": {
    "narrative": "Critères pour obtenir ce badge"
  },
  "image": {
    "id": "https://example.org/badges/1/image",
    "type": "Image"
  },
  "issuer": {
    "id": "https://example.org/issuers/1",
    "type": "Profile"
  }
}
```

#### Propriétés obligatoires :
- `id`: URI unique qui identifie l'achievement
- `type`: Doit inclure "Achievement"
- `name`: Nom lisible du badge
- `issuer`: Référence à l'émetteur (Profile)

#### Propriétés recommandées :
- `description`: Description du badge
- `criteria`: Conditions pour obtenir le badge
- `image`: Image représentant le badge

### 3.3 Credential (Assertion)

Représente l'attribution d'un badge spécifique à un destinataire.

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/openbadges/v3"
  ],
  "id": "https://example.org/assertions/1",
  "type": ["VerifiableCredential", "OpenBadgeCredential"],
  "issuer": {
    "id": "https://example.org/issuers/1",
    "type": "Profile"
  },
  "issuanceDate": "2023-01-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
    "type": "AchievementSubject",
    "achievement": {
      "id": "https://example.org/badges/1",
      "type": "Achievement"
    }
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2023-01-01T00:00:00Z",
    "verificationMethod": "https://example.org/issuers/1/keys/1",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

#### Propriétés obligatoires :
- `id`: URI unique qui identifie le credential
- `type`: Doit inclure "VerifiableCredential" et "OpenBadgeCredential"
- `issuer`: Référence à l'émetteur
- `issuanceDate`: Date d'émission au format ISO
- `credentialSubject`: Information sur le destinataire et l'achievement

#### Propriétés recommandées :
- `proof`: Preuve cryptographique de validité
- `expirationDate`: Date d'expiration (si applicable)

### 3.4 Endorsement

Recommandation ou validation d'un élément (badge, émetteur, assertion) par un tiers.

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/openbadges/v3"
  ],
  "id": "https://example.org/endorsements/1",
  "type": ["VerifiableCredential", "EndorsementCredential"],
  "issuer": {
    "id": "https://example.org/endorsers/1",
    "type": "Profile"
  },
  "issuanceDate": "2023-01-02T00:00:00Z",
  "credentialSubject": {
    "id": "https://example.org/badges/1",
    "type": "Achievement",
    "endorsementComment": "Ce badge répond aux critères de notre organisation."
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2023-01-02T00:00:00Z",
    "verificationMethod": "https://example.org/endorsers/1/keys/1",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

#### Propriétés obligatoires :
- `id`: URI unique qui identifie l'endorsement
- `type`: Doit inclure "VerifiableCredential" et "EndorsementCredential"
- `issuer`: Référence à l'émetteur de l'endorsement
- `issuanceDate`: Date d'émission
- `credentialSubject`: Objet endorsé et commentaire

## 4. Alignments et Extensions

### 4.1 Alignment (Alignement avec un référentiel)

Permet d'associer un badge à des référentiels de compétences externes.

```json
{
  "targetName": "Nom du référentiel",
  "targetUrl": "https://example.org/frameworks/1",
  "targetDescription": "Description du référentiel",
  "targetFramework": "Cadre de compétences",
  "targetCode": "CODE123"
}
```

### 4.2 Evidence (Preuve)

Éléments de preuve justifiant l'obtention d'un badge.

```json
{
  "id": "https://example.org/evidence/1",
  "type": "Evidence",
  "name": "Titre de la preuve",
  "description": "Description de la preuve",
  "narrative": "Explication détaillée",
  "genre": "Type de preuve"
}
```

## 5. Vérification et Sécurité

OpenBadge v3.0 utilise les mécanismes de vérification des Verifiable Credentials, principalement via des signatures cryptographiques.

### 5.1 Méthodes de Vérification

- **Ed25519Signature2020**: Signature EdDSA avec la courbe Ed25519
- **RsaSignature2018**: Signature RSA
- **JsonWebSignature2020**: Signature au format JWS

### 5.2 Révocation

La révocation d'un credential peut être effectuée via plusieurs mécanismes:

- Liste de révocation (status list)
- Vérification du statut via une API

## 6. Différences avec OpenBadge v2.0

- Utilisation du modèle Verifiable Credentials
- Remplacement du terme "Issuer" par "Profile"
- Remplacement du terme "BadgeClass" par "Achievement" 
- Remplacement du terme "Assertion" par "Credential"
- Modèle de sécurité amélioré
- Support de différents types d'identifiants pour les destinataires

## 7. Considérations d'Implémentation

- Support de JSON-LD et des contextes
- Validation des données selon le schéma
- Mécanismes de signature et vérification
- Gestion des identifiants

Pour une documentation complète et officielle, veuillez consulter la [spécification OpenBadge v3.0 de IMS Global](https://www.imsglobal.org/spec/ob/v3p0/).
