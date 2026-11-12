"""E4: an empty 8-relay ring that writes AND erases itself from a world stream.

units: 0 world, 1..8 ring (read at 1), 9 WRITE (world AND NOT ring), 10 ERASE (ring AND NOT world)
Every unit is the unchanged GN27 relay. No if-statement decides what to store.
The world is a list of beat ticks (slot = 4 ticks, 8 slots per 32-tick lap).
"""
import sys, numpy as np
sys.path.insert(0, '.')
from gn27 import Net, Beats, RELAY, settle

W_IN, W_BLOCK, W_RING = -4.5, 5.0, -6.0

def build(mode="we", write_to=3, erase_to=3):
    e = [(1+k, 1+(k+1) % 8, W_RING, 0) for k in range(8)]
    e += [(0, 9, W_IN, 0), (1, 9, W_BLOCK if mode == "we" else W_IN, 0)]   # WRITE (or plain XOR)
    e += [(9, write_to, W_RING, 0)]
    if mode == "we":
        e += [(1, 10, W_IN, 0), (0, 10, W_BLOCK, 0), (10, erase_to, +6.0, 0)]
    return settle(Net([RELAY]*11, e))

def world_pulses(beat_ticks):
    s = set(); [s.update({b-4, b-3}) for b in beat_ticks]   # pulse 4 ticks before beat
    return s

def run(beat_ticks, ticks, mode="we", noise=None):
    net = build(mode); d = Beats(11); P = world_pulses(beat_ticks)
    for t in range(ticks):
        sp = np.zeros(11)
        if t in P: sp[0] = -10
        d.see(net.step(sp_ext=sp), t)
    return d

def per_lap(ev, laps, lap=32):
    out = [0]*laps
    for x in ev:
        if x//lap < laps: out[x//lap] += 1
    return out

def slots(ev, lap_idx, lap=32):
    return sorted({(x % lap)//4 for x in ev if x//lap == lap_idx})

if __name__ == '__main__':
    def pattern(slots_, period=32, start=40, until=10**9):
        return [start + p*period + 4*s for p in range(200) for s in slots_ if start+p*period+4*s < until]
    L = 30
    tests = {
      "one beat/lap":        pattern([0]),
      "three beats {0,3,5}": pattern([0,3,5]),
      "switch {0,3,5}->{1,6} at lap 15": [b for b in pattern([0,3,5], until=15*32)] + pattern([1,6], start=15*32+8),
      "stop at lap 15":      pattern([0,3,5], until=15*32),
    }
    for name, beats in tests.items():
        for mode in ("xor", "we"):
            d = run(beats, L*32, mode)
            w = per_lap(d.ev[9], L); e = per_lap(d.ev[10], L) if mode=="we" else [0]*L
            print(f"{name:34} {mode:3}  writes/lap {w}")
            if mode=="we": print(f"{'':38} erases/lap {e}")
            print(f"{'':38} ring@1 slots lap14 {slots(d.ev[1],14)} lap29 {slots(d.ev[1],29)}  world lap29 {slots(d.ev[0],29)}")
