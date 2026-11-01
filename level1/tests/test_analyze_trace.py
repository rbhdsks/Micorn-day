import tempfile
import unittest
from pathlib import Path
from analyze_trace import analyze, parse_address, read_addresses


class TraceAnalysisTests(unittest.TestCase):
    def test_cache_line_mapping_and_reuse(self):
        result = analyze([0x1000, 0x1004, 0x1040, 0x1000])
        self.assertEqual(result['unique_cache_lines'], 2)
        self.assertEqual(result['adjacent_same_line_accesses'], 1)
        self.assertEqual(result['accesses_to_previously_seen_line'], 2)
        self.assertEqual(result['mean_reuse_gap_accesses'], 1.5)
        self.assertEqual(result['top_line_deltas'], [
            {'delta_lines': 0, 'count': 1},
            {'delta_lines': 1, 'count': 1},
            {'delta_lines': -1, 'count': 1}])

    def test_stride_in_line_units(self):
        result = analyze([0, 256, 512, 768])
        self.assertEqual(result['top_nonzero_line_deltas'], [{'delta_lines': 4, 'count': 3}])
        self.assertIsNone(result['mean_reuse_gap_accesses'])

    def test_single_access_has_no_transition_fraction(self):
        self.assertIsNone(analyze([0])['adjacent_same_line_fraction'])

    def test_invalid_inputs(self):
        for args in [([], 64), ([0], 0), ([0], 63), ([-1], 64)]:
            with self.assertRaises(ValueError):
                analyze(*args)
        with self.assertRaises(ValueError):
            parse_address('-1')
        self.assertEqual(parse_address('0100'), 100)
        self.assertEqual(parse_address('0x100'), 256)

    def test_parsing_and_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'trace.csv'
            path.write_text('address,pc\n0x1000,10\n4160,20\n')
            self.assertEqual(list(read_addresses(path, 'csv')), [4096, 4160])
            path.write_text('pc\n10\n')
            with self.assertRaisesRegex(ValueError, 'address column'):
                list(read_addresses(path, 'csv'))
            path.write_text('# example\n0x1000\nbad\n')
            with self.assertRaisesRegex(ValueError, 'line 3'):
                list(read_addresses(path, 'text'))


if __name__ == '__main__':
    unittest.main()
