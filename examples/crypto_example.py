#!/usr/bin/env python
"""
Exemple d'utilisation des fonctionnalités cryptographiques de PyOpenBadges

Cet exemple montre comment:
1. Générer des clés cryptographiques
2. Créer un OpenBadgeCredential
3. Signer le credential
4. Vérifier la signature
5. Détecter une falsification
"""

import os
import json
from datetime import datetime

# Classe pour encoder les objets datetime et Pydantic en JSON
class CustomJSONEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les objets datetime et Pydantic"""
    def default(self, obj):
        # Gérer les objets datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Gérer les objets Pydantic (comme HttpUrl)
        if hasattr(obj, "__str__"):
            try:
                return str(obj)
            except:
                pass
                
        # Gérer les objets Pydantic BaseModel
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except:
                pass
                
        return super().default(obj)

from pyopenbadges.crypto import generate_keypair
from pyopenbadges.models import Profile, Achievement, OpenBadgeCredential, AchievementSubject


def main():
    """Fonction principale de l'exemple"""
    print("=== Exemple d'utilisation des fonctionnalités cryptographiques de PyOpenBadges ===\n")
    
    # 1. Générer une paire de clés
    print("1. Génération d'une paire de clés Ed25519...")
    keypair = generate_keypair(algorithm="Ed25519")
    print(f"   Type de clé: {keypair.algorithm}")
    print(f"   Clé privée: {keypair.private_key.algorithm}")
    print(f"   Clé publique: {keypair.public_key.algorithm}\n")
    
    # Sauvegarder les clés dans des fichiers temporaires
    private_key_file = "temp_private_key.pem"
    public_key_file = "temp_public_key.pem"
    keypair.save(private_key_file, public_key_file)
    print(f"   Clé privée sauvegardée dans {private_key_file}")
    print(f"   Clé publique sauvegardée dans {public_key_file}\n")
    
    # 2. Créer un émetteur (Profile)
    print("2. Création d'un émetteur...")
    issuer = Profile(
        id="https://example.org/issuers/1",
        type="Profile",
        name="Université Exemple",
        description="Une université fictive pour l'exemple",
        url="https://example.org"
    )
    print(f"   Émetteur: {issuer.name}\n")
    
    # 3. Créer un badge (Achievement)
    print("3. Création d'un badge...")
    badge = Achievement(
        id="https://example.org/badges/python-dev",
        type="Achievement",
        name="Développeur Python Certifié",
        description="Ce badge certifie que le détenteur maîtrise le développement en Python",
        issuer=issuer
    )
    print(f"   Badge: {badge.name}\n")
    
    # 4. Créer un credential
    print("4. Création d'un OpenBadgeCredential...")
    credential = OpenBadgeCredential(
        id="https://example.org/credentials/12345",
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
    print(f"   Credential créé pour: {credential.credentialSubject.name}")
    print(f"   Badge attribué: {credential.credentialSubject.achievement.name}\n")
    
    # 5. Signer le credential
    print("5. Signature du credential...")
    signed_credential = credential.sign(
        private_key=keypair.private_key,
        verification_method="https://example.org/issuers/1/keys/1"
    )
    print(f"   Type de preuve: {signed_credential.proof.type}")
    print(f"   Date de création: {signed_credential.proof.created}")
    print(f"   Méthode de vérification: {signed_credential.proof.verificationMethod}")
    print(f"   Valeur de la preuve: {signed_credential.proof.proofValue[:30]}...\n")
    
    # 6. Vérifier la signature
    print("6. Vérification de la signature...")
    is_valid = signed_credential.verify_signature(
        public_key=keypair.public_key
    )
    print(f"   Le credential est authentique: {is_valid}\n")
    
    # 7. Créer une copie falsifiée
    print("7. Création d'une copie falsifiée du credential...")
    tampered_credential = signed_credential.model_copy(deep=True)
    tampered_credential.credentialSubject.id = "did:example:hacker456"
    print(f"   ID original: {signed_credential.credentialSubject.id}")
    print(f"   ID falsifié: {tampered_credential.credentialSubject.id}\n")
    
    # 8. Vérifier la signature de la copie falsifiée
    print("8. Vérification de la signature de la copie falsifiée...")
    is_tampered_valid = tampered_credential.verify_signature(
        public_key=keypair.public_key
    )
    print(f"   Le credential falsifié est authentique: {is_tampered_valid}\n")
    
    # 9. Convertir en JSON-LD
    print("9. Conversion en JSON-LD...")
    json_ld = signed_credential.to_json_ld()
    print(f"   JSON-LD généré avec {len(json_ld)} champs")
    
    # Sauvegarder le JSON-LD dans un fichier
    json_file = "signed_credential.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_ld, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
    print(f"   JSON-LD sauvegardé dans {json_file}\n")
    
    # 10. Nettoyer les fichiers temporaires
    print("10. Nettoyage des fichiers temporaires...")
    # Décommentez les lignes suivantes pour supprimer les fichiers
    # os.remove(private_key_file)
    # os.remove(public_key_file)
    # os.remove(json_file)
    print(f"   Les fichiers {private_key_file}, {public_key_file} et {json_file} ont été conservés pour référence.\n")
    
    print("=== Fin de l'exemple ===")


if __name__ == "__main__":
    main()
