"""E3: can a positive setpoint pulse on one ring node delete a passing beat, and leave others?"""
import sys, numpy as np
sys.path.insert(0, '.')
from gn27 import Net, Beats, RELAY, settle

N = 8
def ring(extra_units=0):
    edges = [(k, (k+1) % N, -6.0, 0) for k in range(N)]
    return settle(Net([RELAY]*(N+extra_units), edges))

def run(seeds, erase=None, laps=12):
    """seeds: ticks at which node0 gets a -10 2-tick pulse. erase=(node, tick, m, width)."""
    net = ring(); d = Beats(N)
    for t in range(laps*32):
        sp = np.zeros(N)
        if any(s <= t < s+2 for s in seeds): sp[0] = -10
        if erase and erase[1] <= t < erase[1]+erase[3]: sp[erase[0]] += erase[2]
        d.see(net.step(sp_ext=sp), t)
    # count beats on node 0 in last lap
    last = [x for x in d.ev[0] if x >= (laps-1)*32]
    return d, last

if __name__ == '__main__':
    d, last = run([0])
    print("one seed, node beat times first lap:", [ev[:2] for ev in d.ev])
    print("last-lap node0 beats:", last)
    # find erase windows: pulse node 4 near time the beat arrives (lap 3)
    t4 = [x for x in d.ev[4] if x > 64][0]
    print("beat reaches node4 at", t4)
    print("\nerase single beat: node4, offset vs beat arrival, magnitude m, width 2")
    for m in (4, 8, 12, 20):
        row=''
        for off in range(-8, 5):
            _, last = run([0], erase=(4, t4+off, m, 2))
            row += '0' if not last else str(len(last))
        print(f"m=+{m:2}: offsets -8..+4 -> {row}")
