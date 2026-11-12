"""E2: two sources A, B into C with weights (wa, wb). Truth table; also B one tick early/late."""
import sys, numpy as np
sys.path.insert(0, '.')
from gn27 import Net, Beats, RELAY, settle

def case(a, b, wa, wb, lag=0, ticks=40):
    net = settle(Net([RELAY]*3, [(0,2,wa,0),(1,2,wb,0)]))
    d = Beats(3)
    for t in range(ticks):
        sp = np.zeros(3)
        if a and t < 2: sp[0] = -10
        if b and lag <= t < lag+2: sp[1] = -10
        d.see(net.step(sp_ext=sp), t)
    return d.ev[2]

def table(wa, wb, lag=0):
    return ''.join('1' if case(a,b,wa,wb,lag) else '0' for a,b in [(0,0),(1,0),(0,1),(1,1)])

if __name__ == '__main__':
    print("truth table order: 00 10 01 11   (A=world, B=ring)")
    for wa in (-4.5,-5.0,-6.0):
        for wb in (1,2,3,4,5,6,8):
            print(f"wa={wa:5} wb=+{wb}: {table(wa,wb)}   lag+1: {table(wa,wb,1)}  lag-? n/a")
