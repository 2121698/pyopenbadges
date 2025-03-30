# OpenBadge v3.0 Specification

[![🇫🇷 Version française](https://img.shields.io/badge/🇫🇷_Version_française-blue.svg)](SPECIFICATION.fr.md)

This document summarizes the OpenBadge v3.0 specifications according to IMS Global standards. It will serve as a guide for the implementation of our Python library.

## 1. Introduction

OpenBadges v3.0 is a standard format for representing and verifying digital badges. Version 3.0 is based on W3C Verifiable Credentials and brings several improvements compared to v2.0.

## 1.1 Verifiable Credentials

Verifiable Credentials (VCs) are a W3C standard for digital credentials that can be cryptographically verified. They are a core component of OpenBadge v3.0.

### Key Concepts

- **Verifiable Credential**: A tamper-evident credential with authorship that can be cryptographically verified
- **Issuer**: The entity that creates and signs the credential
- **Subject**: The entity about which claims are made (the recipient of a badge)
- **Verifier**: Any entity that needs to verify the credential's authenticity

### Structure of a Verifiable Credential

A Verifiable Credential consists of:

1. **Metadata**: Information about the credential itself (ID, type, issuance date, etc.)
2. **Claims**: Statements about the subject (in OpenBadges, this includes the achievement)
3. **Proof**: Cryptographic proof that makes the credential verifiable

### Verification Process

The verification of a Verifiable Credential involves:

1. Checking the credential's signature using the issuer's public key
2. Verifying that the credential hasn't been revoked or expired
3. Validating that the credential conforms to the expected schema

In PyOpenBadges, the `OpenBadgeCredential` model implements the Verifiable Credential standard, with the `proof` field containing the cryptographic signature.

## 2. General Structure

An OpenBadge v3.0 badge consists of several interconnected elements:

- **Profile** (formerly Issuer): The entity that issues the badge
- **Achievement** (formerly BadgeClass): The badge definition
- **Credential** (formerly Assertion): The attribution of a specific badge to a recipient
- **Endorsement**: A recommendation or validation by a third party

These elements are represented in JSON-LD format (JSON with Linked Data context).

## 3. Main Components

### 3.1 Profile (Issuer)

Represents the entity that issues badges.

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "id": "https://example.org/issuers/1",
  "type": "Profile",
  "name": "Organization name",
  "url": "https://example.org",
  "email": "contact@example.org",
  "description": "Organization description",
  "image": {
    "id": "https://example.org/logo.png",
    "type": "Image"
  }
}
```

#### Required properties:
- `id`: Unique URI that identifies the issuer
- `type`: Must include "Profile"
- `name`: Human-readable name of the issuer

#### Recommended properties:
- `url`: Issuer's website
- `email`: Contact email
- `description`: Description of the issuer
- `image`: Image/logo of the issuer

### 3.2 Achievement (Badge Class)

Defines a specific type of badge that can be awarded.

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "id": "https://example.org/badges/1",
  "type": ["Achievement"],
  "name": "Badge name",
  "description": "Detailed description of the badge",
  "criteria": {
    "narrative": "Criteria for earning this badge"
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

#### Required properties:
- `id`: Unique URI that identifies the achievement
- `type`: Must include "Achievement"
- `name`: Human-readable name of the badge
- `issuer`: Reference to the issuer (Profile)

#### Recommended properties:
- `description`: Description of the badge
- `criteria`: Conditions for earning the badge
- `image`: Image representing the badge

### 3.3 Credential (Assertion)

Represents the award of a specific badge to a recipient.

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

#### Required properties:
- `id`: Unique URI that identifies the credential
- `type`: Must include "VerifiableCredential" and "OpenBadgeCredential"
- `issuer`: Reference to the issuer
- `issuanceDate`: Date of issuance in ISO format
- `credentialSubject`: Information about the recipient and the achievement

#### Recommended properties:
- `proof`: Cryptographic proof of validity
- `expirationDate`: Expiration date (if applicable)

### 3.4 Endorsement

Recommendation or validation of an element (badge, issuer, assertion) by a third party.

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
    "endorsementComment": "This badge meets our organization's criteria."
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

#### Required properties:
- `id`: Unique URI that identifies the endorsement
- `type`: Must include "VerifiableCredential" and "EndorsementCredential"
- `issuer`: Reference to the issuer of the endorsement
- `issuanceDate`: Date of issuance
- `credentialSubject`: Endorsed object and comment

## 4. Alignments and Extensions

### 4.1 Alignment (Alignment with a framework)

Allows associating a badge with external competency frameworks.

```json
{
  "targetName": "Framework name",
  "targetUrl": "https://example.org/frameworks/1",
  "targetDescription": "Framework description",
  "targetFramework": "Competency framework",
  "targetCode": "CODE123"
}
```

### 4.2 Evidence

Evidence elements justifying the award of a badge.

```json
{
  "id": "https://example.org/evidence/1",
  "type": "Evidence",
  "name": "Evidence title",
  "description": "Evidence description",
  "narrative": "Detailed explanation",
  "genre": "Evidence type"
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
