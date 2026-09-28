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


F5 was designed to fix the exact weakness that kills JSteg: the statistical fingerprint left in the DCT histogram. It introduces two key ideas — **matrix encoding** and **subtraction instead of LSB replacement**.

### Why JSteg Fails (Recap)

JSteg overwrites the LSB of a coefficient. That forces even/odd pairs to equalize, producing a tell-tale flattening in the coefficient histogram. Chi-square attacks detect this instantly.

F5 avoids this in two ways.

### Idea 1: Decrement, Don't Overwrite

Instead of *setting* the LSB, F5 changes the LSB by **decreasing the absolute value** of the coefficient toward zero when a change is needed.

| Coefficient | Want to embed | JSteg action | F5 action |
|-------------|---------------|--------------|-----------|
| +5 (LSB=1)  | 0             | force to +4  | subtract 1 → +4 |
| −5 (LSB=1)  | 0             | force to −4  | add 1 → −4 |

Rules:

- Skip the DC coefficient.
- Skip coefficients equal to 0.
- The LSB of a coefficient carries the message bit, where the "bit" of a coefficient is `|coeff| mod 2`.
- If the bit already matches, do nothing.
- If it does not match, move the coefficient one step **toward zero** (positive → −1, negative → +1).

### Idea 2: Shrinkage

When a coefficient with value ±1 is decremented, it becomes 0. A 0 is skipped on extraction, so that bit is *lost*. This event is called **shrinkage**. F5 handles it by **re-embedding** the same bit into the next usable coefficient. This is why F5's histogram does not equalize the way JSteg's does — the change is directional (toward zero), matching the natural shape of the DCT histogram.

### Idea 3: Matrix Encoding

This is F5's efficiency trick. Instead of changing one coefficient per bit, matrix encoding lets you embed *k* bits by changing **at most one** coefficient out of a group of `2^k − 1`.

Example with `k = 2` (group of 3 coefficients):

- You want to embed 2 bits.
- You compute a hash of the current LSBs of the 3 coefficients.
- With high probability you only need to flip **one** coefficient (or none) to make the hash equal your 2 message bits.

Fewer changes → less distortion → far harder to detect. The notation is written as (1, n, k): change at most **1** bit among **n = 2^k − 1** coefficients to embed **k** bits.

### Matrix Encoding — Worked Example (1, 3, 2)

Say three coefficient LSBs are `x1=1, x2=0, x3=1` and you want to embed message bits `m1=1, m2=0`.

Compute:

```
s1 = x1 XOR x3
s2 = x2 XOR x3
```

So `s1 = 1 XOR 1 = 0`, `s2 = 0 XOR 1 = 1`.

Compare to the message `(m1, m2) = (1, 0)`:

```
d1 = s1 XOR m1 = 0 XOR 1 = 1
d2 = s2 XOR m2 = 1 XOR 0 = 1
```

The pair `(d1, d2) = (1, 1)` tells you **which single coefficient to change** (here, position 3). Flip that one coefficient's LSB and both message bits are now recoverable. One change encoded two bits.

### F5-Style Embedding (Simplified)

```python
def embed_f5(dct_coeffs, message_bits):
    flat = dct_coeffs.flatten()
    bit_index = 0

    for i in range(len(flat)):
        if bit_index >= len(message_bits):
            break

        coeff = int(flat[i])

        # Skip DC (handled outside) and zeros
        if coeff == 0:
            continue

        target_bit = int(message_bits[bit_index])
        current_bit = abs(coeff) & 1

        if current_bit == target_bit:
            bit_index += 1          # already correct
            continue

        # Move TOWARD zero
        if coeff > 0:
            coeff -= 1
        else:
            coeff += 1

        # Shrinkage: became 0 -> bit is lost, re-embed later
        if coeff == 0:
            flat[i] = coeff
            continue                # do NOT advance bit_index

        flat[i] = coeff
        bit_index += 1

    return flat.reshape(dct_coeffs.shape)
```

### F5 Extraction (Simplified)

```python
def extract_f5(dct_coeffs, message_length):
    flat = dct_coeffs.flatten()
    bits = ""

    for coeff in flat:
        coeff = int(coeff)
        if coeff == 0:              # skip zeros (shrinkage-safe)
            continue

        bits += str(abs(coeff) & 1)

        if len(bits) >= message_length * 8:
            break

    return bits
```

### F5 vs JSteg Summary

| Property | JSteg | F5 |
|----------|-------|----|
| Change type | LSB overwrite | decrement toward zero |
| Histogram effect | equalizes pairs (detectable) | preserves shape |
| Efficiency | 1 change per bit | matrix encoding (≪ 1 change per bit) |
| Chi-square attack | fails | resists |

F5 is much stronger than JSteg, but modern ML-based steganalysis (SRM features, deep CNNs) can still detect it. It is a milestone, not a final answer.

## OutGuess (DCT-Based Steganography)

OutGuess takes a different route to defeating statistical detection: **histogram preservation**.

### Core Idea

OutGuess embeds in two phases:

1. **Embedding phase** — hide the message in the LSBs of selected DCT coefficients (skipping 0 and 1, like JSteg), chosen pseudo-randomly using a key.
2. **Correction phase** — deliberately modify *other, unused* coefficients so that the **overall coefficient histogram matches the original** as closely as possible.

The insight: JSteg is caught because embedding changes the histogram. If you *repair* the histogram afterward, the chi-square attack sees a normal-looking distribution.

### Why the Correction Step Matters

- Embedding might increase the count of some values and decrease others.
- The correction phase swaps a matching number of *unused* coefficients in the opposite direction.
- Net effect: the first-order histogram is (approximately) restored.

### Trade-off

Preserving the histogram costs capacity — roughly half the usable coefficients are reserved for corrections rather than data. So OutGuess hides **less** than JSteg for the same image, in exchange for resisting first-order statistical attacks.

### OutGuess Limitation

OutGuess preserves the *first-order* histogram but not higher-order statistics (relationships between neighboring blocks/coefficients). Later steganalysis exploits exactly those higher-order dependencies, so OutGuess — like JSteg and F5 — is detectable by modern methods.
