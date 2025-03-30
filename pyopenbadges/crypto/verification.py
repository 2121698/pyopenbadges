"""
Module pour la vérification des signatures des Verifiable Credentials.

Ce module fournit les fonctionnalités pour vérifier l'authenticité des
Verifiable Credentials et de leurs preuves cryptographiques.
"""

import json
import base64
from typing import Dict, Any, Optional, Union
from copy import deepcopy

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

from pyopenbadges.models.credential import OpenBadgeCredential, Proof
from pyopenbadges.crypto.keys import PublicKey


def verify_proof(
    credential_json: Dict[str, Any],
    proof: Proof,
    public_key: PublicKey
) -> bool:
    """
    Vérifie la validité d'une preuve cryptographique pour un credential.

    Args:
        credential_json: Le credential au format JSON
        proof: La preuve à vérifier
        public_key: La clé publique pour vérifier la signature

    Returns:
        bool: True si la preuve est valide, False sinon
    """
    # Vérifier la compatibilité entre l'algorithme de la clé et le type de preuve
    if proof.type == "Ed25519Signature2020" and public_key.algorithm != "Ed25519":
        raise ValueError("Le type de preuve Ed25519Signature2020 nécessite une clé Ed25519")
    if proof.type == "RsaSignature2018" and public_key.algorithm != "RSA":
        raise ValueError("Le type de preuve RsaSignature2018 nécessite une clé RSA")
    
    # Créer une copie du credential sans la preuve
    credential_copy = deepcopy(credential_json)
    if "proof" in credential_copy:
        del credential_copy["proof"]
    
    # Canonicaliser le JSON (trier les clés)
    canonical_json = json.dumps(
        credential_copy,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':')
    ).encode('utf-8')
    
    # Décoder la signature
    try:
        signature = base64.b64decode(proof.proofValue)
    except Exception as e:
        return False
    
    # Vérifier la signature
    try:
        if proof.type == "Ed25519Signature2020":
            # Vérifier avec Ed25519
            key_obj = public_key.get_key_object()
            key_obj.verify(signature, canonical_json)
            return True
        elif proof.type == "RsaSignature2018":
            # Vérifier avec RSA
            key_obj = public_key.get_key_object()
            key_obj.verify(
                signature,
                canonical_json,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        else:
            return False
    except InvalidSignature:
        return False
    except Exception as e:
        return False


def verify_credential(
    credential: OpenBadgeCredential,
    public_key: PublicKey
) -> bool:
    """
    Vérifie l'authenticité d'un OpenBadgeCredential signé.

    Args:
        credential: Le credential à vérifier
        public_key: La clé publique pour vérifier la signature

    Returns:
        bool: True si le credential est authentique, False sinon
    """
    # Vérifier que le credential a une preuve
    if credential.proof is None:
        raise ValueError("Le credential ne possède pas de preuve")
    
    # Convertir le credential en JSON
    credential_json = credential.model_dump(mode='json')
    
    # Vérifier la preuve
    return verify_proof(
        credential_json=credential_json,
        proof=credential.proof,
        public_key=public_key
    )
