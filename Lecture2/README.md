# Lecture2: Discrete Cosine Transform (DCT) in Steganograohy

## Basic Concept

In digital image processing, we often need to:

- Compress images (JPEG)
- Analyze frequency components
- Remove noise
- Embed hidden information (steganography)

However, raw images are stored in the spatial domain, meaning:
Each pixel represents intensity at a specific location.

But many operations are easier and more efficient in the frequency domain.

The Discrete Cosine Transform (DCT) allows us to move from:

*Spatial Domain→Frequency Domain*


### Spatial Domain vs Frequency Domain:

**Spatial Domain:**

An image is represented as:

𝑓
(
𝑥
,
𝑦
)

Each value represents pixel brightness.

**Frequency Domain:**

Instead of pixel values, we represent the image as:

𝐹
(
𝑢
,
𝑣
)

Each value represents the strength of a cosine wave (frequency component).

Low frequency:

- Smooth changes

- Large uniform areas

High frequency:

- Edges

- Fine details

- Noise

### Core Idea of DCT

DCT expresses a signal as a sum of cosine functions with different frequencies.

Think of it like this:

Any signal can be reconstructed by adding together multiple cosine waves of different amplitudes and frequencies.

This is similar to Fourier Transform, but:

- DCT uses only cosine terms

- Works well for real-valued signals


### Structure of DCT Coefficient Matrix

After applying DCT to an 8×8 block:

*Top-left = smooth information*

*Bottom-right = sharp details / noise*


### Energy Compaction Property

This is the most important property of DCT.

In natural images:

Most energy is concentrated in **low frequencies.**

High-frequency coefficients are often small or near zero.

This allows:

- High compression

- Minimal visible distortion

This is why JPEG uses DCT.


### JPEG Compression Using DCT

JPEG process:

- Convert image to YCbCr color space.

- Divide image into 8×8 blocks.

- Apply 2D DCT.

- Quantize coefficients (lossy step).

- Zigzag scan.

- Entropy encode.

Quantization reduces precision of high-frequency coefficients.

Result:

- Small file size

- Slight information loss


### DCT in Steganography

Instead of hiding data in pixel bits, we hide data in DCT coefficients.

Typical strategy:

- Avoid DC coefficient.

- Avoid very high frequencies.

- Modify mid-frequency coefficients slightly.

Example:
Change coefficient parity to embed bits.

This survives JPEG compression much better.

Algorithms using DCT:

- JSteg

- F5

- OutGuess

## JSteg (DCT-Based Steganography)

### Where JSteg Works

JSteg works inside the JPEG compression pipeline.

Recall JPEG steps:

- Split image into 8×8 blocks

- Apply DCT

- Quantize coefficients

- Store quantized coefficients

> JSteg embeds data into the LSB of quantized DCT coefficients(**NOT raw pixel values**)

### Which Coefficients Are Modified?

In each 8×8 block:

- Skip DC coefficient (top-left)

- Skip coefficients equal to 0

- Skip coefficients equal to 1 or -1 (to avoid distortion)

- Modify LSB of remaining coefficients

### Basic 2D DCT

``` python
import cv2
import numpy as np
from scipy.fftpack import dct, idct

# Load grayscale image
img = cv2.imread("input.jpg", 0)
img = np.float32(img)

# Apply 2D DCT
dct_img = dct(dct(img.T, norm='ortho').T, norm='ortho')

# Inverse DCT
reconstructed = idct(idct(dct_img.T, norm='ortho').T, norm='ortho')

# Convert back to uint8
reconstructed = np.uint8(np.clip(reconstructed, 0, 255))

cv2.imwrite("reconstructed.jpg", reconstructed)
```


### JSteg-Style Embedding Example

``` python
def embed_jsteg(dct_coeffs, message_bits):
    flat = dct_coeffs.flatten()
    bit_index = 0

    for i in range(len(flat)):
        if bit_index >= len(message_bits):
            break

        coeff = flat[i]

        # Skip DC and zeros
        if coeff == 0:
            continue

        if abs(coeff) == 1:
            continue

        # Modify LSB
        if (int(coeff) & 1) != int(message_bits[bit_index]):
            if coeff > 0:
                flat[i] -= 1
            else:
                flat[i] += 1

        bit_index += 1

    return flat.reshape(dct_coeffs.shape)
```

### Extraction (Simple Version)

``` python
def extract_jsteg(dct_coeffs, message_length):
    flat = dct_coeffs.flatten()
    bits = ""

    for coeff in flat:
        if coeff == 0:
            continue
        if abs(coeff) == 1:
            continue

        bits += str(int(coeff) & 1)

        if len(bits) >= message_length * 8:
            break

    return bits

```

## Fundamental Problem of JSteg

JSteg assumes:

*Small ±1 changes are invisible.*

True visually. ✅

False statistically. ❌

Modern steganalysis **doesn’t rely on human perception**.

It relies on:

- Higher-order statistics

- Machine learning classifiers

- Feature extraction (SPAM, SRM features)

- Deep CNN detectors

- Against those, JSteg fails easily.


## F5 (DCT-Based Steganography)


