"""E9: WHY does GN27 differ from the window neuron (signed-pair failures in E8, the leak in E7)?
Hypotheses: (a) the 50-tick variance memory drops below 0.1 and flips a unit into 'amplify';
(b) beat-wire amplitude is not exactly 2.0 (FACTS.md: 1.76..2.00 with square size), so a drive
that sits near a band edge in the window model falls outside it in GN27.
We log both per unit and see which one co-occurs with the failures."""
import sys, numpy as np
sys.path[:0] = ['.', 'experiments']
import gn27
from gn27 import Net, Beats, RELAY, settle, WIRE, QMIN
from e8_sol_patterns import graph

def trace(schedule, kind, n=11):
    net = settle(Net([RELAY]*n, graph(kind))); det = Beats(n)
    amp_states, wires = [], []
    for t in range(len(schedule)*32):
        lap, slot = divmod(t, 32); sp = np.zeros(n)
        if any(0 <= slot-p < 2 for p in schedule[lap]): sp[0] = -10
        det.see(net.step(sp_ext=sp), t)
        amp_states.append(net.var < 0.1)
        w = net.sent[0]; wires += list(w[w > 0.5])
    return det, np.array(amp_states), np.array(wires)

for ph in ([0, 8, 16, 24], [3, 11, 19, 27], [0, 4, 8, 12, 16, 20, 24, 28]):
    for kind in ("signed", "xor"):
        det, amp, wires = trace([ph]*12, kind)
        w = {t for t in det.ev[0] if t >= 64}; p = {t for t in det.ev[1] if t >= 64}
        print(f"{str(ph):28} {kind:6}: misses {len(w-p)} extras {len(p-w)} | "
              f"ticks any unit in amplify (var<0.1): {int(amp.any(axis=1).sum())} | "
              f"beat-wire values seen: {sorted(set(np.round(wires,2)))}")

# --- causal test for (b): window neuron whose beat wire is weaker than 2.0 -----------------------
import window, e8_sol_patterns as e8
print("\nwindow neuron with a fixed weaker beat wire (GN's wire ranges 1.76..2.00):")
for amp in (2.0, 1.88, 1.76):
    class W(window.WindowNet):
        def step(self, ext=None, sp_ext=None):
            out = super().step(ext, sp_ext); return out
    orig = window.WindowNet.step
    def step(self, ext=None, sp_ext=None, amp=amp):
        fire = self.pipe[0].copy(); self.wire = np.where(fire, amp, 0.0); self.sent = self.wire[None, :]
        m = np.zeros(self.n)
        for j, i, w, L in self.edges: m[i] += w * self.wire[j]
        if sp_ext is not None: m = m + sp_ext
        self.pipe = np.vstack([self.pipe[1:], ((m >= window.LO) & (m <= window.HI))[None, :]]); self.t += 1
        return np.where(fire, 4.0, 1.5)
    window.WindowNet.step = step
    e8.Net, e8.settle = window.WindowNet, window.settle
    res = {k: sum(e8.score(ph, k)["mem_ok"] for ph in e8.sol_patterns()) for k in ("signed", "xor")}
    window.WindowNet.step = orig
    print(f"  wire {amp}: memory exact  signed {res['signed']}/33   xor {res['xor']}/33")

# --- the E7 leak: variance or not? ----------------------------------------------------------------
import e7_bank
net, err, read, n = e7_bank.bank([9]); det = Beats(n); amp_ticks = 0
beats = [40 + p*36 + o for p in range(200) for o in (0, 8, 20)]; P = set()
[P.update({b-4, b-3}) for b in beats]
for t in range(60*36):
    sp = np.zeros(n)
    if t in P: sp[0] = -10
    det.see(net.step(sp_ext=sp), t); amp_ticks += int((net.var < 0.1).any())
print(f"\nE7 leak (9-relay ring, beats 0,8,20 per 36): error beats {len(det.ev[err[0]])}, "
      f"ticks any unit in amplify: {amp_ticks}")

# --- (b') beat strength that varies beat to beat, as in GN (1.76..2.00), random not state-driven ---
print("\nwindow neuron, each beat's wire drawn from GN's observed values {1.76,1.88,1.91,1.95,1.97,2.0}:")
VALS = np.array([1.76, 1.88, 1.91, 1.95, 1.97, 2.0]); orig = window.WindowNet.step
for seed in (1, 2, 3):
    rng = np.random.default_rng(seed)
    def step(self, ext=None, sp_ext=None):
        fire = self.pipe[0].copy()
        if not hasattr(self, "amp"): self.amp = np.full(self.n, 2.0)
        onset = fire & ~getattr(self, "prevfire", np.zeros(self.n, bool))
        self.amp = np.where(onset, rng.choice(VALS, self.n), self.amp); self.prevfire = fire
        self.wire = np.where(fire, self.amp, 0.0); self.sent = self.wire[None, :]
        m = np.zeros(self.n)
        for j, i, w, L in self.edges: m[i] += w * self.wire[j]
        if sp_ext is not None: m = m + sp_ext
        self.pipe = np.vstack([self.pipe[1:], ((m >= window.LO) & (m <= window.HI))[None, :]]); self.t += 1
        return np.where(fire, 4.0, 1.5)
    window.WindowNet.step = step
    res = {k: sum(e8.score(ph, k)["mem_ok"] for ph in e8.sol_patterns()) for k in ("signed", "xor")}
    window.WindowNet.step = orig
    print(f"  seed {seed}: memory exact  signed {res['signed']}/33   xor {res['xor']}/33")
