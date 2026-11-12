"""E7: a bank of self-writing rings (N = 5..10 relays, laps 20..40 ticks) on one world.
The ring whose error unit falls silent has found the world's period. Runs GN27 (default) or --window."""
import sys, numpy as np
sys.path.insert(0, '.')
import gn27, window
USE_WINDOW = '--window' in sys.argv
Net, settle = (window.WindowNet, window.settle) if USE_WINDOW else (gn27.Net, gn27.settle)
from gn27 import Beats, RELAY

def bank(sizes):
    edges, err, read, n = [], [], [], 1          # unit 0 = world
    for N in sizes:
        base = n; read.append(base)
        edges += [(base+k, base+(k+1) % N, -6.0, 0) for k in range(N)]
        e = base + N
        edges += [(0, e, -4.5, 0), (base, e, -4.5, 0), (e, base+2, -6.0, 0)]
        err.append(e); n = e + 1
    return settle(Net([RELAY]*n, edges)), err, read, n

def run(sizes, beats, ticks):
    net, err, read, n = bank(sizes); d = Beats(n)
    P = set(); [P.update({b-4, b-3}) for b in beats]
    for t in range(ticks):
        sp = np.zeros(n)
        if t in P: sp[0] = -10
        d.see(net.step(sp_ext=sp), t)
    return d, err

if __name__ == '__main__':
    sizes = [5, 6, 7, 8, 9, 10]
    print("rings of", sizes, "relays = laps", [4*s for s in sizes], "ticks;", "WINDOW control" if USE_WINDOW else "GN27")
    for name, period, sl in [("period 28, one beat", 28, [0]), ("period 36, beats at 0,8,20", 36, None),
                             ("period 24, one beat", 24, [0]), ("period 40, beats 0,12", 40, None)]:
        offs = {36: [0, 8, 20], 40: [0, 12]}.get(period, [0])
        beats = [40 + p*period + o for p in range(80) for o in offs]
        T = 40*period
        d, err = run(sizes, beats, T)
        late = [sum(1 for x in d.ev[e] if x > T//2) for e in err]
        print(f"  {name:28}: errors in 2nd half per ring {dict(zip([4*s for s in sizes], late))}")
