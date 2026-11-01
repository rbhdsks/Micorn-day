import unittest,math
from cdm_reference import FACTORS,probabilities,evaluate
class CDMTests(unittest.TestCase):
    def test_notes_initializations(self):
        for row,expected in zip(evaluate(),[.7510,.7425,.7536]):self.assertAlmostEqual(row['mean_nll'],expected,places=4)
    def test_normalization_and_diagonal_exclusion(self):
        for t,c in FACTORS.values():
            self.assertEqual(probabilities(t,c,[0]),{0:1.0})
            self.assertAlmostEqual(sum(probabilities(t,c,[0,1,2]).values()),1)
    def test_stable_large_scores(self):
        p=probabilities([[1000.],[1001.]],[[1000.],[999.]],[0,1])
        self.assertTrue(all(math.isfinite(v) for v in p.values()));self.assertAlmostEqual(sum(p.values()),1)
    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):probabilities(*FACTORS[1],[0,0])
