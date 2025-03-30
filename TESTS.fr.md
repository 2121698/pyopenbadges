# Tests PyOpenBadges - Explication Simple

[![🇬🇧 English version](https://img.shields.io/badge/🇬🇧_English_version-blue.svg)](TESTS.md)

Ce document explique les tests de la bibliothèque PyOpenBadges. Ces tests vérifient que tout fonctionne bien.

## Qu'est-ce qu'un test ?

Un test est comme une vérification. Il s'assure qu'une partie du code fait ce qu'elle doit faire.

## Tests pour les profils (Profile)

Les profils sont utilisés pour représenter les personnes ou organisations qui créent des badges.

### Test 1 : Création d'un profil avec informations minimales
Ce test vérifie qu'on peut créer un profil avec juste :
- un identifiant (URL)
- un type
- un nom

### Test 2 : Création d'un profil complet
Ce test vérifie qu'on peut créer un profil avec toutes les informations :
- identifiant, type, nom
- description
- image
- adresse
- email, téléphone
- site web

### Test 3 : Erreurs lors de la création d'un profil
Ce test vérifie que des erreurs apparaissent quand :
- on ne met pas les informations obligatoires
- on met des informations incorrectes (comme une adresse email mal écrite)

### Test 4 : Conversion d'un profil en format JSON-LD
Ce test vérifie qu'un profil peut être transformé en format JSON-LD (un format standard pour internet).

### Test 5 : Validation d'un profil
Ce test vérifie que la fonction de validation :
- accepte les profils valides
- refuse les profils invalides
- détecte les erreurs dans les profils incorrects

## Tests pour les badges (Achievement)

Les badges sont les récompenses qu'on peut obtenir.

### Test 1 : Création d'un badge avec informations minimales
Ce test vérifie qu'on peut créer un badge avec juste :
- un identifiant
- un type
- un nom
- un émetteur (la personne qui donne le badge)

### Test 2 : Création d'un badge complet
Ce test vérifie qu'on peut créer un badge avec toutes les informations possibles :
- identifiant, type, nom
- description
- image
- critères pour obtenir le badge
- tags
- alignement avec des standards

### Test 3 : Badge avec référence à un émetteur
Ce test vérifie qu'on peut créer un badge en faisant référence à un émetteur :
- par son URL
- ou en utilisant l'objet émetteur directement

### Test 4 : Erreurs lors de la création d'un badge
Ce test vérifie que des erreurs apparaissent quand on ne respecte pas les règles de création d'un badge.

### Test 5 : Conversion d'un badge en format JSON-LD
Ce test vérifie qu'un badge peut être transformé en format JSON-LD.

### Test 6 : Validation d'un badge
Ce test vérifie que la fonction de validation détecte correctement les badges valides et invalides.

## Tests pour les attestations (OpenBadgeCredential)

Les attestations sont les documents qui prouvent qu'une personne a reçu un badge.

### Test 1 : Création d'une attestation avec informations minimales
Ce test vérifie qu'on peut créer une attestation avec juste les informations essentielles.

### Test 2 : Création d'une attestation complète
Ce test vérifie qu'on peut créer une attestation avec toutes les informations possibles :
- identifiant, type
- émetteur
- date d'émission
- date d'expiration
- destinataire
- badge
- preuves

### Test 3 : Attestation avec références à d'autres objets
Ce test vérifie qu'on peut faire référence à un émetteur, un badge et un destinataire.

### Test 4 : Erreurs lors de la création d'une attestation
Ce test vérifie que des erreurs apparaissent quand les informations ne sont pas correctes.

### Test 5 : Conversion d'une attestation en format JSON-LD
Ce test vérifie qu'une attestation peut être transformée en format JSON-LD.

### Test 6 : Méthode pour vérifier si une attestation est valide
Ce test vérifie que la méthode `is_valid()` fonctionne correctement.

### Test 7 : Validation d'une attestation
Ce test vérifie que la fonction de validation détecte correctement les attestations valides et invalides.

## Tests pour les recommandations (EndorsementCredential)

Les recommandations sont des documents qui montrent qu'une personne ou organisation approuve un badge.

### Test 1 : Création d'une recommandation avec informations minimales
Ce test vérifie qu'on peut créer une recommandation avec juste les informations essentielles.

### Test 2 : Création d'une recommandation complète
Ce test vérifie qu'on peut créer une recommandation avec toutes les informations possibles.

### Test 3 : Recommandation pour différents types de cibles
Ce test vérifie qu'on peut recommander :
- un badge
- une attestation
- un émetteur
- une autre recommandation

### Test 4 : Erreurs lors de la création d'une recommandation
Ce test vérifie que des erreurs apparaissent quand les informations ne sont pas correctes.

### Test 5 : Conversion d'une recommandation en format JSON-LD
Ce test vérifie qu'une recommandation peut être transformée en format JSON-LD.

### Test 6 : Méthode pour vérifier si une recommandation est valide
Ce test vérifie que la méthode `is_valid()` fonctionne correctement.

### Test 7 : Validation d'une recommandation
Ce test vérifie que la fonction de validation détecte correctement les recommandations valides et invalides.

## Résumé

En tout, il y a 25 tests qui vérifient que toutes les parties de la bibliothèque PyOpenBadges fonctionnent correctement. Ces tests nous aident à être sûrs que la bibliothèque fait bien ce qu'elle doit faire.
