import unittest
from explain_prefetch import Predictor,walk,MAX_LINE
class PredictorTests(unittest.TestCase):
    def test_training_and_same_line(self):
        self.assertEqual([x['candidate'] for x in walk([10,11,11,12,13])],[None,None,None,13,14])
    def test_reverse_and_bounds(self):
        self.assertEqual([x['candidate'] for x in walk([30,20,10,0])],[None,None,0,None])
        self.assertIsNone(walk([MAX_LINE-2,MAX_LINE-1,MAX_LINE])[-1]['candidate'])
    def test_disabled_training(self):
        p=Predictor()
        for x in [10,11,12]:self.assertIsNone(p.observe(x,False)['candidate'])
        self.assertEqual(p.observe(13)['candidate'],14)
    def test_phase_change(self):
        p=Predictor()
        for x in [10,11,12]:p.observe(x)
        self.assertIsNone(p.observe(20)['candidate']);self.assertEqual(p.observe(28)['candidate'],36)
    def test_next_line(self):
        self.assertEqual([x['candidate'] for x in walk([10,10,40,MAX_LINE],'next_line')],[11,None,41,None])
    def test_invalid(self):
        for x in [-1,MAX_LINE+1,True]:
            with self.assertRaises(ValueError):Predictor().observe(x)
