"""
Module pour la signature des Verifiable Credentials.

Ce module fournit les fonctionnalités pour signer des Verifiable Credentials
et créer des preuves cryptographiques selon la spécification W3C.
"""

import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, Literal, Union
from copy import deepcopy

from pydantic import HttpUrl

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

from pyopenbadges.models.credential import OpenBadgeCredential, Proof
from pyopenbadges.crypto.keys import PrivateKey


def create_proof(
    credential_json: Dict[str, Any],
    private_key: PrivateKey,
    verification_method: Union[str, HttpUrl],
    proof_type: Literal["Ed25519Signature2020", "RsaSignature2018"] = "Ed25519Signature2020",
    proof_purpose: str = "assertionMethod"
) -> Proof:
    """
    Crée une preuve cryptographique pour un credential.

    Args:
        credential_json: Le credential au format JSON
        private_key: La clé privée pour signer
        verification_method: URI de la méthode de vérification
        proof_type: Type de preuve à créer
        proof_purpose: But de la preuve

    Returns:
        Proof: L'objet Proof contenant la signature
    """
    # Vérifier le type de preuve
    if proof_type not in ["Ed25519Signature2020", "RsaSignature2018"]:
        raise ValueError(f"Type de preuve non supporté: {proof_type}")
    
    # Vérifier la compatibilité entre l'algorithme de la clé et le type de preuve
    if proof_type == "Ed25519Signature2020" and private_key.algorithm != "Ed25519":
        raise ValueError("Le type de preuve Ed25519Signature2020 nécessite une clé Ed25519")
    if proof_type == "RsaSignature2018" and private_key.algorithm != "RSA":
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
    
    # Signer le JSON canonicalisé
    if proof_type == "Ed25519Signature2020":
        # Signer avec Ed25519
        key_obj = private_key.get_key_object()
        signature = key_obj.sign(canonical_json)
    elif proof_type == "RsaSignature2018":
        # Signer avec RSA
        key_obj = private_key.get_key_object()
        signature = key_obj.sign(
            canonical_json,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    
    # Encoder la signature en base64
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    
    # Créer l'objet Proof
    return Proof(
        type=proof_type,
        created=datetime.now(),
        verificationMethod=verification_method,
        proofPurpose=proof_purpose,
        proofValue=signature_base64
    )


def sign_credential(
    credential: OpenBadgeCredential,
    private_key: PrivateKey,
    verification_method: Union[str, HttpUrl],
    proof_type: Literal["Ed25519Signature2020", "RsaSignature2018"] = "Ed25519Signature2020",
    proof_purpose: str = "assertionMethod"
) -> OpenBadgeCredential:
    """
    Signe un OpenBadgeCredential avec une clé privée.

    Args:
        credential: Le credential à signer
        private_key: La clé privée pour signer
        verification_method: URI de la méthode de vérification
        proof_type: Type de preuve à créer
        proof_purpose: But de la preuve

    Returns:
        OpenBadgeCredential: Une copie signée du credential
    """
    # Vérifier que le credential n'a pas déjà une preuve
    if credential.proof is not None:
        raise ValueError("Le credential possède déjà une preuve")
    
    # Convertir le credential en JSON
    credential_json = credential.model_dump(mode='json')
    
    # Créer la preuve
    proof = create_proof(
        credential_json=credential_json,
        private_key=private_key,
        verification_method=verification_method,
        proof_type=proof_type,
        proof_purpose=proof_purpose
    )
    
    # Créer une copie du credential avec la preuve
    signed_credential = deepcopy(credential)
    signed_credential.proof = proof
    
    return signed_credential
