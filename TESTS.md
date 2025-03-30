# PyOpenBadges Tests - Simple Explanation

[![🇫🇷 Version française](https://img.shields.io/badge/🇫🇷_Version_française-blue.svg)](TESTS.fr.md)

This document explains the tests for the PyOpenBadges library. These tests verify that everything works correctly.

## What is a test?

A test is like a verification. It ensures that a part of the code does what it's supposed to do.

## Tests for Profiles

Profiles are used to represent people or organizations that create badges.

### Test 1: Creating a profile with minimal information
This test verifies that a profile can be created with just:
- an identifier (URL)
- a type
- a name

### Test 2: Creating a complete profile
This test verifies that a profile can be created with all information:
- identifier, type, name
- description
- image
- address
- email, phone
- website

### Test 3: Errors when creating a profile
This test verifies that errors appear when:
- required information is missing
- incorrect information is provided (such as a badly formatted email address)

### Test 4: Converting a profile to JSON-LD format
This test verifies that a profile can be transformed into JSON-LD format (a standard format for the internet).

### Test 5: Validating a profile
This test verifies that the validation function:
- accepts valid profiles
- rejects invalid profiles
- detects errors in incorrect profiles

## Tests for Badges (Achievement)

Badges are the rewards that can be earned.

### Test 1: Creating a badge with minimal information
This test verifies that a badge can be created with just:
- an identifier
- a type
- a name
- an issuer (the person who gives the badge)

### Test 2: Creating a complete badge
This test verifies that a badge can be created with all possible information:
- identifier, type, name
- description
- image
- criteria for earning the badge
- tags
- alignment with standards

### Test 3: Badge with reference to an issuer
This test verifies that a badge can be created by referencing an issuer:
- by its URL
- or by using the issuer object directly

### Test 4: Errors when creating a badge
This test verifies that errors appear when the rules for creating a badge are not followed.

### Test 5: Converting a badge to JSON-LD format
This test verifies that a badge can be transformed into JSON-LD format.

### Test 6: Validating a badge
This test verifies that the validation function correctly detects valid and invalid badges.

## Tests for Credentials (OpenBadgeCredential)

Credentials are documents that prove a person has received a badge.

### Test 1: Creating a credential with minimal information
This test verifies that a credential can be created with just the essential information.

### Test 2: Creating a complete credential
This test verifies that a credential can be created with all possible information:
- identifier, type
- issuer
- issuance date
- expiration date
- recipient
- badge
- evidence

### Test 3: Credential with references to other objects
This test verifies that references can be made to an issuer, a badge, and a recipient.

### Test 4: Errors when creating a credential
This test verifies that errors appear when the information is not correct.

### Test 5: Converting a credential to JSON-LD format
This test verifies that a credential can be transformed into JSON-LD format.

### Test 6: Method for checking if a credential is valid
This test verifies that the `is_valid()` method works correctly.

### Test 7: Validating a credential
This test verifies that the validation function correctly detects valid and invalid credentials.

## Tests for Endorsements (EndorsementCredential)

Endorsements are documents that show a person or organization approves a badge.

### Test 1: Creating an endorsement with minimal information
This test verifies that an endorsement can be created with just the essential information.

### Test 2: Creating a complete endorsement
This test verifies that an endorsement can be created with all possible information.

### Test 3: Endorsement for different types of targets
This test verifies that the following can be endorsed:
- a badge
- a credential
- an issuer
- another endorsement

### Test 4: Errors when creating an endorsement
This test verifies that errors appear when the information is not correct.

### Test 5: Converting an endorsement to JSON-LD format
This test verifies that an endorsement can be transformed into JSON-LD format.

### Test 6: Method for checking if an endorsement is valid
This test verifies that the `is_valid()` method works correctly.

### Test 7: Validating an endorsement
This test verifies that the validation function correctly detects valid and invalid endorsements.

## Tests for Cryptographic Features

Cryptographic features help make sure badges are secure and can be trusted.

### Test 1: Generating cryptographic keys
This test verifies that the library can create secure keys for signing badges.

### Test 2: Saving and loading keys
This test verifies that keys can be saved to files and loaded back correctly.

### Test 3: Creating a cryptographic proof
This test verifies that a digital proof can be created to make a badge secure.

### Test 4: Signing a credential
This test verifies that a credential can be signed with a private key.

### Test 5: Verifying a signature
This test verifies that a signature can be checked with a public key.

### Test 6: Detecting tampered credentials
This test verifies that the library can detect when someone changes a signed credential.

### Test 7: Credential signing integration
This test verifies that the credential model can directly sign itself.

### Test 8: Credential verification integration
This test verifies that the credential model can verify its own signature.

### Test 9: Complete cryptographic workflow
This test verifies the entire process from key generation to signature verification works together.

### Test 10: JSON serialization of signed credentials
This test verifies that signed credentials can be saved as JSON correctly.

## Summary

In total, there are 48 tests that verify all parts of the PyOpenBadges library work correctly. These tests help us ensure that the library does what it's supposed to do.
