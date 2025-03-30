# Steganography Integration in PyOpenBadges

*Creation date: 03/30/2025*

## Context

The OpenBadge v3.0 specification mentions in section 8.3 (Embedded Proofs) the possibility of embedding proofs directly into the badge. Steganography - the art of hiding information within other data - offers an elegant approach to integrating all badge data (metadata, cryptographic proofs) directly into the image visually representing the badge.

## Advantages of Steganography for Open Badges

### 1. Enhanced Portability
- An image containing its own badge becomes a single, self-contained file
- Facilitates sharing on social networks and other platforms that accept images but not complex metadata
- Eliminates the problem of maintaining a link between the visual image and badge data

### 2. Badge-Visual Link Persistence
- In traditional systems, the image and badge metadata can become separated during sharing
- With steganography, even if the image is copied or downloaded, the badge data remains embedded
- Ensures the conceptual integrity of the badge as a single object

### 3. Offline Verification
- If the complete badge (including its proof) is embedded in the image, it can be verified without access to the original server
- Useful in contexts with limited connectivity or for quick verifications
- Reduces dependence on online services for validation

### 4. Specification Compliance
- Addresses the intent of section 8.3 of the Open Badges v3.0 specification regarding "Embedded Proofs"
- Offers a technical implementation of an important concept in the specification

## Technical Considerations and Challenges

### 1. Data Size
- Complete badges with proofs can occupy several kilobytes of data
- The steganographic capacity of an image is limited by its size and the algorithm type used
- Possible strategies:
  - Compression of badge data before embedding
  - Use of algorithms with high embedding capacity
  - Limiting embedded content to essential data only

### 2. Robustness
- Image modifications (resizing, compression, cropping) can alter or destroy hidden data
- Importance of robustness to common transformations:
  - Algorithms resistant to JPEG compression
  - Data redundancy techniques
  - Error detection and correction mechanisms

### 3. Security and Privacy
- If poorly implemented, steganography could unintentionally expose personal data
- Implementation considerations:
  - Optional encryption of embedded data
  - Granular control of what is embedded (exclusion of sensitive information)
  - Clear documentation for users about what is embedded in the image

### 4. Visual Balance
- Embedding must not visibly degrade the badge image quality
- Adjustable parameters allowing priority to:
  - Imperceptibility (visual preservation)
  - Capacity (amount of embeddable data)
  - Robustness (resistance to transformations)

## Implementation Proposal for PyOpenBadges

### 1. New `EmbeddedProof` Class

```python
from typing import Optional, Union
from PIL import Image
import io
from pydantic import BaseModel, Field
import json
import base64

class EmbeddedProof(BaseModel):
    """
    Represents a proof embedded in an image via steganography
    
    Implements section 8.3 of the OpenBadge v3.0 specification
    """
    type: str = "EmbeddedProof2020"
    image_format: str = "png"  # Image format (png recommended for steganography)
    embedding_method: str = "lsb"  # Embedding method (LSB by default)
    
    @classmethod
    def create(cls, credential_data: dict, image_path: str, 
               method: str = "lsb", password: Optional[str] = None) -> 'EmbeddedProof':
        """
        Embeds credential data into an image via steganography
        
        Args:
            credential_data: Credential data to embed
            image_path: Path to the image in which to embed the data
            method: Steganography method to use ('lsb', 'dct', 'dwt')
            password: Optional password to encrypt the data
            
        Returns:
            EmbeddedProof: The proof object with the embedded image
        """
        # Implementation to be defined
        pass
    
    def extract_credential(self, password: Optional[str] = None) -> dict:
        """
        Extracts credential data embedded in the image
        
        Args:
            password: Password to decrypt the data (if necessary)
            
        Returns:
            dict: The extracted credential data
            
        Raises:
            ValueError: If the data cannot be extracted
        """
        # Implementation to be defined
        pass
```

### 2. Extension of `OpenBadgeCredential`

```python
def embed_in_image(self, image_path: str, output_path: Optional[str] = None,
                  method: str = "lsb", password: Optional[str] = None) -> str:
    """
    Embeds the credential into an image via steganography
    
    Args:
        image_path: Path to the original image
        output_path: Path for the resulting image (if None, uses image_path)
        method: Steganography method ('lsb', 'dct', 'dwt')
        password: Optional password to encrypt the data
        
    Returns:
        str: Path to the image containing the embedded credential
    """
    # Convert credential to JSON
    credential_json = self.model_dump_json()
    
    # Use steganography library to embed data
    # ...
    
    return output_path or image_path

@classmethod
def from_image(cls, image_path: str, password: Optional[str] = None) -> 'OpenBadgeCredential':
    """
    Extracts a credential from an image via steganography
    
    Args:
        image_path: Path to the image containing the credential
        password: Password to decrypt the data (if necessary)
        
    Returns:
        OpenBadgeCredential: The extracted credential
        
    Raises:
        ValueError: If the image does not contain a valid credential
    """
    # Extract data from the image
    # ...
    
    # Convert data to credential
    return cls.model_validate_json(credential_json)
```

### 3. Implementation of Steganography Algorithms

Several approaches would be implemented, each with its own advantages:

#### LSB (Least Significant Bit)
- **Description**: Modifies the least significant bits of pixels
- **Advantages**: Simple, good capacity
- **Disadvantages**: Not very robust to modifications

#### DCT (Discrete Cosine Transform)
- **Description**: Modifies the coefficients of the discrete cosine transform
- **Advantages**: More robust to JPEG compression
- **Disadvantages**: More limited capacity

#### DWT (Discrete Wavelet Transform)
- **Description**: Modifies the wavelet transform coefficients
- **Advantages**: Very robust to transformations
- **Disadvantages**: Implementation complexity

### 4. Dependencies to Add

```toml
[tool.poetry.dependencies]
python = "^3.8"
pydantic = "^2.0.0"
Pillow = "^9.0.0"  # For image manipulation
stegano = "^0.10.0"  # Basic steganography library
pywavelets = "^1.3.0"  # For the DWT method
numpy = "^1.23.0"  # Required for transformations
cryptography = "^40.0.0"  # For data encryption
```

## TDD Implementation Plan

### 1. Basic Tests

```python
def test_embed_and_extract_credential_lsb():
    """Tests embedding and extracting a credential with the LSB method"""
    # Create a credential
    credential = create_test_credential()
    
    # Embed in an image
    output_path = credential.embed_in_image("test_images/badge.png", 
                                           "test_images/badge_with_data.png")
    
    # Extract the credential
    extracted = OpenBadgeCredential.from_image(output_path)
    
    # Verify that the extracted credential matches the original
    assert extracted.id == credential.id
    assert extracted.type == credential.type
    # etc.
```

### 2. Robustness Tests

```python
def test_extract_after_resize():
    """Tests extraction after image resizing"""
    # Create and embed
    # ...
    
    # Resize the image
    # ...
    
    # Attempt to extract
    # ...
```

### 3. Limit Tests

```python
def test_capacity_limits():
    """Tests embedding capacity limits"""
    # Create a credential with lots of data
    # ...
    
    # Try to embed in a small image
    # ...
```

## User Interface Considerations

### 1. Command Line Interface

```bash
# Embed a badge in an image
python -m pyopenbadges embed --credential badge.json --image logo.png --output badge_embedded.png

# Extract a badge from an image
python -m pyopenbadges extract --image badge_embedded.png --output extracted_badge.json
```

### 2. Programmatic Interface

```python
# Embed
credential.embed_in_image("logo.png", "badge_embedded.png")

# Extract
credential = OpenBadgeCredential.from_image("badge_embedded.png")
```

## Conclusion

Integrating steganography features into PyOpenBadges would open new possibilities for badge sharing and verification. Although it's an advanced feature that presents certain technical challenges, it aligns perfectly with the spirit of the OpenBadge v3.0 specification and could become an important differentiator for this library.

This approach would also enrich the digital badge ecosystem by enabling their sharing in contexts where complex metadata is typically not preserved, such as social media platforms, thus broadening the reach and utility of Open Badges.
