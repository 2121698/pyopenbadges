"""
Module de gestion cryptographique pour PyOpenBadges

Ce module fournit les fonctionnalités nécessaires pour signer et vérifier
les Verifiable Credentials selon la spécification OpenBadge v3.0.
"""

from .keys import (
    generate_keypair,
    KeyPair,
    PublicKey,
    PrivateKey,
    load_keypair,
    load_public_key,
    load_private_key
)

from .signing import (
    sign_credential,
    create_proof
)

from .verification import (
    verify_credential,
    verify_proof
)

__all__ = [
    "generate_keypair",
    "KeyPair",
    "PublicKey",
    "PrivateKey",
    "load_keypair",
    "load_public_key",
    "load_private_key",
    "sign_credential",
    "create_proof",
    "verify_credential",
    "verify_proof"
]
