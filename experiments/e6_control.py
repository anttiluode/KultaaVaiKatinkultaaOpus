"""E6: rerun E1, E2, E4, E5 with the window neuron swapped in for GN27."""
import sys, numpy as np, importlib
sys.path.insert(0, '.'); sys.path.insert(0, 'experiments')
import gn27, window
gn27.Net = window.WindowNet; gn27.settle = window.settle      # monkey-patch BEFORE importing experiments
import e1_transfer, e2_mixed, e4_selfring, e5_stress
for mod in (e1_transfer, e2_mixed, e4_selfring):
    mod.Net = window.WindowNet; mod.settle = window.settle
from e5_stress import pattern
from e4_selfring import run, per_lap, slots

print("k sources, window neuron:")
for w in (-6.5,-4.5,-4.0,-3.25,-2.5,-2.0,-1.5,-1.0):
    print(f"  w={w:5}: {' '.join('Y' if e1_transfer.k_sources(k,w) else '.' for k in (1,2,3,4))}")
print("XOR -4.5:", e2_mixed.table(-4.5,-4.5), " lag1:", e2_mixed.table(-4.5,-4.5,1))
print("world AND NOT ring (-4.5,+5):", e2_mixed.table(-4.5,5), " lag1:", e2_mixed.table(-4.5,5,1))
L=20; ok=0
for k in range(1,256):
    sl=[i for i in range(8) if k>>i&1]
    d=run(pattern(sl),L*32,"xor"); w=per_lap(d.ev[9],L)
    ok += sum(w[8:])==0 and slots(d.ev[1],L-1)==slots(d.ev[0],L-1)
print(f"self-writing ring, 255 patterns: {ok}/255")
for per in (16,64,28):
    print(f"  period {per}: errors/lap {per_lap(run(pattern([0],period=per),30*32,'xor').ev[9],30)}")
for j in (1,):
    d=run(pattern([0,3,5],jitter=j,rng=np.random.default_rng(1)),30*32,'xor')
    print(f"  jitter {j}: errors/lap {per_lap(d.ev[9],30)}")
beats=[b for b in pattern([0,3,5]) if not (12*32<=b<13*32 and (b-40)%32==0)]
print("  omission:", per_lap(run(beats,25*32,'xor').ev[9],25))
