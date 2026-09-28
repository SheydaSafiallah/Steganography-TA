# Exam Prep: Final Exam Study Guide

This file has two parts:

1. **Question Bank by Topic** — more questions per topic than a real exam would have, each with its answer directly below it. Use this for targeted review, topic by topic.
2. **Mock Final Exam** — one timed, exam-style paper pulling from all four lectures, in the mixed-format style (multiple choice, short answer, calculation, code tracing, essay) common in university steganography/security courses. Answer key is at the very end — don't peek before attempting it.

Covers: [Lecture0](../Lecture0/README.md) (prerequisites), [Lecture1](../Lecture1/README.md) (LSB), [Lecture2](../Lecture2/README.md) (DCT: JSteg/F5/OutGuess), [Lecture3](../Lecture3/README.md) (steganalysis).

## Table of Contents
1. [Question Bank: Lecture 0 (Prerequisites)](#question-bank-lecture-0-prerequisites)
2. [Question Bank: Lecture 1 (LSB)](#question-bank-lecture-1-lsb)
3. [Question Bank: Lecture 2 (DCT)](#question-bank-lecture-2-dct)
4. [Question Bank: Lecture 3 (Steganalysis)](#question-bank-lecture-3-steganalysis)
5. [Question Bank: Cross-Topic / Integrative](#question-bank-cross-topic--integrative)
6. [Mock Final Exam](#mock-final-exam)
7. [Mock Final Exam — Answer Key](#mock-final-exam--answer-key)

---

# Question Bank: Lecture 0 (Prerequisites)

**Q1.** Convert `10110101` to decimal.

*Answer:* `128 + 32 + 16 + 4 + 1 = 181`

**Q2.** What is the result of `(150 & ~1) | 1`?

*Answer:* `150` is `10010110` (even, LSB=0). `& ~1` clears the LSB (no change here, stays 150), then `| 1` sets it to 1 → `10010111` = `151`.

**Q3.** True or False: `value ^ 1` always increases `value` by 1.

*Answer:* False. XOR with 1 flips the LSB — it adds 1 if the LSB was 0 (even → odd), but *subtracts* 1 if the LSB was 1 (odd → even). E.g. `203 ^ 1 = 202`.

**Q4.** A 1024×768 RGB image — how many bytes of raw pixel data does it contain?

*Answer:* `1024 × 768 × 3 = 2,359,296` bytes (≈ 2.25 MB uncompressed).

**Q5.** Why is `img.load()` followed by `pixels[x, y]` in Pillow, rather than simply `img.getpixel((x, y))`, generally preferred when modifying every pixel in a loop?

*Answer:* `.load()` returns a pixel-access object optimized for repeated random access, making per-pixel reads/writes in a loop significantly faster than calling `getpixel`/`putpixel` (which each carry more per-call overhead) thousands or millions of times.

**Q6.** A 4×4 image patch has pixel values `[10, 200, 15, 190]` in a row. Is this patch more likely "smooth" or "textured," and what statistic would you compute to confirm it?

*Answer:* Textured (high local variance) — the values alternate between very low and very high. Computing the **variance** (or standard deviation) of the patch confirms it: a high variance value quantifies this "jumpiness."

---

# Question Bank: Lecture 1 (LSB)

**Q1.** A pixel's Green channel is `01011010`. Embed the bit `0`. What's the resulting value?

*Answer:* LSB is already `0`, so no change: `01011010` = 90.

**Q2.** What is the maximum theoretical payload (in bytes) for a 2048×1536 grayscale image using 1-bit LSB?

*Answer:* `2048 × 1536 × 1 = 3,145,728 bits = 393,216 bytes` (≈ 384 KB).

**Q3.** Explain in one or two sentences why Randomized LSB requires the *same key* for both embedding and extraction.

*Answer:* The key seeds a pseudo-random number generator (PRNG) that determines the *order* in which pixel positions are used. Without the identical key, the receiver's PRNG produces a different sequence, so it reads bits from the wrong positions and reconstructs garbage instead of the message.

**Q4.** In Adaptive LSB, why are edge/textured regions preferred over smooth regions for embedding?

*Answer:* Smooth regions have low natural variance, so any change (even a 1-bit flip) stands out both visually and statistically. Edge/textured regions already have high natural pixel variation, so small changes are "masked" — statistically and visually harder to distinguish from natural noise.

**Q5.** In LSB Matching (±1 embedding), a pixel has value `255` and its LSB doesn't match the bit to embed. What must happen, and why can't the usual "randomly ±1" rule apply here?

*Answer:* The pixel must move to `254` (subtract 1). It can't go to `256` because pixel values are capped at `255` (out of the valid 8-bit range), so the random-direction choice is forced to the only valid option.

**Q6.** Why does basic sequential LSB replacement cause pairs of values like (100, 101) to become statistically equalized, but LSB Matching does not?

*Answer:* LSB replacement always forces value 100 to become 100 or 101 depending purely on the bit — nothing else changes. This creates a hard boundary between only two neighboring values. LSB Matching, when there's a mismatch, can move the pixel to *either* neighbor (±1) at random, so changes aren't confined to one fixed even/odd pair — the distortion spreads more naturally across the histogram.

**Q7.** You're given a cover image and a message of 500,000 bits. The cover image is 800×600 RGB. Is there enough capacity for basic sequential 1-bit LSB embedding? Show your work.

*Answer:* Capacity = `800 × 600 × 3 = 1,440,000` bits. Since `500,000 < 1,440,000`, yes, there is enough capacity (with plenty of room to spare — using only ~35% of capacity).

**Q8.** Name the *variant* of LSB steganography that would be least resistant to a naive visual inspection of the LSB bit-plane, and explain why.

*Answer:* Basic/sequential LSB (LSB1), because it embeds bits in a fixed, predictable order across the whole image without regard to local image content — the message's structure (much more regular than natural pixel noise) tends to show up as visible patterns/shapes in the LSB plane.

---

# Question Bank: Lecture 2 (DCT)

**Q1.** Why is DCT preferred over raw pixel manipulation for steganography that needs to survive JPEG compression?

*Answer:* JPEG compression itself operates in the DCT domain — it quantizes DCT coefficients as its lossy step. Embedding directly in the *same* quantized DCT coefficients JPEG already works with means the hidden data participates in (rather than gets destroyed by) the compression pipeline, unlike raw pixel LSBs which JPEG's compression overwrites.

**Q2.** What does "energy compaction" mean, and why does it matter for JPEG compression?

*Answer:* Energy compaction is DCT's property of concentrating most of an image block's information (energy) into a few low-frequency coefficients (top-left of the coefficient matrix), leaving most high-frequency coefficients small or zero. This lets JPEG discard/quantize the many near-zero high-frequency coefficients aggressively with minimal visible quality loss, which is the basis of JPEG's compression.

**Q3.** JSteg skips DC coefficients, zero coefficients, and coefficients equal to ±1. Explain the reasoning for each skip rule.

*Answer:* DC is skipped because it holds a large share of block energy (average brightness) — changing it causes a visible, block-wide shift. Zero coefficients are skipped because embedding there is undefined/ambiguous for the ±1-avoidance scheme and zero-counts are a known steganalysis signal. Coefficients at ±1 are skipped because moving them toward "correcting" the LSB would turn them into 0, artificially inflating the zero-coefficient count — a statistically detectable anomaly.

**Q4.** A DCT coefficient is `-7` (binary magnitude `111`, LSB=1). F5 needs to embed a `1`. What happens?

*Answer:* `|−7| & 1 = 1`, which already matches the target bit `1`. No change is made — F5 only modifies a coefficient when the current bit does *not* match the target.

**Q5.** Explain "shrinkage" in F5 and why it requires re-embedding.

*Answer:* Shrinkage happens when a coefficient at ±1 is decremented toward zero and becomes exactly 0. Since zero coefficients are always skipped during extraction, the bit that was supposed to be encoded there is lost. F5 handles this by *not* advancing to the next message bit when shrinkage occurs — it retries embedding that same bit in the next available coefficient.

**Q6.** In (1, 3, 2) matrix encoding, three coefficient LSBs are `x1=0, x2=1, x3=0`, and the message bits to embed are `(m1, m2) = (0, 1)`. Which coefficient (if any) needs to flip?

*Answer:* `s1 = x1 XOR x3 = 0 XOR 0 = 0`. `s2 = x2 XOR x3 = 1 XOR 0 = 1`. `d1 = s1 XOR m1 = 0 XOR 0 = 0`. `d2 = s2 XOR m2 = 1 XOR 1 = 0`. `(d1, d2) = (0, 0)` means **no coefficient needs to change** — the current LSBs already encode the desired message bits.

**Q7.** Why does OutGuess have lower embedding capacity than JSteg for the same cover image?

*Answer:* OutGuess reserves roughly half of its usable (non-zero, non-±1) coefficients for the correction phase, which restores the first-order histogram after embedding. Only the remaining half actually carries message data, cutting effective capacity roughly in half compared to JSteg, which uses (nearly) all usable coefficients for data.

**Q8.** Rank JSteg, F5, and OutGuess from *weakest* to *strongest* resistance against a basic chi-square attack, and justify the order in one sentence each.

*Answer:* **JSteg** (weakest) — LSB overwrite directly equalizes value pairs, the exact signature chi-square detects. **F5** — decrement-toward-zero avoids pair equalization, so chi-square sees a near-normal histogram. **OutGuess** (strongest against this specific attack) — actively repairs the first-order histogram in a correction phase, defeating chi-square by construction (though it remains vulnerable to higher-order attacks).

---

# Question Bank: Lecture 3 (Steganalysis)

**Q1.** What hypothesis is the chi-square attack testing when applied to a suspect image?

*Answer:* It tests whether the observed histogram matches the pattern expected from full sequential LSB replacement — specifically, whether counts of adjacent value pairs (2k, 2k+1) have been pulled toward equal, which is the signature LSB overwriting leaves behind.

**Q2.** A histogram pair has `h[2k] = 80`, `h[2k+1] = 20`. Compute the chi-square contribution for this pair, and state what a value this large suggests.

*Answer:* `h_avg = 50`. Contribution = `(80-50)²/50 + (20-50)²/50 = 900/50 + 900/50 = 18 + 18 = 36`. A large contribution like this suggests the pair is *far* from equalized — i.e., this region does not show the signature of full sequential LSB embedding (more consistent with a clean image, or embedding that didn't reach here).

**Q3.** Why does RS analysis remain effective at lower embedding rates than the chi-square attack?

*Answer:* RS analysis examines local pixel-group relationships (smoothness before/after an LSB flip) rather than the global single-value histogram. Even small amounts of embedding measurably shift the balance between Regular and Singular groups in the regions where it occurs, whereas a low embedding rate barely perturbs the overall histogram shape that chi-square relies on.

**Q4.** What makes SPAM/SRM "blind" steganalysis methods, as opposed to the chi-square attack or RS analysis?

*Answer:* Chi-square and RS analysis are built around the specific statistical signature of one embedding family (sequential LSB replacement/overwrite). SPAM/SRM instead extract broad, generic statistical features (pixel-difference correlations, multiple noise-residual co-occurrences) and use a trained classifier to separate cover from stego — without assuming which specific algorithm was used, making them effective against a wide range of unknown methods.

**Q5.** Why is a fixed, high-pass filter often used as the *first layer* of a CNN steganalyzer, instead of letting the network learn its own first-layer filters from raw pixels?

*Answer:* Raw pixel values are dominated by image *content* (the actual scene), which is huge compared to the tiny amplitude of an embedding signal. A fixed high-pass/noise-residual filter suppresses image content upfront and boosts the noise-like embedding signal, giving the rest of the network a cleaner signal to learn from rather than having to first discover this suppression on its own.

**Q6.** What is "cover-source mismatch," and why is it a limitation of CNN-based steganalysis specifically (more so than, say, the chi-square attack)?

*Answer:* Cover-source mismatch is the drop in detection accuracy when a detector trained on one distribution (specific cameras/cover images, embedding algorithm, or payload rate) is tested against a different distribution. CNNs learn distribution-specific features during training, so they can overfit to their training data's quirks; a simple statistical test like chi-square, by contrast, is a fixed formula that behaves identically regardless of training data (it has no training data at all).

**Q7.** OutGuess defeats the chi-square attack. Name one attack from this lecture that could still catch OutGuess, and explain what statistic it uses that OutGuess doesn't repair.

*Answer:* SRM (or any blockiness/co-occurrence-based second-order test). OutGuess's correction phase only repairs the *first-order* histogram (single-coefficient value counts). SRM-style features measure relationships *between* coefficients/pixels (co-occurrence, pairwise correlation) — higher-order statistics that OutGuess's correction does not address.

**Q8.** A student claims: "If an image passes the chi-square test (high p-value / normal-looking histogram), it must be clean." Is this claim correct? Explain.

*Answer:* No. Passing the chi-square test only rules out the specific signature of sequential LSB-overwrite-style embedding (JSteg-family). It says nothing about F5, OutGuess, LSB Matching, or adaptive schemes — all deliberately designed to leave a normal first-order histogram. A negative chi-square result is evidence *against one specific embedding family*, not proof of a clean image.

---

# Question Bank: Cross-Topic / Integrative

**Q1.** Compare basic sequential LSB (Lecture 1) and JSteg (Lecture 2): what do they have in common structurally, and what's the key difference in *where* they embed?

*Answer:* Both directly overwrite the LSB of a value based on the message bit, and both are vulnerable to the chi-square attack for the same underlying reason (pair-of-values equalization). The key difference is domain: basic LSB modifies raw spatial-domain pixel values directly, while JSteg modifies quantized DCT coefficients inside the JPEG compression pipeline — which is why JSteg survives JPEG compression and basic LSB does not.

**Q2.** A steganalyst has an image and doesn't know which algorithm (if any) was used to embed data. Describe a sensible order in which to apply the techniques from Lecture 3, from cheapest/most-specific to most general, and explain the tradeoff.

*Answer:* Start with cheap, targeted tests (visual LSB-plane inspection, then chi-square attack) since they're fast and immediately rule in/out the most naive embedding families. If those come back negative, move to RS analysis (still targeted at LSB-style embedding but more sensitive). If still inconclusive, fall back to blind/universal methods (SRM, then CNN-based classifiers) which are more expensive (need training data / more computation) but catch a much broader range of algorithms, including ones specifically designed to defeat the cheaper tests.

**Q3.** Both Adaptive LSB (Lecture 1) and F5's matrix encoding (Lecture 2) aim to reduce detectability — but by different mechanisms. Contrast them.

*Answer:* Adaptive LSB reduces detectability by choosing *where* to embed (favoring high-variance/textured regions where changes are naturally masked), without changing how each individual bit is embedded. F5's matrix encoding reduces detectability by changing *how many* coefficients need to be modified at all (embedding k bits by changing at most 1 coefficient out of 2^k−1), reducing the total number of changes regardless of where they occur. One is spatial/positional; the other is about embedding efficiency.

**Q4.** Explain, using concepts from at least two different lectures, why OutGuess having lower capacity than JSteg is a deliberate design tradeoff rather than a flaw.

*Answer:* From Lecture 2: OutGuess reserves roughly half its usable coefficients for a correction phase that repairs the first-order histogram after embedding. From Lecture 3: this repair is specifically what defeats the chi-square attack, which JSteg fails. The capacity loss isn't accidental — it's the direct cost of buying statistical security. This mirrors the same tradeoff in Lecture 1, where Randomized/Adaptive LSB also sacrifice some capacity (skipped positions/regions) for the same reason: security against detection costs usable bits.

---

# Mock Final Exam

**Time allowed:** 3 hours | **Total points:** 100
**Instructions:** Attempt all sections. Show your work for calculation questions — partial credit is available. Do not consult the lecture notes or the question bank above until you've finished.

## Part A — Multiple Choice (10 x 2 = 20 points)

Circle the single best answer.

**A1.** Which operation reads the least significant bit of an integer `x` in Python?
a) `x >> 1`  b) `x & 1`  c) `x | 1`  d) `x ^ 1`

**A2.** A 1200x900 RGB image has a maximum 1-bit LSB capacity of:
a) 1,080,000 bits  b) 3,240,000 bits  c) 1,080,000 bytes  d) 324,000 bytes

**A3.** Which LSB variant embeds only in pixels selected by a key-driven pseudo-random sequence?
a) LSB Matching  b) Adaptive LSB  c) Randomized LSB  d) LSB2

**A4.** Why must LSB steganography use a lossless image format?
a) Lossless formats are always smaller  b) Lossy compression alters/destroys exact pixel values  c) Lossless formats support more colors  d) It's only a convention, not a technical requirement

**A5.** In the DCT coefficient matrix of an 8x8 block, the DC coefficient is located:
a) Bottom-right  b) Center  c) Top-left  d) It varies per block

**A6.** JSteg skips DCT coefficients with a magnitude of 1 primarily to avoid:
a) Slowing down the algorithm  b) Creating extra zero coefficients (detectable) c) Visible pixel artifacts  d) Exceeding JPEG's coefficient range

**A7.** F5's core mechanism for embedding a mismatched bit is to:
a) Overwrite the LSB directly  b) Move the coefficient one step toward zero  c) Swap the coefficient with a neighbor  d) Add random noise to the coefficient

**A8.** OutGuess's correction phase mainly targets:
a) Visual artifacts  b) The first-order coefficient histogram  c) File size  d) The DC coefficient

**A9.** The chi-square attack is most effective against:
a) F5  b) OutGuess  c) Sequential LSB / JSteg  d) CNN-based embedding

**A10.** Which steganalysis method is described as "blind" / algorithm-agnostic?
a) Chi-square attack  b) RS analysis  c) Category attack  d) SRM

## Part B — Short Answer (5 x 6 = 30 points)

**B1.** Explain, in 2-3 sentences, why LSB steganography is considered "almost invisible" to the human eye.

**B2.** Describe the difference between LSB replacement and LSB Matching, and state one statistical consequence of that difference.

**B3.** Explain the "energy compaction" property of DCT and why it is essential to JPEG compression.

**B4.** What is "shrinkage" in F5, and how does F5's embedding algorithm handle it?

**B5.** Explain why passing a chi-square test does not prove an image is free of hidden data.

## Part C — Calculation (3 x 10 = 30 points)

**C1.** A 1600×1200 grayscale image is used for 1-bit sequential LSB embedding.
(a) What is its maximum capacity, in bytes?
(b) If a message requires 45,000 bytes (including a 4-byte length header), what percentage of capacity is used?

**C2.** A histogram has three value pairs with the following counts:

| Pair | h[2k] | h[2k+1] |
|------|-------|---------|
| (50,51) | 60 | 40 |
| (100,101) | 45 | 45 |
| (150,151) | 70 | 72 |

Compute the chi-square contribution for each pair and the total χ² across all three. Which pair looks most consistent with full LSB embedding, and why?

**C3.** Using (1, 3, 2) matrix encoding, three coefficient LSBs are `x1=1, x2=1, x3=0`. The message bits to embed are `(m1, m2) = (1, 1)`. Determine `s1`, `s2`, `d1`, `d2`, and state which coefficient (if any) must change.

## Part D — Code Tracing (2 x 10 = 20 points)

**D1.** Trace through this function with `pixel = 156` and `bit = 1`. Show the binary value of `pixel` at each labeled step, and give the final decimal result.

```python
def embed_bit(pixel, bit):
    step1 = pixel & ~1     # A
    step2 = step1 | bit    # B
    return step2
```

**D2.** Trace this simplified F5-style function with `coeff = -2` and `target_bit = 1`. State whether the function modifies `coeff`, what the new value is (if changed), and whether shrinkage occurs.

```python
def f5_step(coeff, target_bit):
    if coeff == 0:
        return coeff, False  # skip

    current_bit = abs(coeff) & 1
    if current_bit == target_bit:
        return coeff, False  # no change needed

    if coeff > 0:
        coeff -= 1
    else:
        coeff += 1

    shrinkage = (coeff == 0)
    return coeff, shrinkage
```

---

# Mock Final Exam — Answer Key

## Part A

| # | Answer |
|---|--------|
| A1 | b) `x & 1` |
| A2 | b) 3,240,000 bits |
| A3 | c) Randomized LSB |
| A4 | b) Lossy compression alters/destroys exact pixel values |
| A5 | c) Top-left |
| A6 | b) Creating extra zero coefficients (detectable) |
| A7 | b) Move the coefficient one step toward zero |
| A8 | b) The first-order coefficient histogram |
| A9 | c) Sequential LSB / JSteg |
| A10 | d) SRM |

> **Note on A2:** the question describes an *RGB* image, so capacity is `1200 × 900 × 3 = 3,240,000` bits — answer **(b)**, not (a). (a) would only be correct for a grayscale image of the same dimensions. This is a deliberate trap testing whether you account for all 3 channels — re-read calculation questions carefully for "RGB" vs "grayscale."

## Part B

**B1.** The least significant bit contributes only ±1 to a channel's value (out of 0–255), which is a change of well under 1% of the channel's range. Human vision cannot reliably distinguish such a small intensity difference, especially when it's confined to one bit of one channel per pixel, so the modified image looks visually identical to the original.

**B2.** LSB replacement always *forces* the LSB to a specific value (0 or 1) — if it already matches, nothing changes; if not, it's overwritten. LSB Matching, when there's a mismatch, instead randomly adds or subtracts 1 from the pixel — it never directly sets the bit. Statistical consequence: replacement causes adjacent value pairs (2k, 2k+1) to equalize in frequency (detectable by chi-square), while matching spreads changes to either neighboring value, avoiding this pair-equalization signature.

**B3.** Energy compaction means that after applying DCT to an image block, most of the block's signal energy concentrates into a small number of low-frequency coefficients (top-left), while many high-frequency coefficients are small or zero. JPEG exploits this by quantizing (reducing precision of) the high-frequency coefficients heavily — since they carry little energy/information, this produces large file-size savings with minimal perceptible quality loss, which is the whole basis of JPEG's lossy compression.

**B4.** Shrinkage occurs when F5 decrements a coefficient with magnitude 1 toward zero, turning it into a zero coefficient — but zero coefficients are always skipped during extraction, so the bit intended for that position is lost. F5 handles this by not advancing to the next message bit when shrinkage happens; instead, it retries embedding the same (lost) bit into the next usable non-zero coefficient.

**B5.** The chi-square test only detects one specific signature: the pair-of-values equalization left by sequential LSB-overwrite-style embedding (e.g. basic LSB, JSteg). Algorithms like F5 (decrement toward zero) and OutGuess (explicit histogram correction) are specifically designed to avoid this exact signature while still hiding data, so an image can pass the chi-square test and still contain a hidden message embedded by one of these other methods.

## Part C

**C1.**
(a) `1600 × 1200 × 1 = 1,920,000 bits = 240,000 bytes`
(b) `45,000 / 240,000 = 0.1875 = 18.75%`

**C2.**

- Pair (50,51): `h_avg = 50`. Contribution = `(60-50)²/50 + (40-50)²/50 = 100/50 + 100/50 = 2 + 2 = 4`
- Pair (100,101): `h_avg = 45`. Contribution = `(45-45)²/45 + (45-45)²/45 = 0`
- Pair (150,151): `h_avg = 71`. Contribution = `(70-71)²/71 + (72-71)²/71 = 1/71 + 1/71 ≈ 0.028`

Total χ² ≈ `4 + 0 + 0.028 = 4.028`

The pair (100,101) is most consistent with full LSB embedding — its contribution is exactly 0, meaning its counts are already perfectly equalized (45/45), matching the textbook signature of sequential LSB replacement.

**C3.**
`s1 = x1 XOR x3 = 1 XOR 0 = 1`
`s2 = x2 XOR x3 = 1 XOR 0 = 1`
`d1 = s1 XOR m1 = 1 XOR 1 = 0`
`d2 = s2 XOR m2 = 1 XOR 1 = 0`
`(d1, d2) = (0, 0)` → **no coefficient needs to change**; the current LSBs already encode message bits `(1, 1)`.

## Part D

**D1.**
`pixel = 156 = 10011100`
Step A: `156 & ~1` → clears LSB → `10011100` = 156 (already even, unchanged)
Step B: `156 | 1` → sets LSB to 1 → `10011101` = **157**
Final result: **157**

**D2.**
`coeff = -2`, `abs(-2) & 1 = 0`. `target_bit = 1`. Current bit (0) does not match target (1), so the function proceeds: since `coeff < 0`, it does `coeff += 1` → `coeff = -1`.
`shrinkage = (coeff == 0)` → `-1 == 0` is False.
Result: coeff is modified to **-1**, shrinkage **does not** occur (it would only occur if the result were exactly 0, e.g. starting from -1 or +1).
