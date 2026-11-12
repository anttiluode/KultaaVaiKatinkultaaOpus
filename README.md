# Kultaa vai katinkultaa? (Opus)

*Gold or fool's gold?* Opus 5.5's half of a two-repo check of the GN-XOR claims (Sol has [KultaaVaiKatinkultaa](https://github.com/anttiluode/KultaaVaiKatinkultaa)). Every result below was run on the **unchanged** V27 geometric neuron (`gn27.py` and `taps.json`, byte-identical to [GN-XOR](https://github.com/anttiluode/GN-XOR)), and then again on a control neuron with no checkerboard at all.

## Verdict in one paragraph

The gold is real, and it is in the **circuit**, not in the checkerboard. A ring of relays plus one XOR unit that writes back into the ring learns **all 255** possible 8-slot rhythms from empty, falls silent once it knows them, relearns when the rhythm changes, and empties when the rhythm stops. No line of code decides what to store. But an abstract "window neuron" (fire 4 ticks later if the input lands in a band) reproduces every one of those results, 17 times faster. The checkerboard's contribution is a way of making a band, plus one leak the abstract neuron does not have.

## What was tested

| # | Question | GN27 result | Window-neuron control |
|---|---|---|---|
| E1 | What does one relay answer to a setpoint pulse of strength m? | **One band only**: fires for m ≈ −13.5 … −8.5, hole near −11, silent everywhere else, never for positive m | band copied from GN |
| E1 | k identical sources at weight w | **"Exactly k" detector**: −4.5 fires for exactly 1 (XOR), −2.5 for exactly 2 (AND), −1.5 for 3 or 4 | same, edges differ by one step |
| E1 | 3-input parity (fires for 1 and 3)? | **Impossible**: one band, so no weight puts 1 and 3 inside while 2 is outside. My earlier "periodic" prediction was wrong | same |
| E2 | Gemini: world −4.5, ring +5 gives "world AND NOT ring"? | **Yes**, `0100`, when synchronous. One tick of lag breaks it | same |
| E3 | Can a positive pulse erase one circulating beat? | **Yes, selectively**, even at +4, but only at **one exact tick** (when the drive from the previous node lands) | — |
| E4 | Empty 8-relay ring + one XOR error unit writing into node 3 | Learns, goes silent, **switches** to a new pattern, **empties** when the world stops | same |
| E4 | Is a separate ERASE unit needed? | **No.** The plain XOR version already erases | same |
| E5 | All 255 nonempty 8-slot patterns | **255/255** learned, silent from lap 8 on | **255/255** |
| E5 | World periods 8, 16 | learned (they fit the 32-tick lap) | same |
| E5 | World periods 28, 30, 36, 64 | never settle: 1–3 errors per lap forever | same |
| E5 | ±1 tick jitter | **breaks**: 0–6 errors per lap, never settles | same |
| E5 | One omitted beat | costs exactly **two** errors (delete, rewrite) | same |
| E7 | Bank of rings, laps 20…40 ticks, one world | **the ring whose lap matches the world's period falls silent**: tempo read out by silence | same |
| E7 | Period 36, three beats, 9-relay ring | **one beat leaks every 2 laps** and the error unit rewrites it, forever | no leak |

## Round 2: cross-checking Sol and Gemini (E8, E9)

Sol's repo [KultaaVaiKatinkultaa](https://github.com/anttiluode/KultaaVaiKatinkultaa) built the **signed pair** (an innovation unit at −5/+5 that writes, an omission unit at +5/−5 that erases, two wires into the ring) and stressed it on 33 patterns, including off-grid phases. E8 runs Sol's exact patterns, seed and scoring on both circuits:

| Circuit | Source exact | **Memory exact** | Both |
|---|---|---|---|
| Sol's signed pair, GN27 | 20/33 | **22/33** (reproduces Sol's numbers exactly) | 14/33 |
| One XOR wire, GN27 | 20/33 | **31/33** | 19/33 |
| Signed pair, window neuron | 20/33 | **33/33** | 20/33 |
| One XOR wire, window neuron | 20/33 | **33/33** | 20/33 |

- **The single XOR wire is the better circuit on GN27.** One of its two misses (`[30]`) is slow convergence: it is locked from lap 3, and scoring starts at lap 2.
- **Source failures are identical everywhere.** Pulses 2 ticks apart merge in the input relay before reaching any memory, as Sol said.
- **The signed pair's failures are GN27-specific.** The window neuron does both circuits perfectly. Together with the E7 leak, that's two places where the geometry changes behaviour. In both, the change is a fault.

**E9 asks why**, testing Gemini's explanation (the 50-tick variance memory makes units fatigue):

| Failure | Any unit leaves its normal (damp) regime? | Verdict on "variance fatigue" |
|---|---|---|
| E7 leak, 9-relay ring | no, 0 ticks | **wrong** |
| Signed pair, `[0,8,16,24]` and `[3,11,19,27]` | no, 0 ticks | **wrong** |
| Signed pair, all 8 slots | yes, 17 ticks, with weak clock-like beats (0.56) | **right** here |

Two more controls: a uniformly weaker beat wire, and beat sizes drawn at random from GN's observed values (1.76–2.00). Neither reproduces the signed failures. Random beat size does make the XOR wire miss 4 patterns, because −4.5 × 1.76 falls below the band. **Remaining candidate, not yet tested:** the receiver itself. A resting relay is never still (FACTS.md: square size flickers between 40 and 52), so where its band edge sits may depend on its recent past.

**What I carry over:**
- From **Sol**: the 33-pattern stress set, the scoring that separates source failures from memory failures, and the jitter result (Sol and I independently find ±1 tick breaks it).
- From **Gemini**: the criticism that my control only covers the **relay regime** (constant 1.6, nothing on `signal_in`). That's correct. The window neuron replaces a GN27 relay in these circuits; it says nothing about the clock mode or `signal_in`, which it doesn't have. The claim is narrowed accordingly.

**Corrections:**
- **Mine, round 1:** I wrote that the +12 one-tick erase was "not proven in V27". It is: V27's README records it, 12 of 12 rings. I had only checked FACTS.md.
- **Gemini's round-2 summary:** there is no OR setting in my sweep (−3.5 to −3.75 fires for nothing; −4.0 fires for exactly one input). Learning takes about two laps, not one. The leak was in E7 (three beats per 36 ticks), not a dense pattern in E5.

## Why it works: the band makes arithmetic mod 2

When the error unit writes into a ring slot that is **empty**, the slot's drive is −12 (in the band): a beat is written. When the slot **already holds** a beat, the error's −12 adds to the neighbour's −12: −24, past the band, and the beat disappears. So a write is a toggle:

```
ring  <-  ring XOR error      and      error = world XOR ring
=>    ring  <-  world
```

The band turns "add one more input" into "flip the bit". Write and erase are the same operation, which is why no ERASE unit is needed. The error stream is

```
e(t) = w(t) XOR w(t - lap)
```

a mod-2 comb filter: silent exactly when the world repeats with the ring's lap.

## What it is, in known terms

- **A native "same as one lap ago" predictor.** It learns the rhythm, not a rule. It cannot learn a period that doesn't divide its lap; that is what the bank of rings is for.
- **Comb-filter tempo detection.** The bank (E7) is the classic comb-filter bank used for tempo estimation, built from one unit type.
- **Mismatch / omission responses.** Silent on match, one pulse on omission or extra. Unsigned; the ±5 unit (E2) gives the signed "world but not ring" half.
- **GF(2) arithmetic.** Ring plus XOR feedback is the same family as linear feedback shift registers. Rule-learning (changing *which* nodes feed back, Berlekamp–Massey style) is **not** done here.

None of these are new ideas. What is specific is that one accidental 2025 node graph does all of them with the same unchanged equation, and the learning is done by the units themselves.

## Honest ledger

**Verified (7 tests pass):** single band; XOR at −4.5 and AND at −2.5; world AND NOT ring at (−4.5, +5); selective erase by a positive pulse; self-writing ring learns, switches and stops; tempo bank picks the matching ring; window neuron reproduces 255/255.

**Not established:**
- That the checkerboard adds any capability **in the relay regime**. Every positive result there reproduces without it. The clock mode and `signal_in` are untested by the control.
- Any tolerance to timing noise: ±1 tick breaks everything. Real input (taps, audio) would need quantising to the 4-tick grid first.
- Learning of a rule or a period. The ring learns content, and the period is set by how many relays it has.
- Anything about biology. The analogies (dendritic calcium spikes, mismatch neurons, comb filters) are of function, not mechanism.

**Corrections to claims made today:**
- Opus predicted the response might be periodic and allow 3-input parity: **wrong**, one band.
- Gemini's "+12 erase was proven 12/12 in V27": **correct** (V27 README). I first checked only FACTS.md and wrongly said otherwise; see Round 2.
- Gemini's Kolmogorov-complexity reading: the ring length that silences the error measures the **period**, not Kolmogorov complexity.
- Sol's report that naive feedback goes wrong on removed/added events: with the error unit writing into node 3 at −6, the naive version handled switching and stopping here. The difference may be weights or write position; worth comparing.

## Where the geometry could still earn its place

The window neuron has no slow state. GN27 does: a 50-tick variance memory, a clock mode (constant 1.0), the four interleaved lanes, the leak seen in E7. Tests that could separate them:

1. **Jitter.** Can a slow GN variable widen the coincidence window, so ±1 tick no longer breaks the ring? The window neuron cannot do that.
2. **The receiver's resting flicker.** Both GN-only behaviours (E7 leak, signed-pair failures) survive the variance and beat-size explanations (E9). Test next: does the receiver's band edge move with its resting square size?
3. **A clock unit as the world.** Can a 1.0 clock entrain a ring, or a ring entrain a clock?

## Run

Python 3.10+, NumPy.

```sh
python -m unittest discover -s tests -v      # ~13 s
python experiments/e5_stress.py              # 255 patterns on GN27, ~40 s
python experiments/e6_control.py             # the same on the window neuron, ~2 s
python experiments/e7_bank.py [--window]     # tempo bank
```

Saved outputs are in `results/`. `gn27.py` and `taps.json` are copied unchanged from GN-XOR (sha256 `dca6e52b…` and `90c3de1c…`).

Lineage: [GeometricNeuronV27](https://github.com/anttiluode/GeometricNeuronV27) · [GN-XOR](https://github.com/anttiluode/GN-XOR) · [MuistoVaihde](https://github.com/anttiluode/MuistoVaihde). MIT.
