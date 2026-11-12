"""E8: Sol's 33 stress patterns (KultaaVaiKatinkultaa/experiments/stress.py, same seed and scoring)
run on BOTH circuits: Sol's signed pair (innovation + omission units, two wires) and
Opus' single XOR wire. Same GN27, same world encoding (2-tick pulse at phase p, beat at p+4)."""
import sys, random, numpy as np
sys.path.insert(0, '.')
import gn27, window
from gn27 import Beats, RELAY
USE_WINDOW = '--window' in sys.argv
Net, settle = (window.WindowNet, window.settle) if USE_WINDOW else (gn27.Net, gn27.settle)

def graph(kind):
    e = [(i+1, 1+(i+1) % 8, -6.0, 0) for i in range(8)]
    if kind == "signed":   # Sol's circuit, copied
        e += [(0, 9, -5.0, 0), (1, 9, +5.0, 0), (0, 10, +5.0, 0), (1, 10, -5.0, 0),
              (9, 3, -6.0, 0), (10, 3, +6.0, 0)]
    else:                  # one XOR unit, one wire
        e += [(0, 9, -4.5, 0), (1, 9, -4.5, 0), (9, 3, -6.0, 0)]
    return e

def learn(schedule, kind):
    net = settle(Net([RELAY]*11, graph(kind))); det = Beats(11)
    for t in range(len(schedule)*32):
        lap, slot = divmod(t, 32); sp = np.zeros(11)
        if any(0 <= slot-p < 2 for p in schedule[lap]): sp[0] = -10
        det.see(net.step(sp_ext=sp), t)
    return det.ev

def sol_patterns():
    rng = random.Random(27)
    pats = [[0],[0,16],[0,8,16,24],[0,2],[0,4],[0,4,8],[0,4,8,12,16,20,24,28],[0,2,4,6],[3,11,19,27]]
    for n in range(1, 7):
        for _ in range(4): pats.append(sorted(rng.sample(list(range(0,32,2)), n)))
    return pats

def score(ph, kind, laps=12):
    ev = learn([ph]*laps, kind); s, e = 64, laps*32
    world = {t for t in ev[0] if s <= t < e}; pred = {t for t in ev[1] if s <= t < e}
    req = {l*32+p+4 for l in range(laps) for p in ph if s <= l*32+p+4 < e}
    return dict(src_ok=world == req, mem_ok=world == pred, miss=len(world-pred), extra=len(pred-world))

if __name__ == '__main__':
    print("GN27" if not USE_WINDOW else "WINDOW control")
    tot = {"signed": [0,0,0], "xor": [0,0,0]}
    for ph in sol_patterns():
        row = []
        for kind in ("signed", "xor"):
            r = score(ph, kind)
            tot[kind][0] += r["src_ok"]; tot[kind][1] += r["mem_ok"]; tot[kind][2] += r["src_ok"] and r["mem_ok"]
            row.append(f"{kind}: mem {'ok ' if r['mem_ok'] else f'miss{r[chr(109)+chr(105)+chr(115)+chr(115)]}/x{r[chr(101)+chr(120)+chr(116)+chr(114)+chr(97)]}'}")
        print(f"{str(ph):34} src {'ok' if r['src_ok'] else 'BAD'}  | " + " | ".join(row))
    for k, (s, m, b) in tot.items():
        print(f"{k:6}: source exact {s}/33   memory exact {m}/33   both {b}/33")
