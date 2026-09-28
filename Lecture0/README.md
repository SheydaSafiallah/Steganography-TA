# Lecture0: Prerequisites

This lecture is a toolbox, not a story. It collects everything Lectures 1–3 assume you already know: binary numbers, bitwise operations, how digital images are represented, enough Python/Pillow to manipulate them, and the handful of statistics ideas (histogram, mean, variance) that steganalysis is built on.

If you're already comfortable with binary and basic image processing, skim the headers and jump straight to the practice questions to check yourself. If any of this is new, read it in order — later lectures build directly on it.

## Table of Contents
1. [Number Systems: Binary, Decimal, Hex](#number-systems-binary-decimal-hex)
2. [Bitwise Operations](#bitwise-operations)
3. [Text as Binary (ASCII)](#text-as-binary-ascii)
4. [Digital Images 101](#digital-images-101)
5. [Python + Pillow Quickstart](#python--pillow-quickstart)
6. [Statistics You'll Need](#statistics-youll-need)
7. [Practice Questions](#practice-questions)

# Number Systems: Binary, Decimal, Hex

Computers store everything as **bits** — digits that are either `0` or `1`. Steganography constantly asks: "what is the last bit of this number, and can I change it?" — so you need to read binary as comfortably as decimal.

### Binary → Decimal

Each bit position is a power of 2, counted from the right, starting at 0:

```
Binary:    1   1   0   0   1   0   1   0
Position:  7   6   5   4   3   2   1   0
Value:   128  64  32  16   8   4   2   1
```

To convert, sum the powers of 2 where the bit is `1`:

```
11001010 = 128 + 64 + 0 + 0 + 8 + 0 + 2 + 0 = 202
```

### Decimal → Binary

Repeatedly divide by 2 and record the remainders (bottom to top), or subtract the largest power of 2 that fits:

```
202 → 202 - 128 = 74
       74 - 64  = 10
       10 - 8   = 2
        2 - 2   = 0
→ bits set at 128, 64, 8, 2 → 11001010
```

### Why 8 Bits (1 Byte)?

A single color channel of a pixel (e.g. Red) is stored in **1 byte = 8 bits**, giving values from `00000000` (0) to `11111111` (255) — exactly the 0–255 range you'll see constantly in Lectures 1–3.

### Hexadecimal (a quick note)

Hex (base 16, digits `0-9A-F`) is a compact way to write binary — each hex digit represents exactly 4 bits. You'll mostly see decimal (0–255) in this course, but color values are often written in hex in image tools (e.g. `#CA` = `202` = `11001010`). Two hex digits = 1 byte, which is why web colors look like `#FF0000` (3 bytes: R, G, B).

# Bitwise Operations

These operations work directly on individual bits and are the entire mechanical basis of LSB steganography (Lecture 1) and DCT-coefficient steganography (Lecture 2).

| Operation | Symbol (Python) | Rule | Used for |
|-----------|:---:|------|----------|
| AND | `&` | 1 only if both bits are 1 | Reading/masking a bit |
| OR | `\|` | 1 if either bit is 1 | Setting a bit to 1 |
| XOR | `^` | 1 if bits differ | Flipping a bit, comparing bits |
| NOT | `~` | Flips every bit | Clearing a bit (combined with AND) |
| Left shift | `<<` | Shifts bits left, fills with 0 | Multiplying by powers of 2 |
| Right shift | `>>` | Shifts bits right | Dividing by powers of 2 |

### The Three Operations Every Steganography Algorithm Uses

**1. Reading the LSB — `value & 1`**

```
202 = 11001010
  1 = 00000001
  & = 00000000  → 0   (202's last bit is 0)
```

```python
>>> 202 & 1
0
>>> 203 & 1
1
```

**2. Clearing the LSB, then setting it — `(value & ~1) | bit`**

This is exactly the pattern used in Lecture 1's embedding code.

```
value & ~1   → clears the last bit to 0, keeps everything else
result | bit → sets the last bit to whatever you want (0 or 1)
```

```python
>>> pixel = 202          # 11001010
>>> pixel & ~1           # 11001010 -> clears LSB -> 11001010 (already 0, unchanged: 202)
202
>>> pixel = 203          # 11001011
>>> (pixel & ~1) | 1     # clear then set to 1 -> 11001011 -> 203 (unchanged, already 1)
203
>>> (pixel & ~1) | 0     # clear then force to 0 -> 11001010 -> 202
202
```

**3. Flipping a bit — `value ^ 1`**

```python
>>> 202 ^ 1   # 11001010 XOR 00000001 = 11001011
203
>>> 203 ^ 1   # flip again -> back to 202
202
```

You'll see `& 1` for reading, `(x & ~1) | bit` for writing, and `^ 1` for flipping throughout Lectures 1–3 — memorizing these three lines now will make every later code sample self-explanatory.

# Text as Binary (ASCII)

Steganography usually hides *text messages*, so you need to convert text to bits before embedding.

**ASCII** assigns every common character a number from 0–127 (extended ASCII goes to 255). Each character is stored as 1 byte (8 bits).

| Character | Decimal | Binary |
|-----------|:-------:|--------|
| `H` | 72 | 01001000 |
| `i` | 105 | 01101001 |
| `!` | 33 | 00100001 |
| `0` | 48 | 00110000 |
| `A` | 65 | 01000001 |
| `a` | 97 | 01100001 |

So the string `"Hi"` becomes the bitstream `01001000 01101001` — this is the exact example used in Lecture 1.

```python
>>> ord('H')          # character -> decimal
72
>>> format(72, '08b')  # decimal -> 8-bit binary string
'01001000'
>>> chr(72)            # decimal -> character
'H'
>>> int('01001000', 2) # binary string -> decimal
72
```

Chaining these four functions is exactly how the `text_to_bits` / `bits_to_text` helpers in Lecture 1's embed/extract code work.

# Digital Images 101

### Pixels and Channels

A digital image is a grid of **pixels**. Each pixel typically stores color as three numbers — Red, Green, Blue (**RGB**) — each an 8-bit value from 0–255.

```
A single pixel:  (202, 185, 101)  ->  R=202, G=185, B=101
```

- A **grayscale** image has only 1 channel per pixel (just brightness, 0–255).
- An RGB image has 3 channels per pixel. Some formats add a 4th (Alpha, transparency) → RGBA.

### Resolution and Total Data

An image's **resolution** (e.g. 1920×1080) tells you width × height in pixels.

```
total values in an RGB image = width x height x 3
```

A 1920×1080 RGB image has `1920 × 1080 × 3 = 6,220,800` individual 8-bit numbers — this is exactly the number Lecture 1's capacity formula starts from.

### Bit Depth

**Bit depth** = bits per channel. Almost everything in this course assumes **8-bit depth** (0–255 per channel), which is the overwhelming standard for consumer images (PNG, BMP, standard JPEG).

### Color vs. Coordinates

Pixels are addressed by `(x, y)` coordinates, with `(0, 0)` conventionally at the **top-left** corner. `x` increases rightward, `y` increases downward (opposite of typical math-class graphs — a common source of bugs).

# Python + Pillow Quickstart

Lectures 1–3 use **Pillow** (`PIL`) for image I/O and **NumPy** for numeric arrays. Install both:

```bash
pip install pillow numpy scipy
```

### Opening, Inspecting, and Saving an Image

```python
from PIL import Image

img = Image.open("photo.png").convert("RGB")  # force 3-channel RGB
print(img.size)        # (width, height), e.g. (1920, 1080)
print(img.mode)        # 'RGB'

pixels = img.load()    # gives fast (x, y) -> (r, g, b) access
r, g, b = pixels[0, 0] # top-left pixel
print(r, g, b)

pixels[0, 0] = (r, g, 0)  # set Blue channel of top-left pixel to 0
img.save("edited.png")    # PNG is lossless -- see Lecture 1
```

### Looping Over Every Pixel

This nested-loop pattern is exactly what Lecture 1's embed/extract functions use:

```python
for y in range(img.height):
    for x in range(img.width):
        r, g, b = pixels[x, y]
        # ... read or modify r, g, b here ...
```

### NumPy Arrays (used in Lectures 2 & 3)

Pillow images convert easily to NumPy arrays, which support fast whole-array math (needed for DCT and histograms):

```python
import numpy as np

arr = np.array(img)         # shape: (height, width, 3)
print(arr.shape)            # e.g. (1080, 1920, 3)
print(arr[0, 0])            # top-left pixel, as [R, G, B]

gray = np.array(img.convert("L"))  # single-channel grayscale, shape (height, width)
```

# Statistics You'll Need

Lecture 3 (Steganalysis) leans on a few statistics ideas. You don't need a full stats course — just these:

### Histogram

A **histogram** counts how many times each value (0–255) appears in the image.

```python
import numpy as np

hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
# hist[k] = number of pixels with value k
```

A natural photo's histogram is a smooth, bumpy curve — not flat, not perfectly symmetric. Steganalysis attacks (Lecture 3) work by noticing when embedding makes parts of this curve unnaturally *flat* or *shifted*.

### Mean and Variance

- **Mean** (average) — the typical/center value of a set of numbers: `sum(values) / count(values)`.
- **Variance** — how spread out the values are around the mean. High variance = noisy/textured region; low variance = smooth region.

```python
patch = gray[0:4, 0:4]           # a small 4x4 block of pixels
print(patch.mean())              # average brightness
print(patch.var())               # how "flat" (low) vs "textured" (high) the patch is
```

This is exactly the intuition behind **Adaptive LSB** (Lecture 1) and the discrimination function in **RS analysis** (Lecture 3): high-variance regions hide changes better than low-variance ones.

### What a Chi-Square Test Is Actually Asking

You do not need the formal statistical theory — just this intuition, which Lecture 3 builds on directly:

> "I have some **observed** counts, and a hypothesis about what the **expected** counts should be. Chi-square measures how far apart observed and expected are, in a way that's sensitive to relative size (being off by 10 matters more when the expected count is 20 than when it's 2000)."

```
chi_square_contribution = (observed - expected)² / expected
```

Small chi-square → observed data matches the hypothesis well.
Large chi-square → observed data does *not* match the hypothesis.

Lecture 3 uses this to test the hypothesis "this histogram looks like it went through sequential LSB embedding."

# Practice Questions

**1. Convert `11010011` to decimal.**

<details>
<summary>Answer</summary>

`128 + 64 + 0 + 16 + 0 + 0 + 2 + 1 = 211`
</details>

**2. Convert `77` to an 8-bit binary string.**

<details>
<summary>Answer</summary>

`77 = 64 + 8 + 4 + 1 → 01001101`
</details>

**3. What does `pixel = pixel & ~1` do to a pixel value, in plain English? What does `pixel = pixel | 1` do?**

<details>
<summary>Answer</summary>

`pixel & ~1` clears (forces to 0) the least significant bit, rounding the value down to the nearest even number (e.g. 203 → 202, 202 stays 202). `pixel | 1` sets the LSB to 1, rounding up to the nearest odd number (e.g. 202 → 203, 203 stays 203).
</details>

**4. A 640×480 grayscale image — how many individual 8-bit values does it contain? How does that change if it's RGB instead?**

<details>
<summary>Answer</summary>

Grayscale: `640 × 480 × 1 = 307,200` values. RGB: `640 × 480 × 3 = 921,600` values — three times as many, since each pixel has 3 channels instead of 1.
</details>

**5. What is the ASCII binary encoding of the character `'0'` (digit zero, not the number 0)? Why might a beginner confuse the two?**

<details>
<summary>Answer</summary>

The **character** `'0'` has ASCII decimal value 48, so its binary is `00110000`. It's easy to confuse with the **number** `0` (binary `00000000`) because they look the same when printed — but `ord('0')` is 48, not 0. This distinction matters constantly when converting messages to bits, since you must convert the *character*, not assume its ASCII code equals its printed digit.
</details>

**6. A 4x4 pixel patch has very low variance. Should an Adaptive LSB embedder (Lecture 1) prefer to hide data there, or avoid it? Why?**

<details>
<summary>Answer</summary>

Avoid it. Low variance means the region is smooth/flat, so any pixel change (even a 1-bit LSB flip) is more statistically and visually noticeable against the uniform background. Adaptive LSB specifically targets high-variance (textured/edge) regions, where small changes blend into existing natural noise.
</details>

**7. Two histogram bins have `observed = 48` and `expected = 50`. Compute the chi-square contribution for this bin.**

<details>
<summary>Answer</summary>

`(48 - 50)² / 50 = 4 / 50 = 0.08` — a small contribution, meaning this bin closely matches the hypothesis.
</details>
