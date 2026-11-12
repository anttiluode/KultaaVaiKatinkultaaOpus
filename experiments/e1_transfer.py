"""E1: how does one relay answer a setpoint pulse of strength m? And k identical sources?"""
import sys, numpy as np
sys.path.insert(0, '.')
from gn27 import Net, Beats, RELAY, settle

def pulse_response(m, width=2, ticks=40):
    net = settle(Net([RELAY]))
    b = Beats(1)
    for t in range(ticks):
        sp = np.array([m if t < width else 0.0])
        b.see(net.step(sp_ext=sp), t)
    return b.ev[0]

def k_sources(k, w, ticks=40):
    n = k + 1
    edges = [(j, k, w, 0) for j in range(k)]
    net = settle(Net([RELAY]*n, edges))
    b = Beats(n)
    for t in range(ticks):
        sp = np.zeros(n); 
        if t < 2: sp[:k] = -10.0
        b.see(net.step(sp_ext=sp), t)
    return b.ev[k]

if __name__ == '__main__':
    print("direct setpoint pulse m (2 ticks) -> receiver beats")
    for m in np.arange(-30, 12.01, 0.5):
        ev = pulse_response(m)
        print(f"{m:6.1f} {'#' if ev else '.'} {ev}")
