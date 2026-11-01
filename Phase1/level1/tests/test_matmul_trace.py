import csv
import json
import tempfile
import unittest
from pathlib import Path
from analyze_trace import analyze, read_addresses
from generate_matmul_trace import Config, generate, layout


class MatmulTraceTests(unittest.TestCase):
    def test_numeric_reference_and_address_bounds_for_both_orders(self):
        config = Config(2, 3, 4)
        with tempfile.TemporaryDirectory() as temporary:
            results = []
            for order in ('ijk', 'ikj'):
                path = Path(temporary) / order
                metadata = generate(path, config, order)
                with (path / 'trace.csv').open() as source:
                    rows = list(csv.DictReader(source))
                self.assertEqual(len(rows), 2 * 4 + 4 * 2 * 3 * 4)
                self.assertTrue(metadata['reference_check_passed'])
                for sequence, row in enumerate(rows):
                    region = metadata['regions'][row['operand']]
                    self.assertEqual(int(row['sequence']), sequence)
                    self.assertLessEqual(region['base'], int(row['address'], 16))
                    self.assertLessEqual(int(row['address'], 16) + 4, region['base'] + region['size_bytes'])
                results.append(json.loads((path / 'result.json').read_text()))
                self.assertEqual(analyze(read_addresses(path / 'trace.csv', 'csv'))['accesses'], len(rows))
            self.assertEqual(results[0], results[1])

    def test_b_stream_has_expected_inner_loop_stride(self):
        with tempfile.TemporaryDirectory() as temporary:
            deltas = {}
            for order in ('ijk', 'ikj'):
                path = Path(temporary) / order
                generate(path, Config(1, 3, 4), order)
                with (path / 'trace.csv').open() as source:
                    addresses = [int(r['address'], 16) for r in csv.DictReader(source) if r['operand'] == 'B']
                deltas[order] = addresses[1] - addresses[0]
            self.assertEqual(deltas, {'ijk': 16, 'ikj': 4})

    def test_large_regions_do_not_overlap(self):
        regions = list(layout(Config(40, 40, 40)).values())
        for previous, current in zip(regions, regions[1:]):
            self.assertLessEqual(previous['base'] + previous['size_bytes'], current['base'])

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            Config(0, 4, 4)
        with self.assertRaises(ValueError):
            Config(element_size=8)


if __name__ == '__main__':
    unittest.main()
