"""Run: python -m unittest discover -s tests -v   (from the repo root)"""
import sys, unittest, importlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import numpy as np


class GN(unittest.TestCase):
    """Native GN27 relays (unchanged V27 equations and taps.json)."""
    def test_single_band(self):
        from e1_transfer import pulse_response
        fires = [m for m in np.arange(-30, 12.01, 0.5) if pulse_response(m)]
        self.assertTrue(all(-13.5 <= m <= -8.5 for m in fires))
        self.assertFalse(any(m > 0 for m in fires))

    def test_xor_and_counting(self):
        from e1_transfer import k_sources
        self.assertEqual([bool(k_sources(k, -4.5)) for k in (1, 2, 3)], [True, False, False])
        self.assertEqual([bool(k_sources(k, -2.5)) for k in (1, 2, 3)], [False, True, False])

    def test_world_and_not_ring(self):
        from e2_mixed import table
        self.assertEqual(table(-4.5, 5.0), "0100")

    def test_selective_erase(self):
        from e3_erase import run
        d, _ = run([0, 4])
        t4 = [x for x in d.ev[4] if x > 64][0]
        _, last = run([0, 4], erase=(4, t4 - 4, 6, 2))
        self.assertEqual(len(last), 1)

    def test_self_writing_ring_learns_switches_stops(self):
        from e4_selfring import run, per_lap, slots
        from e5_stress import pattern
        beats = pattern([0, 3, 5], until=12 * 32) + pattern([1, 6], start=12 * 32 + 8)
        d = run(beats, 24 * 32, "xor")
        w = per_lap(d.ev[9], 24)
        self.assertEqual(sum(w[4:12]) + sum(w[15:]), 0)
        self.assertEqual(slots(d.ev[1], 23), slots(d.ev[0], 23))

    def test_tempo_bank(self):
        import e7_bank
        beats = [40 + p * 28 for p in range(80)]
        d, err = e7_bank.run([6, 7, 8], beats, 40 * 28)
        late = [sum(1 for x in d.ev[e] if x > 20 * 28) for e in err]
        self.assertEqual(late[1], 0)
        self.assertTrue(late[0] > 10 and late[2] > 10)


class Control(unittest.TestCase):
    """The abstract window neuron reproduces the self-writing ring on all 255 patterns."""
    def test_window_all_patterns(self):
        import gn27, window
        import e4_selfring
        old = e4_selfring.Net, e4_selfring.settle
        e4_selfring.Net, e4_selfring.settle = window.WindowNet, window.settle
        try:
            from e5_stress import pattern
            ok = 0
            for k in range(1, 256):
                sl = [i for i in range(8) if k >> i & 1]
                d = e4_selfring.run(pattern(sl), 20 * 32, "xor")
                w = e4_selfring.per_lap(d.ev[9], 20)
                ok += sum(w[8:]) == 0 and e4_selfring.slots(d.ev[1], 19) == e4_selfring.slots(d.ev[0], 19)
            self.assertEqual(ok, 255)
        finally:
            e4_selfring.Net, e4_selfring.settle = old



class SolCrossCheck(unittest.TestCase):
    """E8: Sol's 33 stress patterns. Reproduce Sol's signed-pair score; the XOR wire does better."""
    def test_signed_vs_xor_on_gn27(self):
        import importlib, gn27, e8_sol_patterns as e8
        e8.Net, e8.settle = gn27.Net, gn27.settle
        pats = e8.sol_patterns()
        signed = sum(e8.score(p, "signed")["mem_ok"] for p in pats)
        xor = sum(e8.score(p, "xor")["mem_ok"] for p in pats)
        self.assertEqual(signed, 22)
        self.assertEqual(xor, 31)


if __name__ == "__main__":
    unittest.main()
