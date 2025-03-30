# Open Badges dans le Fediverse : Vision d'une intégration avec ActivityPub

*Document de réflexion - 30 mars 2025*

## Introduction

Ce document explore une vision où les Open Badges (spécification v3.0) seraient intégrés au Fediverse via le protocole ActivityPub. Cette fusion pourrait permettre la création d'un écosystème décentralisé et fédéré de badges numériques, augmentant considérablement leur portée et leur impact.

En tant qu'ingénieur du Fediverse, je propose cette vision comme une évolution naturelle des deux standards, qui partagent des valeurs fondamentales communes et dont la convergence technique est non seulement possible, mais souhaitable.

## Convergence philosophique

Open Badges et ActivityPub partagent plusieurs principes fondamentaux qui rendent leur intégration particulièrement pertinente :

### 1. Souveraineté numérique

**Open Badges** place l'individu au centre en lui donnant la propriété de ses badges et compétences. Les badges sont portables et l'individu peut les présenter où il le souhaite.

**ActivityPub** donne aux utilisateurs la propriété de leur identité sociale et de leurs contenus, en leur permettant de choisir leur instance tout en interagissant avec l'ensemble du réseau.

→ *Convergence* : Un système de badges fédéré permettrait aux utilisateurs de posséder leurs compétences certifiées tout en les partageant à travers le Fediverse, sans dépendance à une plateforme centralisée.

### 2. Interopérabilité et standards ouverts

**Open Badges** utilise des standards ouverts (JSON-LD, Verifiable Credentials) qui permettent à différents systèmes de comprendre et vérifier les badges.

**ActivityPub** est basé sur des standards ouverts (JSON-LD, ActivityStreams) qui permettent à des plateformes hétérogènes de communiquer.

→ *Convergence* : Les deux technologies utilisent JSON-LD comme format sous-jacent, ce qui facilite leur intégration technique.

### 3. Vérifiabilité et confiance distribuée

**Open Badges** permet la vérification cryptographique de l'authenticité et de l'intégrité des badges.

**ActivityPub** permet la vérification de l'identité des acteurs via des signatures cryptographiques.

→ *Convergence* : Ces mécanismes de confiance peuvent se compléter pour créer un système distribué où la confiance circule naturellement à travers les relations sociales.

### 4. Résistance à la centralisation

**Open Badges** cherche à démocratiser la reconnaissance des compétences en dehors des institutions traditionnelles.

**ActivityPub** vise à libérer les interactions sociales de la domination des plateformes centralisées.

→ *Convergence* : Ensemble, ils peuvent créer un modèle de reconnaissance des compétences plus résilient, diversifié et démocratique.

## Vision technique : "FediBadges"

Voici comment les Open Badges pourraient s'intégrer à ActivityPub pour créer ce que nous pourrions appeler "FediBadges" :

### 1. Modélisation des badges comme objets ActivityPub

Les badges seraient modélisés comme des objets ActivityPub, avec leur propre type :

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/openbadges/v3"
  ],
  "type": ["Object", "Achievement"],
  "id": "https://badge-issuer.org/badges/programming-101",
  "name": "Programming 101",
  "content": "This badge certifies basic programming skills",
  "image": {
    "type": "Image",
    "mediaType": "image/png",
    "url": "https://badge-issuer.org/badges/programming-101/image"
  },
  "issuer": {
    "type": ["Organization", "Profile"],
    "id": "https://badge-issuer.org/profile",
    "name": "Coding Academy"
  }
}
```

### 2. Activités d'émission et de réception de badges

L'émission d'un badge deviendrait une activité fédérée :

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Award",
  "actor": {
    "type": "Organization",
    "id": "https://badge-issuer.org/profile",
    "name": "Coding Academy"
  },
  "object": {
    "type": ["Achievement", "OpenBadgeCredential"],
    "id": "https://badge-issuer.org/badges/programming-101"
  },
  "target": {
    "type": "Person",
    "id": "https://social.example/@alice"
  },
  "published": "2025-03-30T10:45:00Z"
}
```

### 3. Boîte de réception de badges

Les serveurs ActivityPub traiteraient ces activités comme des messages spéciaux, les stockant dans le profil de l'utilisateur et les rendant accessibles via des endpoints spécifiques :

```
GET /users/alice/badges
```

### 4. Vérification et confiance

La vérification des badges pourrait s'appuyer sur les mécanismes existants du Web de confiance du Fediverse :

1. **Signatures cryptographiques** : Les badges seraient signés par l'émetteur
2. **Web of Trust** : La confiance accordée à un émetteur dépendrait de son réseau de followers/following
3. **Endorsements** : D'autres acteurs du Fediverse pourraient avaliser un badge ou un émetteur

### 5. Extensions de protocole

De nouvelles extensions pour ActivityPub seraient nécessaires :

```
- Badge Collection : Une collection spéciale pour stocker les badges
- Badge Display : Une façon standardisée d'afficher les badges dans les profils
- Badge Verification : Un mécanisme pour vérifier les badges
```

### 6. Intégration avec l'interface utilisateur

Dans les clients du Fediverse comme Mastodon, Pleroma, etc. :

- Les badges apparaîtraient sur les profils des utilisateurs
- Des filtres permettraient de découvrir des personnes selon leurs compétences
- Les utilisateurs pourraient facilement partager leurs nouveaux badges
- Les organisations pourraient créer et émettre des badges directement depuis leur compte

## Cas d'usage concrets

### 1. Apprentissage communautaire

Alice participe à un cours de programmation hébergé sur PeerTube. À la fin, l'instructeur émet un badge via son serveur ActivityPub, qui apparaît automatiquement sur le profil d'Alice sur Mastodon.

### 2. Reconnaissance professionnelle décentralisée

Une entreprise utilisant son propre serveur ActivityPub émet des badges de compétence à ses collaborateurs. Ces badges sont visibles sur leurs profils, quelle que soit la plateforme qu'ils utilisent.

### 3. Communautés d'apprentissage

Un groupe d'étude sur un serveur Lemmy définit des badges pour différents niveaux d'expertise. Les membres peuvent les gagner et les afficher partout dans le Fediverse.

### 4. Certification pair-à-pair

Des individus peuvent créer des badges pour reconnaître les contributions d'autres membres du Fediverse, créant ainsi un système organique de reconnaissance.

## Défis à surmonter

1. **Modération et spam** : Empêcher l'émission massive de badges sans valeur
2. **Vie privée** : Permettre aux utilisateurs de contrôler quels badges sont visibles et par qui
3. **Extensibilité** : S'assurer que l'extension du protocole reste légère et compatible avec les implémentations existantes
4. **Consensus** : Faire adopter ces extensions par les développeurs du Fediverse

## Prochaines étapes techniques

1. **Prototype** : Développer une extension ActivityPub pour PyOpenBadges
2. **Preuve de concept** : Modifier un serveur ActivityPub existant pour supporter les FediBadges
3. **Documentation** : Rédiger une proposition d'extension formelle pour ActivityPub
4. **Client de démonstration** : Créer un client web qui montre l'intégration
5. **Standard** : Proposer l'extension au Social CG du W3C

## Réflexion philosophique sur l'union des deux approches

La fusion des Open Badges et d'ActivityPub représente plus qu'une simple intégration technique - c'est la convergence de deux mouvements qui cherchent à redistribuer le pouvoir dans leurs domaines respectifs.

Open Badges a émergé pour démocratiser la reconnaissance des compétences, traditionnellement monopolisée par les institutions éducatives formelles. ActivityPub est né pour libérer les interactions sociales de l'emprise des plateformes centralisées.

Ensemble, ils pourraient créer un nouvel écosystème où :

- La reconnaissance des compétences devient un processus social, organique et distribué
- La valeur des certifications découle de leur contexte social et de leur vérifiabilité, pas de l'autorité centralisée qui les émet
- Les individus peuvent construire et porter leur réputation à travers le réseau sans dépendre d'une plateforme
- Les communautés d'intérêt peuvent définir leurs propres standards de compétence et de reconnaissance

Cette vision combine la rigueur des standards de certification avec la fluidité des réseaux sociaux fédérés, ouvrant la voie à de nouveaux modèles d'apprentissage, de collaboration et de reconnaissance professionnelle.

---

*Ce document est une exploration conceptuelle de l'intégration possible entre Open Badges et ActivityPub. Sa mise en œuvre nécessiterait des discussions plus approfondies avec les communautés des deux standards.*
