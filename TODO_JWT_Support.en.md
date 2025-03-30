# TODO: JWT Support Implementation in PyOpenBadges

*Creation date: 03/30/2025*

## Context

The OpenBadge v3.0 specification explicitly states in section 8.2 (https://www.imsglobal.org/spec/ob/v3p0/#jwt-proof) that the JWT format can be used as an alternative to Linked Data Proofs to ensure badge authenticity and integrity. While PyOpenBadges already implements support for Linked Data Proofs, adding JWT support would significantly increase compatibility with other ecosystems.

> **Comment from IMS Global Engineer**: 
> 
> "The integration of JWT in the OpenBadge v3.0 specification was not a trivial choice. We observed that many digital identity and verification systems rely heavily on JSON Web Tokens (JWT). By explicitly including this option in the specification, we facilitate the adoption of the standard by a greater number of actors and increase interoperability with existing ecosystems. The JWT format also offers the advantage of being compact and easily transportable, which is particularly useful for mobile environments and modern web applications."

## Technical Implementation

### 1. Creating a JwtProof Class

```python
from typing import Optional, Dict, Any, Union
from datetime import datetime
import jwt
from pydantic import BaseModel, Field, HttpUrl

class JwtProof(BaseModel):
    """
    Represents a proof in JWT format for an OpenBadgeCredential
    
    Implements section 8.2 of the OpenBadge v3.0 specification
    """
    type: str = "JwtProof2020"
    jwt: str
    
    @classmethod
    def create(cls, credential_data: Dict[str, Any], private_key: str, 
               algorithm: str = "RS256", key_id: Optional[str] = None) -> 'JwtProof':
        """
        Creates a JWT proof for a credential
        
        Args:
            credential_data: Credential data to sign
            private_key: Private key in PEM or JWK format
            algorithm: Signature algorithm (default RS256)
            key_id: Key identifier used
            
        Returns:
            JwtProof: The created JWT proof object
        """
        header = {
            "alg": algorithm,
            "typ": "JWT"
        }
        
        if key_id:
            header["kid"] = key_id
            
        # Creating JWT signature
        token = jwt.encode(
            payload=credential_data,
            key=private_key,
            algorithm=algorithm,
            headers=header
        )
        
        return cls(type="JwtProof2020", jwt=token)
    
    def verify(self, public_key: str, algorithms: Union[str, list] = None) -> Dict[str, Any]:
        """
        Verifies the JWT signature and returns the decoded content
        
        Args:
            public_key: Public key to verify the signature
            algorithms: List of accepted algorithms
            
        Returns:
            Dict: The decoded JWT content
            
        Raises:
            jwt.exceptions.InvalidSignatureError: If the signature is invalid
            jwt.exceptions.ExpiredSignatureError: If the token is expired
            jwt.exceptions.DecodeError: If the token cannot be decoded
        """
        if algorithms is None:
            algorithms = ["RS256", "ES256", "EdDSA"]
            
        return jwt.decode(
            jwt=self.jwt,
            key=public_key,
            algorithms=algorithms,
            options={"verify_signature": True}
        )
```

> **Comment from IMS Global Engineer**: 
> 
> "For maximum compatibility, we recommend supporting at least the RS256, ES256, and EdDSA algorithms, as they are widely adopted in the digital identity ecosystem. The 'JwtProof2020' type is consistent with current Verifiable Credentials practices, but keep an eye on evolving W3C standards in this area that could influence future versions of the OpenBadge specification."

### 2. Updating the OpenBadgeCredential Class

```python
# In pyopenbadges/models/credential.py

from typing import Optional, Union
from .proof import Proof, JwtProof  # Add JwtProof import

class OpenBadgeCredential(BaseModel):
    # ... existing code ...
    
    # Modify the proof field to support JwtProof
    proof: Optional[Union[Proof, JwtProof]] = None
    
    def sign_jwt(self, private_key: str, algorithm: str = "RS256", 
                 key_id: Optional[str] = None) -> 'OpenBadgeCredential':
        """
        Signs the credential with the provided private key in JWT format
        
        Args:
            private_key: The private key to sign the credential
            algorithm: The signature algorithm to use
            key_id: The key identifier to include in the JWT header
            
        Returns:
            OpenBadgeCredential: The credential signed with a JWT proof
        """
        # First convert to JSON-LD without the proof
        credential_data = self.model_dump(exclude={"proof"})
        
        # Create the JWT proof
        jwt_proof = JwtProof.create(
            credential_data=credential_data,
            private_key=private_key,
            algorithm=algorithm,
            key_id=key_id
        )
        
        # Create a copy of the credential with the proof
        signed_credential = self.model_copy()
        signed_credential.proof = jwt_proof
        
        return signed_credential
    
    def verify_jwt(self, public_key: str, algorithms: Union[str, list] = None) -> bool:
        """
        Verifies the JWT proof of the credential
        
        Args:
            public_key: The public key to verify the signature
            algorithms: The algorithms accepted for verification
            
        Returns:
            bool: True if the signature is valid, False otherwise
            
        Raises:
            ValueError: If the credential does not have a JWT proof
        """
        if self.proof is None or not isinstance(self.proof, JwtProof):
            raise ValueError("The credential does not have a JWT proof")
            
        try:
            decoded = self.proof.verify(public_key, algorithms)
            
            # Check that the decoded content matches the credential
            credential_data = self.model_dump(exclude={"proof"})
            
            # Verification of essential fields
            return (decoded.get("id") == credential_data.get("id") and
                    decoded.get("type") == credential_data.get("type"))
        except Exception as e:
            return False
```

> **Comment from IMS Global Engineer**: 
> 
> "When developing the v3.0 specification, we paid particular attention to backward compatibility and interoperability. The dual-mode implementation (Linked Data Proofs and JWT) is exactly what we had in mind. Note that for full compliance, your implementation should allow for complete serialization of the credential in JWT (not just the proof), as indicated in section 8.2.3. This allows third-party systems to verify the badge without needing to understand the JSON-LD format."

## Implementation Steps

1. **Dependencies**
   - Add PyJWT and cryptography to the pyproject.toml file
   ```toml
   [tool.poetry.dependencies]
   python = "^3.8"
   pydantic = "^2.0.0"
   pyjwt = "^2.6.0"
   cryptography = "^40.0.0"  # For encryption algorithms
   ```

2. **File Structure**
   - Create or update `pyopenbadges/models/proof.py` to include JwtProof
   - Update `pyopenbadges/models/__init__.py` to expose JwtProof
   - Update `pyopenbadges/models/credential.py` to integrate JWT support

3. **Tests**
   - Create `tests/test_jwt_proof.py` with tests covering:
     - JwtProof creation
     - Signing a credential with JWT
     - JWT signature verification
     - Tests with different algorithms (RS256, ES256, EdDSA)
     - Error cases and exceptions

4. **Documentation**
   - Update README.md to mention JWT support
   - Add a new tutorial: TUTORIAL.jwt.md
   - Update existing documentation to include JWT examples

> **Comment from IMS Global Engineer**: 
> 
> "An often overlooked aspect in specification implementations concerns support for different format transformations (JSON-LD ⟷ JWT). For a robust implementation, make sure to test not only the creation and verification of JWTs, but also the bidirectional transformation between formats. This is essential to ensure interoperability with the various systems in the ecosystem. Developers will also appreciate clear examples showing how these transformations fit into common usage flows."

## Security Considerations

1. **Key Management**
   - Provide utilities for generating JWT-compatible key pairs
   - Document best practices for key rotation and secure storage

2. **Recommended Algorithms**
   - Document preferred algorithms (RS256, ES256, EdDSA)
   - Include warnings about less secure algorithms (e.g., HS256 without appropriate context)

3. **Critical Field Validation**
   - Ensure JWT verification includes validation of issuer, expiration, and audience

> **Comment from IMS Global Engineer**: 
> 
> "Cryptographic key management is a critical aspect in any system using JWTs. Our experience shows that this is often the weak link in implementations. Beyond simple signing and verification, consider providing utilities for key lifecycle management (generation, rotation, revocation) and clearly document best practices. The security of the badge ecosystem depends on the correct implementation of these aspects by each actor."

## Resources and References

1. OpenBadge v3.0 Specification:
   - https://www.imsglobal.org/spec/ob/v3p0/
   - JWT specific section: https://www.imsglobal.org/spec/ob/v3p0/#jwt-proof

2. JWT Standards:
   - RFC 7519 (JWT): https://tools.ietf.org/html/rfc7519
   - RFC 7515 (JWS): https://tools.ietf.org/html/rfc7515
   - RFC 7518 (JWA): https://tools.ietf.org/html/rfc7518

3. Python Libraries:
   - PyJWT: https://pyjwt.readthedocs.io/
   - cryptography: https://cryptography.io/

> **Final Comment from IMS Global Engineer**: 
> 
> "Implementing JWT support in your PyOpenBadges library is an important step in strengthening the OpenBadge ecosystem. As a standards organization, we are delighted to see developers investing in the complete implementation of the specification, including advanced features like JWT support.
> 
> A suggestion for the future: also consider implementing section 8.3 of the specification concerning 'Embedded Proofs'. This approach allows proofs to be directly integrated into formats such as PNG or SVG, which is particularly useful for visual badges.
> 
> Thank you for contributing to the OpenBadge ecosystem and please don't hesitate to contact us through our official channels for any clarification on the specification."
