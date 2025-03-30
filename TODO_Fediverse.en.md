# Open Badges in the Fediverse: A Vision for Integration with ActivityPub

*Reflection document - March 30, 2025*

## Introduction

This document explores a vision where Open Badges (specification v3.0) would be integrated into the Fediverse via the ActivityPub protocol. This fusion could enable the creation of a decentralized and federated digital badge ecosystem, significantly increasing their reach and impact.

As a Fediverse engineer, I propose this vision as a natural evolution of both standards, which share fundamental common values and whose technical convergence is not only possible but desirable.

## Philosophical Convergence

Open Badges and ActivityPub share several fundamental principles that make their integration particularly relevant:

### 1. Digital Sovereignty

**Open Badges** places the individual at the center by giving them ownership of their badges and skills. Badges are portable and individuals can present them wherever they wish.

**ActivityPub** gives users ownership of their social identity and content, allowing them to choose their instance while interacting with the entire network.

→ *Convergence*: A federated badge system would allow users to own their certified skills while sharing them across the Fediverse, without dependence on a centralized platform.

### 2. Interoperability and Open Standards

**Open Badges** uses open standards (JSON-LD, Verifiable Credentials) that allow different systems to understand and verify badges.

**ActivityPub** is based on open standards (JSON-LD, ActivityStreams) that allow heterogeneous platforms to communicate.

→ *Convergence*: Both technologies use JSON-LD as an underlying format, which facilitates their technical integration.

### 3. Verifiability and Distributed Trust

**Open Badges** allows for cryptographic verification of badge authenticity and integrity.

**ActivityPub** allows for verification of actor identity via cryptographic signatures.

→ *Convergence*: These trust mechanisms can complement each other to create a distributed system where trust naturally flows through social relationships.

### 4. Resistance to Centralization

**Open Badges** seeks to democratize skills recognition outside traditional institutions.

**ActivityPub** aims to free social interactions from the domination of centralized platforms.

→ *Convergence*: Together, they can create a more resilient, diverse, and democratic model of skills recognition.

## Technical Vision: "FediBadges"

Here's how Open Badges could integrate with ActivityPub to create what we might call "FediBadges":

### 1. Modeling Badges as ActivityPub Objects

Badges would be modeled as ActivityPub objects, with their own type:

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

### 2. Badge Issuance and Reception Activities

Badge issuance would become a federated activity:

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

### 3. Badge Inbox

ActivityPub servers would treat these activities as special messages, storing them in the user's profile and making them accessible via specific endpoints:

```
GET /users/alice/badges
```

### 4. Verification and Trust

Badge verification could rely on existing trust mechanisms in the Fediverse web of trust:

1. **Cryptographic signatures**: Badges would be signed by the issuer
2. **Web of Trust**: Trust in an issuer would depend on their follower/following network
3. **Endorsements**: Other Fediverse actors could endorse a badge or an issuer

### 5. Protocol Extensions

New extensions for ActivityPub would be necessary:

```
- Badge Collection: A special collection for storing badges
- Badge Display: A standardized way to display badges in profiles
- Badge Verification: A mechanism for verifying badges
```

### 6. User Interface Integration

In Fediverse clients like Mastodon, Pleroma, etc.:

- Badges would appear on user profiles
- Filters would allow discovering people by their skills
- Users could easily share their new badges
- Organizations could create and issue badges directly from their account

## Concrete Use Cases

### 1. Community Learning

Alice participates in a programming course hosted on PeerTube. At the end, the instructor issues a badge via their ActivityPub server, which automatically appears on Alice's Mastodon profile.

### 2. Decentralized Professional Recognition

A company using its own ActivityPub server issues skill badges to its collaborators. These badges are visible on their profiles, regardless of the platform they use.

### 3. Learning Communities

A study group on a Lemmy server defines badges for different levels of expertise. Members can earn them and display them throughout the Fediverse.

### 4. Peer-to-Peer Certification

Individuals can create badges to recognize the contributions of other Fediverse members, creating an organic recognition system.

## Challenges to Overcome

1. **Moderation and spam**: Preventing massive issuance of worthless badges
2. **Privacy**: Allowing users to control which badges are visible and to whom
3. **Scalability**: Ensuring protocol extension remains lightweight and compatible with existing implementations
4. **Consensus**: Getting these extensions adopted by Fediverse developers

## Next Technical Steps

1. **Prototype**: Develop an ActivityPub extension for PyOpenBadges
2. **Proof of concept**: Modify an existing ActivityPub server to support FediBadges
3. **Documentation**: Draft a formal extension proposal for ActivityPub
4. **Demo client**: Create a web client that demonstrates the integration
5. **Standard**: Propose the extension to the W3C Social CG

## Philosophical Reflection on Uniting the Two Approaches

The fusion of Open Badges and ActivityPub represents more than just a technical integration—it's the convergence of two movements seeking to redistribute power in their respective domains.

Open Badges emerged to democratize skill recognition, traditionally monopolized by formal educational institutions. ActivityPub was born to free social interactions from the grip of centralized platforms.

Together, they could create a new ecosystem where:

- Skills recognition becomes a social, organic, and distributed process
- The value of certifications stems from their social context and verifiability, not from the centralized authority that issues them
- Individuals can build and carry their reputation across the network without depending on a platform
- Communities of interest can define their own standards of competence and recognition

This vision combines the rigor of certification standards with the fluidity of federated social networks, paving the way for new models of learning, collaboration, and professional recognition.

---

*This document is a conceptual exploration of the possible integration between Open Badges and ActivityPub. Its implementation would require more in-depth discussions with communities from both standards.*
