# Lecture1: LSB (Least Significant Bit)


## Table of Contents
1. [Introduction](#introduction)
2. [Basic Concept](#basic-concept)
3. [How LSB Works Step-by-Step](#how-lsb-works-step-by-step)
4. [Variants of LSB Steganography](#variants-of-lsb-steganography)
5. [Lossless vs Lossy Images](#lossless-vs-lossy-images)
6. [Randomized LSB](#randomized-lsb)
7. [Adaptive LSB](#adaptive-lsb)
8. [LSB Matching (±1 Embedding)](#lsb-matching-±1-embedding)





# Introduction

Steganography is the practice of hiding secret information within a non-secret medium (image, audio, video, text) so that the presence of the message is concealed.

LSB (Least Significant Bit) steganography is one of the most widely used techniques in digital steganography. It hides information by modifying the least significant bit of the host medium’s data.

Why LSB?
*The least significant bits contribute very little to the overall value of a pixel or sample.
Changing them does not cause noticeable visual or auditory changes, making the hidden message almost invisible.*

# Basic Concept

Digital data (like images) is represented in binary.

For a 24-bit color image, each pixel has three color channels: Red, Green, Blue, each 8 bits.

Example of a pixel in binary (RGB):

- Red:   11001010
- Green: 10111001
- Blue:  11100101


The least significant bit (LSB) is the rightmost bit in each 8-bit channel.

LSB steganography modifies these bits to embed secret data:

Secret bit to hide: 1
- Original Red LSB:   0 → change to 1
- Original Green LSB: 1 → keep 1
- Original Blue LSB:  1 → keep 1


Resulting pixel still looks almost the same to the human eye.

# How LSB Works (Step-by-Step)
### Step 1: Prepare the Cover Medium

Commonly an image, audio, or video file.

Images are often used: BMP, PNG (lossless formats are better than JPEG).

### Step 2: Convert the Secret Message

Message → binary string (e.g., text “Hi” → ASCII → binary → 01001000 01101001).

### Step 3: Embed the Message

Take each bit of the message and replace the LSB of the pixel’s color channels.

For example: If the message is 0101, replace the LSB of the first 4 color channels with these bits.

### Step 4: Save the Stego-Medium

The new image now contains the hidden message.

Visual difference is usually imperceptible.

### Step 5: Extraction

To retrieve the secret message:

Read the LSB of each pixel/channel in the same order.

Combine the bits to reconstruct the original message.

**Example:**

- Cover Image Pixel (RGB):

    - Red:   10010110
    - Green: 11001101
    - Blue:  10110011


Message to hide: 101

- Embed 1 in Red LSB → 10010111

- Embed 0 in Green LSB → 11001100

- Embed 1 in Blue LSB → 10110011

Stego Pixel:

- Red:   10010111
- Green: 11001100
- Blue:  10110011


> Human eye sees almost no difference.

# Variants of LSB Steganography

| Variant | Description | Pros | Cons |
|---------|-------------|------|------|
| **LSB1 (1-bit)** | Uses only the least significant bit | Safe, minimal distortion | Limited capacity |
| **LSB2 / Multi-bit** | Uses 2+ least significant bits | Higher capacity | Risk of visible distortion |
| **Randomized LSB** | Uses a key and embeds bits in pseudo-random order | Harder to detect | Requires key for extraction |



# Lossless vs Lossy Images

### Lossless Image

A lossless image format stores data in a way that no information is lost during compression.

If you:

- Save the image

- Close it

- Reopen it

You get exactly the same pixel values — bit-for-bit identical.


**Examples:**
- PNG
- BMP
- TIFF (lossless mode)

***Why it matters for LSB:***

If you hide data in the least significant bits, those bits remain intact. So extraction works perfectly.

### Lossy Image

A lossy image format compresses the image by removing some information to reduce file size.

It does this by:

- Approximating colors

- Removing details the human eye is less sensitive to

- Modifying pixel values mathematically

When you save a lossy image:

- Some original pixel data is permanently changed.

- The exact binary values are not preserved.

**Examples:**

- JPEG (most common lossy format)
- WebP (lossy mode)

Why it’s a problem for LSB?
*LSB steganography depends on precise bit control!*

# Randomized LSB


In Randomized LSB, you Use a secret key!

1. Use that key to generate a pseudo-random sequence of pixel positions

2. Embed message bits only in those selected positions

>So without the key, extraction is almost impossible.

**Example:**


### Step 1 — Cover Image

Assume we have 8 grayscale pixels (each 8 bits):

***P1:*** 10110010

***P2***: 11001001

***P3***: 10011100

***P4***: 11100011

***P5***: 10101010

***P6***: 11010101

***P7***: 10010011

P***8***: 11111100

### Step 2 — Secret Message

***Message***: "A"

***ASCII of A*** = 65

***Binary*** = 01000001

So we need to embed:

**0 1 0 0 0 0 0 1**

### Step 3 — Secret Key

***Key*** = "KEY123"

We feed this key into a pseudo-random generator (PRNG).

The PRNG gives us this pixel order:

[5, 2, 8, 1, 7, 3, 6, 4]


This means:

- First bit → Pixel 5
- Second bit → Pixel 2
- Third bit → Pixel 8 etc.

>This order is not sequential.

### Step 4 — Embedding

Now we replace LSB of those pixels in that order.

### Extraction Process


1.  same key "KEY123"

2. Generate same pseudo-random order

3. Read LSB from pixels in that order

4. Reconstruct binary

5. Convert back to ASCII

>If the wrong key is used → wrong pixel order → garbage message.

### Why Randomized LSB is Stronger

Sequential LSB is vulnerable to:

- Statistical analysis
- Chi-square attack
- RS steganalysis

Randomized LSB:

- Breaks predictable embedding patterns

- Distributes changes across image

- Reduces statistical anomalies

> Still not bulletproof — but significantly harder to detect.

### simple PRNG implementation:

Linear Congruential Generator formula:

### *Xₙ₊₁ = (aXₙ + c) mod m*

> **Important Concept:** 
These numbers are not random.
They are carefully chosen mathematical parameters that control:
**Period length**,
**Distribution**,
**Predictability**



```python

class LCG:
    def __init__(self, seed):
        self.m = 2**31
        self.a = 1103515245
        self.c = 12345
        self.state = seed

    def next(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def randrange(self, max_value):
        return self.next() % max_value


def key_to_seed(key):
    return sum(ord(char) for char in key)


def generate_shuffled_positions(total_pixels, key):
    seed = key_to_seed(key)
    prng = LCG(seed)

    positions = list(range(total_pixels))

    for i in range(total_pixels - 1, 0, -1):
        j = prng.randrange(i + 1)
        positions[i], positions[j] = positions[j], positions[i]

    return positions


# ===== Example Usage ===== #

NUMBER_OF_PIXELS = 20
key = "KEY123"

positions = generate_shuffled_positions(NUMBER_OF_PIXELS, key)

print(positions)

```

Basic LSB is easy to detect because:

- It modifies pixels uniformly

- It disturbs statistical properties

- It increases noise in smooth regions


To make LSB harder to detect, we use *Adaptive LSB*.

## Adaptive LSB


Instead of embedding bits uniformly across the whole image,
we embed them only in regions where modifications are harder to detect.

Typically:

- Edges
- Textured areas
- Noisy regions

Avoid:

- Smooth areas
- Flat backgrounds
- Large uniform colors

Because human vision and statistical detectors are very sensitive there.


### Adaptive LSB Strategy

There are several levels of sophistication.

### 1. Edge-Based Adaptive LSB (Most Common)

Idea:

***Embed only in high-gradient areas.***

Steps:

1. Compute edge map (Sobel, Canny, Laplacian)
2. Select pixels where gradient magnitude > threshold
3. Embed only in those pixels

Why it works:

- Edge pixels already have high variation
- Small LSB changes are statistically masked
- Harder to distinguish from natural noise

### 2. Texture-Based Adaptive LSB

Instead of edges, measure:

- Local variance

- Local standard deviation

- Entropy

Embed in regions with high local variance.

***Smooth region example:***

120, 120, 121, 120


***Textured region example:***

45, 200, 13, 178


>Textured regions hide changes better.


### 3. LSB Matching (±1 Embedding)

Instead of forcing LSB directly, it does this:

| Condition                  | Action                                                                  |
|----------------------------|------------------------------------------------------------------------ |
| LSB already equals bit     | Do nothing                                                              |
| LSB does not equal bit     | Randomly either: **Add 1** or **Subtract 1 (while keeping pixel in range 0–255)**|
                      


***Example:***

**Original pixel:** 100

**Binary:** 01100100

**LSB =** 0

*We want to embed 1*

Instead of forcing 101, we randomly choose:

- 100 + 1 = 101

OR

- 100 − 1 = 99

So result could be:

- 99 (01100011)
or
- 101 (01100101)

> **Important:**  Now the modification is not always within even/odd pairs.

*Why This Is Stronger?*

In basic LSB:

- If pixel is even and you embed 1 → it becomes odd.

- If pixel is odd and you embed 0 → it becomes even.

So **even/odd distributions equalize.**

In LSB Matching:

- Pixel may move to neighboring intensity outside its direct pair.

- Distribution distortion spreads across histogram.

Instead of:

100 ↔ 101

You now have:

100 → 99 or 101

*That spreads distortion.*

Steganalysis becomes harder because:

- No forced pair equalization
- Histogram shifts more naturally
- RS analysis becomes less effective

```python

import random

def lsb_match(pixel, bit):
    lsb = pixel & 1

    if lsb == bit:
        return pixel  # no change

    # mismatch → add or subtract randomly
    if pixel == 0:
        return 1
    elif pixel == 255:
        return 254
    else:
        return pixel + random.choice([-1, 1])

```