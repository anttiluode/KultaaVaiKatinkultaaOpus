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
- That the checkerboard adds any capability. Every positive result reproduces without it.
- Any tolerance to timing noise: ±1 tick breaks everything. Real input (taps, audio) would need quantising to the 4-tick grid first.
- Learning of a rule or a period. The ring learns content, and the period is set by how many relays it has.
- Anything about biology. The analogies (dendritic calcium spikes, mismatch neurons, comb filters) are of function, not mechanism.

**Corrections to claims made today:**
- Opus predicted the response might be periodic and allow 3-input parity: **wrong**, one band.
- Gemini's "+12 erase was proven 12/12 in V27": not in V27's FACTS.md. Erasing does work (E3), now measured here.
- Gemini's Kolmogorov-complexity reading: the ring length that silences the error measures the **period**, not Kolmogorov complexity.
- Sol's report that naive feedback goes wrong on removed/added events: with the error unit writing into node 3 at −6, the naive version handled switching and stopping here. The difference may be weights or write position; worth comparing.

## Where the geometry could still earn its place

The window neuron has no slow state. GN27 does: a 50-tick variance memory, a clock mode (constant 1.0), the four interleaved lanes, the leak seen in E7. Tests that could separate them:

1. **Jitter.** Can a slow GN variable widen the coincidence window, so ±1 tick no longer breaks the ring? The window neuron cannot do that.
2. **The leak.** E7's leak is the first GN-only behaviour. Is it noise, or a forgetting mechanism that could be put to use?
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
