import csv
from pathlib import Path
import sys
import tempfile
import unittest

LEVEL2 = Path(__file__).resolve().parents[1]
PHASE1 = LEVEL2.parent
sys.path.insert(0, str(LEVEL2))
from cache_model import DirectMappedCache, read_addresses, simulate, word_at


class CacheModelTests(unittest.TestCase):
    def test_all_words_share_one_fill_and_return_selected_word(self):
        model = DirectMappedCache()
        events = [model.read(0x1230 + offset) for offset in (0, 4, 8, 12)]
        self.assertEqual([e['hit'] for e in events], [False, True, True, True])
        self.assertEqual([e['data'] for e in events], [word_at(0x1230+i*4) for i in range(4)])
        self.assertEqual((model.hits, model.misses), (3, 1))

    def test_direct_map_conflict_preserves_full_identity(self):
        model = DirectMappedCache()
        events = [model.read(address) for address in (0x1000, 0x1400, 0x1000)]
        self.assertTrue(all(e['index'] == 0 and not e['hit'] for e in events))
        self.assertEqual([e['evicted_line_identity'] for e in events], [None, 0x100, 0x140])
        self.assertEqual(events[-1]['data'], word_at(0x1000))

    def test_zero_line_is_a_valid_resident_identity(self):
        model = DirectMappedCache(index_bits=1)
        self.assertFalse(model.read(0)['hit'])
        self.assertTrue(model.read(4)['hit'])
        self.assertEqual(model.read(32)['evicted_line_identity'], 0)

    def test_decode_and_top_of_address_space(self):
        model = DirectMappedCache()
        self.assertEqual(model.decode(0x1234), {'address':0x1234, 'line_identity':0x123,
            'index':35, 'conventional_tag':4, 'word_offset':1, 'aligned_line_address':0x1230})
        event = model.read(0xfffffffc)
        self.assertEqual((event['line_identity'], event['index'], event['word_offset']), (0xfffffff,63,3))
        self.assertEqual(event['data'], word_at(0xfffffffc))

    def test_reset_flushes_data_identity_and_counters(self):
        model = DirectMappedCache()
        model.read(0x1000)
        model.read(0x1000)
        model.reset()
        self.assertEqual((model.accesses, model.hits, model.misses), (0,0,0))
        self.assertIsNone(model.summary()['demand_hit_rate'])
        self.assertFalse(model.read(0x1000)['hit'])

    def test_invalid_geometry_addresses_and_empty_input(self):
        for bits in (0,13,True,2.0):
            with self.assertRaises(ValueError): DirectMappedCache(bits)
        for address in (-4,2,0x100000000,True,4.0):
            with self.assertRaises(ValueError): DirectMappedCache().read(address)
        with self.assertRaises(ValueError): simulate([])

    def test_strict_trace_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'trace.csv'
            path.write_text('address,gap\n0x00001000,20\n0x00001004,0\n')
            self.assertEqual(read_addresses(path), [0x1000,0x1004])
            for bad in ('address,gap\n1000,0\n','address,gap\n0x1002,0\n',
                        'address,gap\n0x1000,-1\n','address,gap\n0x1000,100001\n',
                        'address,gap\n','address,gap,operation\n0x1000,0,R\n'):
                path.write_text(bad)
                with self.assertRaises(ValueError): read_addresses(path)

    def test_all_recorded_no_prefetch_rtl_counts_match_untimed_model(self):
        # With no speculation and serialized demand accesses, instantaneous refill
        # preserves the same residency order as RTL. This compares counts, not cycles.
        script_dir = PHASE1/'level5/scripts'
        sys.path.insert(0, str(script_dir))
        try:
            from generate_traces import generate
            with tempfile.TemporaryDirectory() as temporary:
                destination=Path(temporary)
                manifest=generate(destination)
                with (PHASE1/'level5/results/reference/summary.csv').open() as source:
                    baseline={row['workload']:row for row in csv.DictReader(source) if row['policy']=='none'}
                self.assertEqual(len(manifest['traces']),13)
                for description in manifest['traces']:
                    with self.subTest(trace=description['name']):
                        actual=simulate(read_addresses(destination/description['file']))['summary']
                        expected=baseline[description['name']]
                        self.assertEqual(actual['accesses'],int(expected['accesses']))
                        self.assertEqual(actual['hits'],int(expected['hits']))
                        self.assertEqual(actual['misses'],int(expected['misses']))
                        self.assertEqual(actual['demand_dram_reads'],int(expected['dram_reads']))
        finally:
            sys.path.remove(str(script_dir))


if __name__ == '__main__':
    unittest.main()
