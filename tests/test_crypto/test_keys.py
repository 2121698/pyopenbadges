"""
Tests pour le module de gestion des clés cryptographiques
"""

import pytest
from pathlib import Path
import tempfile
import os

# Import des fonctions à tester (qui n'existent pas encore)
from pyopenbadges.crypto.keys import (
    generate_keypair,
    KeyPair,
    PublicKey,
    PrivateKey,
    load_keypair,
    load_public_key,
    load_private_key
)


class TestKeyGeneration:
    """Tests pour la génération et gestion des clés cryptographiques"""

    def test_generate_keypair_ed25519(self):
        """Test de génération d'une paire de clés Ed25519"""
        # Génération d'une paire de clés
        keypair = generate_keypair(algorithm="Ed25519")
        
        # Vérification du type
        assert isinstance(keypair, KeyPair)
        assert isinstance(keypair.public_key, PublicKey)
        assert isinstance(keypair.private_key, PrivateKey)
        
        # Vérification de l'algorithme
        assert keypair.algorithm == "Ed25519"
        assert keypair.public_key.algorithm == "Ed25519"
        assert keypair.private_key.algorithm == "Ed25519"
        
        # Vérification que les clés ne sont pas vides
        assert keypair.public_key.key_data
        assert keypair.private_key.key_data

    def test_generate_keypair_rsa(self):
        """Test de génération d'une paire de clés RSA"""
        # Génération d'une paire de clés
        keypair = generate_keypair(algorithm="RSA", key_size=2048)
        
        # Vérification du type
        assert isinstance(keypair, KeyPair)
        assert isinstance(keypair.public_key, PublicKey)
        assert isinstance(keypair.private_key, PrivateKey)
        
        # Vérification de l'algorithme
        assert keypair.algorithm == "RSA"
        assert keypair.public_key.algorithm == "RSA"
        assert keypair.private_key.algorithm == "RSA"
        
        # Vérification que les clés ne sont pas vides
        assert keypair.public_key.key_data
        assert keypair.private_key.key_data

    def test_generate_keypair_invalid_algorithm(self):
        """Test de génération avec un algorithme invalide"""
        with pytest.raises(ValueError):
            generate_keypair(algorithm="InvalidAlgorithm")

    def test_keypair_serialization(self):
        """Test de sérialisation d'une paire de clés"""
        # Génération d'une paire de clés
        keypair = generate_keypair(algorithm="Ed25519")
        
        # Sérialisation des clés
        public_pem = keypair.public_key.to_pem()
        private_pem = keypair.private_key.to_pem()
        
        # Vérification que les PEM ne sont pas vides
        assert public_pem and isinstance(public_pem, bytes)
        assert private_pem and isinstance(private_pem, bytes)
        
        # Vérification que les PEM contiennent les en-têtes appropriés
        assert b"-----BEGIN PUBLIC KEY-----" in public_pem
        assert b"-----END PUBLIC KEY-----" in public_pem
        assert b"-----BEGIN PRIVATE KEY-----" in private_pem
        assert b"-----END PRIVATE KEY-----" in private_pem


class TestKeySerialization:
    """Tests pour la sérialisation et désérialisation des clés"""

    def test_save_and_load_keypair(self):
        """Test de sauvegarde et chargement d'une paire de clés"""
        # Création d'un répertoire temporaire
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Génération d'une paire de clés
            keypair = generate_keypair(algorithm="Ed25519")
            
            # Chemins des fichiers
            private_key_path = os.path.join(tmpdirname, "private.pem")
            public_key_path = os.path.join(tmpdirname, "public.pem")
            
            # Sauvegarde des clés
            keypair.save(private_key_path=private_key_path, public_key_path=public_key_path)
            
            # Vérification que les fichiers existent
            assert os.path.exists(private_key_path)
            assert os.path.exists(public_key_path)
            
            # Chargement des clés
            loaded_keypair = load_keypair(private_key_path=private_key_path, public_key_path=public_key_path)
            
            # Vérification que les clés chargées sont du bon type
            assert isinstance(loaded_keypair, KeyPair)
            assert isinstance(loaded_keypair.public_key, PublicKey)
            assert isinstance(loaded_keypair.private_key, PrivateKey)
            
            # Vérification que l'algorithme est préservé
            assert loaded_keypair.algorithm == keypair.algorithm
            
            # Vérification que les clés sont identiques
            assert loaded_keypair.public_key.key_data == keypair.public_key.key_data
            assert loaded_keypair.private_key.key_data == keypair.private_key.key_data

    def test_load_public_key_only(self):
        """Test de chargement d'une clé publique seule"""
        # Création d'un répertoire temporaire
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Génération d'une paire de clés
            keypair = generate_keypair(algorithm="Ed25519")
            
            # Chemin du fichier
            public_key_path = os.path.join(tmpdirname, "public.pem")
            
            # Sauvegarde de la clé publique
            with open(public_key_path, 'wb') as f:
                f.write(keypair.public_key.to_pem())
            
            # Chargement de la clé publique
            loaded_public_key = load_public_key(public_key_path)
            
            # Vérification que la clé chargée est du bon type
            assert isinstance(loaded_public_key, PublicKey)
            
            # Vérification que l'algorithme est préservé
            assert loaded_public_key.algorithm == keypair.algorithm
            
            # Vérification que la clé est identique
            assert loaded_public_key.key_data == keypair.public_key.key_data
