import csv
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from trace_io import MAX_GAP, TraceRow, read_trace, write_trace, write_mem
from generate_traces import filter_immutable_reads, generate, load_matmul_generator
from metrics import POLICIES, markdown_report, read_measurement, summarize
from run_benchmarks import invalidate_published_outputs, simulator_path, run


class TraceContractTests(unittest.TestCase):
    def test_roundtrip_maximum_word_and_gap(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'trace.csv';mem=Path(d)/'trace.mem'
            rows=[TraceRow(0,0),TraceRow(0xfffffffc,MAX_GAP)]
            write_trace(path,rows);write_mem(mem,rows)
            self.assertEqual(read_trace(path),rows)
            self.assertEqual(mem.read_text().splitlines(),['0000000000000000','fffffffc000186a0'])

    def test_reject_ambiguous_out_of_range_and_unaligned_addresses(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.csv'
            for address in ['1000','deadbeef','0x100000000','0x1001','-0x4','0X1000']:
                path.write_text(f'address,gap\n{address},0\n')
                with self.subTest(address=address),self.assertRaises(ValueError):read_trace(path)

    def test_reject_invalid_gap_header_empty_and_extra_columns(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.csv'
            texts=['address,gap\n','address,cycles\n0x1000,0\n',
                   'address,gap\n0x1000,-1\n','address,gap\n0x1000,1.0\n',
                   f'address,gap\n0x1000,{MAX_GAP+1}\n',
                   'address,gap\n0x1000,0,unexpected\n']
            for text in texts:
                path.write_text(text)
                with self.subTest(text=text),self.assertRaises(ValueError):read_trace(path)

    def test_validated_rows_reject_bool_or_negative_inputs(self):
        for args in [(True,0),(0,True),(-4,0),(0,-1)]:
            with self.subTest(args=args),self.assertRaises(ValueError):TraceRow(*args)


class MatmulBridgeTests(unittest.TestCase):
    def test_filter_preserves_only_immutable_ab_compute_reads_in_order(self):
        with tempfile.TemporaryDirectory() as d:
            module=load_matmul_generator();source=Path(d)/'source'
            metadata=module.generate(source,module.Config(m=2,k=3,n=4),'ikj')
            rows,excluded=filter_immutable_reads(source/'trace.csv',gap=7)
            with (source/'trace.csv').open() as file:
                records=list(csv.DictReader(file))
            expected=[int(r['address'],16) for r in records if r['phase']=='compute' and r['operation']=='R' and r['operand'] in ('A','B')]
            self.assertEqual([r.address for r in rows],expected)
            self.assertEqual(len(rows),2*2*3*4)
            self.assertEqual(excluded,len(records)-len(rows))
            self.assertTrue(all(r.gap==7 for r in rows))
            self.assertTrue(metadata['reference_check_passed'])
            c=metadata['regions']['C']
            self.assertTrue(all(not c['base']<=r.address<c['base']+c['size_bytes'] for r in rows))

    def test_generation_records_provenance_and_exact_checksums(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);manifest=generate(root)
            self.assertEqual(len(manifest['traces']),13)
            names={r['name']:r for r in manifest['traces']}
            self.assertEqual(names['pollution_return']['rows'],320)
            self.assertEqual(names['three_line_bursts']['rows'],192)
            for item in manifest['traces']:
                self.assertEqual(item['sha256'],hashlib.sha256((root/item['file']).read_bytes()).hexdigest())
                self.assertEqual(item['rows'],len(read_trace(root/item['file'])))
            item=names['modelled_matmul_ijk_ab_reads']
            self.assertEqual(item['rows'],512)
            self.assertIn('exclude C',item['filter'])
            self.assertIn('not captured',item['provenance'])
            self.assertEqual(item['source_sha256'],hashlib.sha256((root/item['source_file']).read_bytes()).hexdigest())


class MetricTests(unittest.TestCase):
    def fake(self,policy):
        return {'workload':'same_line','trace_kind':'synthetic_pattern','policy':policy,
                'accesses':4,'hits':3,'misses':1,'prefetch_issued':0,'timely_useful':0,'late_useful':0,
                'unused_evicted':0,'resident_unconsumed':0,'dram_reads':1,'completion_cycles':12,
                'quiescent_cycles':14,'latency_sum':20,'max_latency':17,
                'offer_latency_sum':20,'max_offer_latency':17,'request_wait_cycles':0,'total_compute_gap_cycles':0}

    def test_no_predictions_report_is_defined_without_stride_or_division(self):
        summaries=summarize([self.fake(p) for p in POLICIES])
        report=markdown_report(summaries,6,12)
        self.assertIn('N/A',report)
        self.assertEqual([r['speedup'] for r in summaries],[1,1,1])
        self.assertTrue(all(r['prefetch_consumption_accuracy']=='' for r in summaries))
        self.assertTrue(all(r['demand_hit_rate']==0.75 for r in summaries))

    def test_missing_or_duplicate_policy_is_rejected(self):
        with self.assertRaises(ValueError):summarize([self.fake('none')])
        with self.assertRaises(ValueError):summarize([self.fake(p) for p in POLICIES]+[self.fake('stride')])

    def test_invalid_prefetch_fate_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.csv';row=self.fake('stride');row.pop('workload');row.pop('trace_kind');row.pop('policy')
            row['prefetch_issued']=1
            with path.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerow(row)
            with self.assertRaisesRegex(ValueError,'do not conserve'):read_measurement(path,4,1)



class RunnerSafetyTests(unittest.TestCase):
    def test_whitespace_in_simulator_output_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'must not contain whitespace'):
            simulator_path(Path('build/path with spaces/trace.mem'))

    def test_failed_attempt_cannot_reuse_old_success_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            for name in ('summary.csv','report.md','provenance.json'):
                (output/name).write_text('old successful output')
            with self.assertRaisesRegex(ValueError, 'INDEX_BITS'):
                run(output,index_bits=0)
            self.assertFalse(any((output/name).exists() for name in ('summary.csv','report.md','provenance.json')))

if __name__=='__main__':unittest.main()
