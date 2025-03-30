"""
Module de gestion des clés cryptographiques pour PyOpenBadges.

Ce module fournit les fonctionnalités pour générer, charger, sauvegarder
et manipuler des clés cryptographiques utilisées pour signer et vérifier
les Verifiable Credentials.
"""

from typing import Optional, Tuple, Union, Literal
from pathlib import Path
import os

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)


class PublicKey:
    """
    Représente une clé publique utilisée pour vérifier les signatures.
    """

    def __init__(self, key_data: bytes, algorithm: str):
        """
        Initialise une clé publique.

        Args:
            key_data: Les données binaires de la clé publique
            algorithm: L'algorithme de la clé (Ed25519, RSA, etc.)
        """
        self.key_data = key_data
        self.algorithm = algorithm
        self._key_obj = None

        # Charger l'objet de clé approprié selon l'algorithme
        if algorithm == "Ed25519":
            self._key_obj = load_pem_public_key(key_data)
        elif algorithm == "RSA":
            self._key_obj = load_pem_public_key(key_data)
        else:
            raise ValueError(f"Algorithme non supporté: {algorithm}")

    def to_pem(self) -> bytes:
        """
        Convertit la clé publique en format PEM.

        Returns:
            bytes: La clé au format PEM
        """
        if isinstance(self._key_obj, ed25519.Ed25519PublicKey):
            return self._key_obj.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        elif isinstance(self._key_obj, rsa.RSAPublicKey):
            return self._key_obj.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        else:
            raise ValueError(f"Type de clé non supporté: {type(self._key_obj)}")

    def save(self, path: Union[str, Path]) -> None:
        """
        Sauvegarde la clé publique dans un fichier.

        Args:
            path: Chemin du fichier où sauvegarder la clé
        """
        with open(path, 'wb') as f:
            f.write(self.to_pem())

    def get_key_object(self):
        """
        Retourne l'objet de clé cryptographique sous-jacent.

        Returns:
            L'objet de clé cryptographique
        """
        return self._key_obj


class PrivateKey:
    """
    Représente une clé privée utilisée pour créer des signatures.
    """

    def __init__(self, key_data: bytes, algorithm: str):
        """
        Initialise une clé privée.

        Args:
            key_data: Les données binaires de la clé privée
            algorithm: L'algorithme de la clé (Ed25519, RSA, etc.)
        """
        self.key_data = key_data
        self.algorithm = algorithm
        self._key_obj = None

        # Charger l'objet de clé approprié selon l'algorithme
        if algorithm == "Ed25519":
            self._key_obj = load_pem_private_key(key_data, password=None)
        elif algorithm == "RSA":
            self._key_obj = load_pem_private_key(key_data, password=None)
        else:
            raise ValueError(f"Algorithme non supporté: {algorithm}")

    def to_pem(self) -> bytes:
        """
        Convertit la clé privée en format PEM.

        Returns:
            bytes: La clé au format PEM
        """
        if isinstance(self._key_obj, ed25519.Ed25519PrivateKey):
            return self._key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        elif isinstance(self._key_obj, rsa.RSAPrivateKey):
            return self._key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        else:
            raise ValueError(f"Type de clé non supporté: {type(self._key_obj)}")

    def save(self, path: Union[str, Path]) -> None:
        """
        Sauvegarde la clé privée dans un fichier.

        Args:
            path: Chemin du fichier où sauvegarder la clé
        """
        with open(path, 'wb') as f:
            f.write(self.to_pem())

    def get_key_object(self):
        """
        Retourne l'objet de clé cryptographique sous-jacent.

        Returns:
            L'objet de clé cryptographique
        """
        return self._key_obj

    def get_public_key(self) -> PublicKey:
        """
        Dérive la clé publique correspondante à cette clé privée.

        Returns:
            PublicKey: La clé publique correspondante
        """
        if isinstance(self._key_obj, ed25519.Ed25519PrivateKey):
            public_key = self._key_obj.public_key()
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return PublicKey(public_bytes, "Ed25519")
        elif isinstance(self._key_obj, rsa.RSAPrivateKey):
            public_key = self._key_obj.public_key()
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return PublicKey(public_bytes, "RSA")
        else:
            raise ValueError(f"Type de clé non supporté: {type(self._key_obj)}")


class KeyPair:
    """
    Représente une paire de clés (publique et privée) utilisée pour la signature et la vérification.
    """

    def __init__(self, private_key: PrivateKey, public_key: Optional[PublicKey] = None):
        """
        Initialise une paire de clés.

        Args:
            private_key: La clé privée
            public_key: La clé publique (optionnelle, peut être dérivée de la clé privée)
        """
        self.private_key = private_key
        self.public_key = public_key or private_key.get_public_key()
        
        # Vérifier que les clés utilisent le même algorithme
        if self.private_key.algorithm != self.public_key.algorithm:
            raise ValueError(
                f"Les algorithmes des clés ne correspondent pas: "
                f"{self.private_key.algorithm} vs {self.public_key.algorithm}"
            )
        
        self.algorithm = self.private_key.algorithm

    def save(self, private_key_path: Union[str, Path], public_key_path: Union[str, Path]) -> None:
        """
        Sauvegarde la paire de clés dans des fichiers.

        Args:
            private_key_path: Chemin du fichier où sauvegarder la clé privée
            public_key_path: Chemin du fichier où sauvegarder la clé publique
        """
        self.private_key.save(private_key_path)
        self.public_key.save(public_key_path)


def generate_keypair(
    algorithm: Literal["Ed25519", "RSA"] = "Ed25519", 
    key_size: int = 2048
) -> KeyPair:
    """
    Génère une nouvelle paire de clés.

    Args:
        algorithm: L'algorithme à utiliser (Ed25519 ou RSA)
        key_size: La taille de la clé (uniquement pour RSA)

    Returns:
        KeyPair: La paire de clés générée
    """
    if algorithm == "Ed25519":
        # Générer une clé Ed25519
        private_key = ed25519.Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return KeyPair(PrivateKey(private_bytes, "Ed25519"))
    
    elif algorithm == "RSA":
        # Générer une clé RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return KeyPair(PrivateKey(private_bytes, "RSA"))
    
    else:
        raise ValueError(f"Algorithme non supporté: {algorithm}")


def load_keypair(
    private_key_path: Union[str, Path], 
    public_key_path: Union[str, Path]
) -> KeyPair:
    """
    Charge une paire de clés à partir de fichiers.

    Args:
        private_key_path: Chemin du fichier contenant la clé privée
        public_key_path: Chemin du fichier contenant la clé publique

    Returns:
        KeyPair: La paire de clés chargée
    """
    # Charger la clé privée
    with open(private_key_path, 'rb') as f:
        private_key_data = f.read()
    
    # Déterminer l'algorithme
    if b"BEGIN PRIVATE KEY" in private_key_data:
        private_key_obj = load_pem_private_key(private_key_data, password=None)
        if isinstance(private_key_obj, ed25519.Ed25519PrivateKey):
            algorithm = "Ed25519"
        elif isinstance(private_key_obj, rsa.RSAPrivateKey):
            algorithm = "RSA"
        else:
            raise ValueError(f"Type de clé privée non supporté: {type(private_key_obj)}")
    else:
        raise ValueError("Format de clé privée non supporté")
    
    # Charger la clé publique
    with open(public_key_path, 'rb') as f:
        public_key_data = f.read()
    
    # Créer les objets de clé
    private_key = PrivateKey(private_key_data, algorithm)
    public_key = PublicKey(public_key_data, algorithm)
    
    return KeyPair(private_key, public_key)


def load_public_key(public_key_path: Union[str, Path]) -> PublicKey:
    """
    Charge une clé publique à partir d'un fichier.

    Args:
        public_key_path: Chemin du fichier contenant la clé publique

    Returns:
        PublicKey: La clé publique chargée
    """
    # Charger la clé publique
    with open(public_key_path, 'rb') as f:
        public_key_data = f.read()
    
    # Déterminer l'algorithme
    if b"BEGIN PUBLIC KEY" in public_key_data:
        public_key_obj = load_pem_public_key(public_key_data)
        if isinstance(public_key_obj, ed25519.Ed25519PublicKey):
            algorithm = "Ed25519"
        elif isinstance(public_key_obj, rsa.RSAPublicKey):
            algorithm = "RSA"
        else:
            raise ValueError(f"Type de clé publique non supporté: {type(public_key_obj)}")
    else:
        raise ValueError("Format de clé publique non supporté")
    
    return PublicKey(public_key_data, algorithm)


def load_private_key(private_key_path: Union[str, Path]) -> PrivateKey:
    """
    Charge une clé privée à partir d'un fichier.

    Args:
        private_key_path: Chemin du fichier contenant la clé privée

    Returns:
        PrivateKey: La clé privée chargée
    """
    # Charger la clé privée
    with open(private_key_path, 'rb') as f:
        private_key_data = f.read()
    
    # Déterminer l'algorithme
    if b"BEGIN PRIVATE KEY" in private_key_data:
        private_key_obj = load_pem_private_key(private_key_data, password=None)
        if isinstance(private_key_obj, ed25519.Ed25519PrivateKey):
            algorithm = "Ed25519"
        elif isinstance(private_key_obj, rsa.RSAPrivateKey):
            algorithm = "RSA"
        else:
            raise ValueError(f"Type de clé privée non supporté: {type(private_key_obj)}")
    else:
        raise ValueError("Format de clé privée non supporté")
    
    return PrivateKey(private_key_data, algorithm)
