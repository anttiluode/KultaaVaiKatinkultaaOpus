"""E5: stress the XOR self-writing ring: all 255 patterns, other periods, jitter, omissions."""
import sys, numpy as np, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'experiments')
from e4_selfring import run, per_lap, slots

def pattern(sl, period=32, start=40, until=10**9, jitter=0, rng=None):
    out=[]
    for p in range(300):
        for s in sl:
            b = start + p*period + 4*s
            if b >= until: continue
            if jitter and rng is not None: b += int(rng.integers(-jitter, jitter+1))
            out.append(b)
    return out

if __name__ == '__main__':
    L = 20
    ok = 0; bad = []
    for k in range(1, 256):
        sl = [i for i in range(8) if k >> i & 1]
        d = run(pattern(sl), L*32, "xor")
        w = per_lap(d.ev[9], L)
        quiet = sum(w[8:]) == 0
        match = slots(d.ev[1], L-1) == slots(d.ev[0], L-1)
        if quiet and match: ok += 1
        else: bad.append((sl, w[:8], slots(d.ev[1], L-1), slots(d.ev[0], L-1)))
    print(f"all 255 nonempty 8-slot patterns: learned and silent after lap 8 in {ok}/255")
    for b in bad[:6]: print("  fail:", b)

    print("\nworld period != 32 (one beat per period):")
    for per in (16, 8, 64, 28, 36, 30):
        d = run(pattern([0], period=per), 30*32, "xor")
        print(f"  period {per:3}: errors/lap {per_lap(d.ev[9],30)}")

    print("\njitter (world beat moved by up to +-j ticks), pattern {0,3,5}:")
    for j in (1, 2):
        rng = np.random.default_rng(1)
        d = run(pattern([0,3,5], jitter=j, rng=rng), 30*32, "xor")
        print(f"  j={j}: errors/lap {per_lap(d.ev[9],30)}")

    print("\nsingle omission at lap 12, pattern {0,3,5}:")
    beats = [b for b in pattern([0,3,5]) if not (12*32 <= b < 13*32 and (b-40) % 32 == 0)]
    d = run(beats, 25*32, "xor")
    print(f"  errors/lap {per_lap(d.ev[9],25)}")
