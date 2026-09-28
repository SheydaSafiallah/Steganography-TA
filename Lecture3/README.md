# Lecture3: Steganalysis (Detecting Hidden Data)

## Table of Contents
1. [Introduction](#introduction)
2. [Categories of Steganalysis](#categories-of-steganalysis)
3. [Visual and Structural Attacks](#visual-and-structural-attacks)
4. [Chi-Square Attack](#chi-square-attack)
5. [RS (Regular-Singular) Analysis](#rs-regular-singular-analysis)
6. [Histogram-Based Attacks on DCT Steganography](#histogram-based-attacks-on-dct-steganography)
7. [Feature-Based Steganalysis: SPAM and SRM](#feature-based-steganalysis-spam-and-srm)
8. [Deep Learning Steganalysis (CNNs)](#deep-learning-steganalysis-cnns)
9. [Lecture Summary](#lecture-summary)
10. [Practice Questions](#practice-questions)

# Introduction

Lectures 1 and 2 were about **hiding** data — spatial-domain LSB and frequency-domain DCT embedding (JSteg, F5, OutGuess). Every one of those methods was eventually broken by a detector.

Steganalysis is the mirror discipline: given a file, decide whether it secretly carries a message, and ideally estimate how much and where.

Two ways to frame the problem:

- **Detection** — is this file stego or clean? (binary classification)
- **Extraction** — if stego, what is the payload? (much harder, often needs the key)

This lecture focuses on detection, since it is what breaks the algorithms from Lectures 1–2.

> The embedder's job is to disturb the cover as little as possible.
> The steganalyst's job is to notice *any* disturbance, however small.

# Categories of Steganalysis

| Category | Idea | Example |
|----------|------|---------|
| **Visual** | Look for artifacts a human can see | Enhanced LSB planes, color anomalies |
| **Structural** | Exploit a specific algorithm's known weakness | RS analysis, chi-square attack |
| **Statistical / first-order** | Compare histograms to expected natural statistics | Histogram attacks on JSteg |
| **Feature-based / higher-order** | Extract many numeric features, feed to a classifier | SPAM, SRM |
| **Deep learning** | Let a CNN learn the features itself | Xu-Net, Ye-Net, SRNet |

Structural and statistical attacks are **targeted** — they assume you know the embedding algorithm. Feature-based and deep-learning attacks are **universal (blind)** — they work without knowing which algorithm was used, which is why they eventually caught up to F5 and OutGuess.

# Visual and Structural Attacks

The crudest attack: extract and display the LSB plane of an image as a black-and-white bitmap.

- A clean image's LSB plane looks like random noise.
- A naively LSB-embedded image (Lecture 1, sequential, non-adaptive) often shows visible shapes, text outlines, or sharp region boundaries where the message stopped — because the message itself is far more structured than natural pixel noise.

```python
import cv2
import numpy as np

img = cv2.imread("suspect.png", 0)
lsb_plane = (img & 1) * 255
cv2.imwrite("lsb_plane.png", lsb_plane)
```

This is why Lecture 1 introduced **Randomized LSB** and **Adaptive LSB** — both exist specifically to defeat this kind of visual inspection by breaking up structure and avoiding smooth regions.

Visual inspection catches naive embedding but nothing more sophisticated. Everything below is quantitative.

# Chi-Square Attack

Targets **sequential LSB replacement** (basic LSB from Lecture 1, and JSteg from Lecture 2 — both *overwrite* the LSB rather than move toward zero).

### Why It Works

LSB replacement forces **Pairs of Values (PoVs)** to equalize:

- Values 2k and 2k+1 (e.g. 100 and 101) become interchangeable once you embed — a pixel with value 100 stays 100 or becomes 101, and vice versa, depending only on the message bit.
- If the message bits are roughly 50/50 ones and zeros (true for compressed/encrypted payloads), then after embedding, the counts of 2k and 2k+1 pull toward being **equal**.
- Natural images do *not* have equal counts for adjacent value pairs — histograms are smooth but rarely flat between neighbors.

### The Test

For each pair of values (2k, 2k+1), let:

- `h[2k]`, `h[2k+1]` = observed counts in the (suspect) image
- expected count under "fully embedded" hypothesis: `h_avg = (h[2k] + h[2k+1]) / 2` for both

Compute Pearson's chi-square statistic:

```
χ² = Σ (h[2k] − h_avg)² / h_avg   over all pairs k
```

A **low** χ² (observed ≈ expected/flattened) → strong evidence of full sequential LSB embedding.
A **high** χ² (histogram is naturally uneven) → likely clean, or embedding didn't reach that region.

Running the test over increasing prefixes of the image (first 10%, 20%, …) even estimates **how much of the image** was used — the statistic stays low up to the embedded region and jumps back to normal afterward.

```python
import numpy as np
from scipy.stats import chi2

def chi_square_attack(pixels, num_pairs=128):
    hist, _ = np.histogram(pixels.flatten(), bins=256, range=(0, 256))
    chi_sq = 0.0
    dof = 0

    for k in range(num_pairs):
        h0, h1 = hist[2 * k], hist[2 * k + 1]
        h_avg = (h0 + h1) / 2
        if h_avg == 0:
            continue
        chi_sq += ((h0 - h_avg) ** 2) / h_avg
        dof += 1

    # p-value close to 1 -> histogram matches the "flattened" stego model closely
    p_value = 1 - chi2.cdf(chi_sq, dof - 1)
    return chi_sq, p_value
```

> **Why F5 resists this:** F5 moves coefficients *toward zero* instead of overwriting the LSB, so 2k and 2k+1 don't pull toward equal counts — the chi-square statistic stays high (normal-looking), as noted in Lecture 2.
>
> **Why OutGuess resists this:** its correction phase explicitly repairs the first-order histogram after embedding, defeating this exact test by construction.

### Worked Example (By Hand)

Suppose a small image has only two value-pairs in its histogram:

| Value | Count |
|-------|-------|
| 100   | 40 |
| 101   | 10 |
| 102   | 30 |
| 103   | 32 |

**Pair (100, 101):** `h_avg = (40 + 10) / 2 = 25`

```
contribution = (40 - 25)² / 25 + (10 - 25)² / 25 = 225/25 + 225/25 = 9 + 9 = 18
```

**Pair (102, 103):** `h_avg = (30 + 32) / 2 = 31`

```
contribution = (30 - 31)² / 31 + (32 - 31)² / 31 = 1/31 + 1/31 ≈ 0.06
```

`χ² ≈ 18 + 0.06 ≈ 18.06` over 2 pairs — **high**, dominated by the (100, 101) pair, which is far from equalized. This looks like a **clean or lightly-embedded** region: a fully-embedded pair would show counts like 25/25, giving a contribution near 0, not 18.

If instead the histogram had been `100→25, 101→25, 102→31, 103→31` (i.e. every pair perfectly balanced), `χ² ≈ 0` — the textbook signature of full sequential LSB replacement.

# RS (Regular-Singular) Analysis

Targets sequential spatial-domain LSB (same family as the chi-square attack, but works even at low embedding rates where chi-square is weak).

### Core Idea

Partition the image into small groups of adjacent pixels (e.g. 4 pixels in a row). For each group, define a **discrimination function** `f` that measures local smoothness/noisiness, typically:

```
f(x1, x2, x3, x4) = |x1 - x2| + |x2 - x3| + |x3 - x4|
```

Define a **flipping function** `F1` that flips the LSB of every pixel in the group (0↔1, 2↔3, …), and `F(-1)` that does the reverse-direction flip.

Classify each group after applying the flip:

- **Regular (R)**: `f(F(group)) > f(group)` — flipping increased noisiness (typical of natural image structure)
- **Singular (S)**: `f(F(group)) < f(group)` — flipping decreased noisiness
- **Unusable (U)**: `f(F(group)) = f(group)`

For unmodified natural images, empirically: `R_M ≈ R_{-M}` and `S_M ≈ S_{-M}` (regular/singular counts for the positive and negative flip masks are close to each other).

### Why LSB Embedding Breaks the Symmetry

LSB replacement is a **non-invertible**, asymmetric operation on pixel values in a way that pulls `R_M` and `R_{-M}` apart as the embedding rate increases. RS analysis fits a quadratic curve to `R_M − S_M` vs. `R_{-M} − S_{-M}` across different embedding-rate assumptions and solves for the crossing point, which estimates the **actual embedding rate**, not just presence/absence.

RS analysis is more sensitive than chi-square at low payload rates precisely because it looks at *local pixel-pair relationships* rather than the global histogram.

### Simplified Python Sketch

```python
import numpy as np

def discrimination(group):
    return sum(abs(int(group[i]) - int(group[i + 1])) for i in range(len(group) - 1))

def flip_lsb(value):
    return value ^ 1  # 0<->1, 2<->3, 4<->5, ...

def classify_groups(pixels, group_size=4):
    R = S = U = 0
    for i in range(0, len(pixels) - group_size + 1, group_size):
        group = pixels[i:i + group_size]
        f_before = discrimination(group)
        flipped = [flip_lsb(int(p)) for p in group]
        f_after = discrimination(flipped)

        if f_after > f_before:
            R += 1
        elif f_after < f_before:
            S += 1
        else:
            U += 1
    return R, S, U

# ===== Example Usage ===== #
row = np.array([52, 53, 50, 49, 130, 131, 128, 127])  # flatten a row of pixels
R, S, U = classify_groups(row)
print(f"Regular={R}, Singular={S}, Unusable={U}")
```

> A full RS analysis also runs this with the `F(-1)` (negative) flipping mask and compares `R_M` vs `R_{-M}` across many groups, then fits the quadratic curve mentioned above to estimate embedding rate. This sketch only shows the per-group classification step.

# Histogram-Based Attacks on DCT Steganography

Lecture 2's algorithms leave different traces in the **DCT coefficient histogram**:

| Algorithm | Histogram signature | Detected by |
|-----------|---------------------|-------------|
| JSteg | Even/odd coefficient pairs equalize (classic PoV pattern) | Chi-square on DCT histogram |
| F5 | No pair equalization, but coefficient magnitudes are systematically shrunk toward zero (extra zeros/ones vs. expected) | Category attack (compares observed histogram to a model of the *undistorted* histogram, e.g. Fridrich's F5 detector) |
| OutGuess | First-order histogram is repaired | Blockiness/co-occurrence measures across 8×8 block boundaries (second-order statistics) |

The general lesson: **fixing one statistic (first-order histogram) doesn't fix all statistics.** This motivates moving beyond hand-picked, algorithm-specific tests to broad, general-purpose feature sets.

# Feature-Based Steganalysis: SPAM and SRM

Targeted attacks (chi-square, RS, category attacks) each assume a specific embedding algorithm. **Blind steganalysis** instead extracts a large, generic feature vector from every image and trains a classifier (commonly an SVM) to separate cover from stego, regardless of which algorithm was used.

### SPAM (Subtractive Pixel Adjacency Matrix)

1. Compute pixel differences along rows/columns/diagonals: `D_i = X_{i+1} - X_i`.
2. Model consecutive differences as a Markov chain: build a transition probability matrix `P(D_{i+1} = d2 | D_i = d1)`.
3. These transition probabilities are the feature vector (hundreds of dimensions).

Why it works: LSB and LSB-matching embedding subtly change the local correlation between neighboring pixels, even when they preserve the single-pixel histogram. SPAM captures exactly that second-order (pairwise) correlation — the thing LSB matching (Lecture 1's ±1 embedding) was specifically designed to survive against histogram-only attacks, but not against pairwise-correlation attacks.

```python
import numpy as np

def spam_features(image, T=3):
    """Simplified 1D horizontal SPAM-style feature: co-occurrence of
    consecutive pixel differences, clipped to [-T, T]."""
    diffs = np.diff(image.astype(int), axis=1)          # D_i = X_{i+1} - X_i
    diffs = np.clip(diffs, -T, T)

    size = 2 * T + 1
    transition = np.zeros((size, size))

    for row in diffs:
        for d1, d2 in zip(row[:-1], row[1:]):            # consecutive difference pairs
            transition[d1 + T, d2 + T] += 1

    transition /= transition.sum()                       # normalize to probabilities
    return transition.flatten()                           # feature vector, size (2T+1)^2
```

This one function only covers horizontal, first-order differences; the real SPAM feature set repeats this for vertical/diagonal directions and both signs, then concatenates everything into one long feature vector fed to a classifier.

### SRM (Spatial Rich Models)

SRM generalizes SPAM by computing **many different noise residuals** (dozens of high-pass filters/kernels, not just one first-difference), then building co-occurrence histograms for each residual.

- Union of many "weak" feature submodels → tens of thousands of features total.
- No single embedding algorithm can avoid disturbing *all* of these residual statistics simultaneously — some submodel almost always picks up the perturbation.
- Paired with an ensemble classifier (typically random forests), SRM was the state of the art for hand-crafted steganalysis features for years, and is effective against F5, OutGuess, and modern adaptive embedders (e.g. HUGO, WOW, S-UNIWARD).

# Deep Learning Steganalysis (CNNs)

SPAM/SRM require a human to *design* the residual filters. CNN-based steganalysis lets the network **learn** them.

### Key architectural ideas (Xu-Net / Ye-Net style)

1. **Fixed high-pass preprocessing layer** — the first layer is often initialized with (or fixed to) a known noise-residual filter (like SRM's kernels), because raw pixel values contain too much image *content* and too little of the tiny embedding *signal*. This suppresses the image itself and boosts the noise.
2. **No pooling early on** — aggressive pooling would destroy the very-low-amplitude embedding signal before deeper layers can use it.
3. **Global average pooling + small dense head** — steganalysis needs to detect a diffuse statistical pattern across the whole image, not localize an object, so architectures differ from typical vision CNNs.
4. **Trained on cover/stego pairs** — same cover image, embedded and not-embedded, so the network's gradient signal is purely about the embedding, not about image content differences.

### Why CNNs Beat SRM

- SRM's filters are hand-picked and fixed; a sufficiently different embedding scheme can slip between them.
- A CNN adapts its filters to the training distribution, including higher-order and cross-channel dependencies humans didn't think to encode by hand.
- In practice, modern CNN steganalyzers (SRNet and successors) detect F5, OutGuess, and even adaptive spatial-domain schemes at payload rates where SRM+ensemble classifiers start to fail.

### Trade-off

CNN steganalysis needs large labeled cover/stego datasets and is sensitive to **mismatch** — a detector trained on one cover-image source, embedding algorithm, or payload rate often degrades against a different one. This "cover source mismatch" problem is an active research area, and is the steganalysis-side analog of why F5 and OutGuess kept needing new defenses: no detector generalizes perfectly either.

# Lecture Summary

| Attack | Targets | Signal it exploits | Defeated by |
|--------|---------|---------------------|-------------|
| **Visual LSB-plane inspection** | Naive sequential LSB | Structure visible in LSB bitmap | Randomized/Adaptive LSB |
| **Chi-square attack** | Sequential LSB, JSteg | Pair-of-Values equalization | F5, OutGuess, LSB matching |
| **RS analysis** | Sequential spatial LSB | Regular/Singular group asymmetry | LSB matching, adaptive embedding |
| **DCT histogram / category attack** | JSteg, F5 | First-order coefficient distribution shift | OutGuess-style correction |
| **SPAM** | LSB matching, general spatial embedding | Pairwise pixel-difference correlation | Nothing fully — pushed field toward SRM |
| **SRM** | Broad range incl. F5, OutGuess, adaptive schemes | Many co-occurrence residual features | Cover-source mismatch, CNNs surpass it |
| **CNN steganalysis** | State of the art, most schemes above | Learned residual + statistical features | Adversarially-aware embedders, domain mismatch |

The overall arc across Lectures 1–3: every embedding trick (randomization, adaptivity, decrement-not-overwrite, histogram correction) defeats one specific class of detector, and every generation of steganalysis (structural → statistical → feature-based → deep learning) widens the net to catch the previous generation's blind spot. This detector/embedder arms race is the central theme of modern steganography research.

# Practice Questions

**1. A histogram pair (2k, 2k+1) has counts `h[2k] = 50` and `h[2k+1] = 50`. What does the chi-square attack conclude, and why?**

<details>
<summary>Answer</summary>

`h_avg = 50`, so the contribution to χ² for this pair is `(50-50)²/50 + (50-50)²/50 = 0`. A near-zero contribution across many pairs means the histogram matches the "flattened" pattern left by sequential LSB replacement — strong evidence of embedding via basic LSB or JSteg (not proof against F5/OutGuess, which don't leave this signature).
</details>

**2. Why is the chi-square attack ineffective against F5, even though F5 also modifies DCT coefficient LSBs?**

<details>
<summary>Answer</summary>

F5 always moves a mismatched coefficient *toward zero* rather than overwriting its LSB directly. This means values 2k and 2k+1 don't get pulled toward equal counts the way JSteg's overwrite does — the histogram keeps its natural, uneven shape, so χ² stays high (looks clean) even when the image is fully embedded.
</details>

**3. In RS analysis, what does it mean if, for a natural (unmodified) image, `R_M` and `R_{-M}` are nearly equal, but after LSB embedding they diverge?**

<details>
<summary>Answer</summary>

`R_M` and `R_{-M}` count how many pixel groups become "more regular" (noisier) under the positive-direction and negative-direction LSB flip, respectively. In natural images these are symmetric because there's no bias toward either flip direction. LSB replacement is a directional, non-invertible operation that breaks this symmetry — the bigger the payload, the further `R_M` and `R_{-M}` (and `S_M`/`S_{-M}`) pull apart, which is what lets RS analysis estimate the embedding *rate*, not just detect presence.
</details>

**4. Why can't SPAM or SRM be defeated the same way OutGuess defeats the chi-square attack (i.e. by "fixing" one statistic after embedding)?**

<details>
<summary>Answer</summary>

OutGuess only repairs the first-order (single-value) histogram. SPAM and SRM measure second-order and higher statistics — correlations *between* neighboring pixels/coefficients, across many different residual filters and directions. Fixing the single-value histogram doesn't restore these pairwise/co-occurrence relationships, so an embedder would need to separately correct dozens of different statistics simultaneously — which is essentially what later adaptive embedders (HUGO, WOW, S-UNIWARD) try to do by minimizing a broad distortion function instead of patching one test at a time.
</details>

**5. A CNN steganalyzer trained on JSteg-embedded images performs poorly when tested on F5-embedded images. Is this surprising, and what is this phenomenon called in general?**

<details>
<summary>Answer</summary>

Not surprising — it's a specific case of **cover-source / algorithm mismatch**. The CNN learned features tuned to JSteg's particular statistical fingerprint (LSB pair equalization); F5's fingerprint (decrement-toward-zero, shrinkage) is different enough that those learned features don't transfer well. This is why robust steganalysis systems are usually trained (or fine-tuned) on the same family of embedding algorithms, cover sources, and payload rates they'll be tested against.
</details>

**6. Rank the following from *least* to *most* general-purpose (i.e., works against the widest range of unknown embedding algorithms): chi-square attack, SRM, RS analysis.**

<details>
<summary>Answer</summary>

Chi-square attack and RS analysis are both **targeted**, assuming sequential LSB-style embedding — chi-square is the narrowest (specifically pair-equalization from LSB overwrite), RS is slightly more general (catches embedding at lower rates within the same LSB family). SRM is **blind/universal**, built from many generic statistical features and a trained classifier, so it works reasonably well against algorithms it wasn't explicitly designed for. Order: chi-square attack < RS analysis < SRM.
</details>
