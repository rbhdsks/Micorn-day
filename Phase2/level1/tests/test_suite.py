import json,tempfile,unittest
from pathlib import Path
from generate_suite import kernel,stress_cases,corpus_embedding
from fetch_corpus import load

class KernelTests(unittest.TestCase):
 def test_complete_numeric_kernels_all_declared_shapes(self):
  for kind in ['gemm_tiled','conv1d','depthwise1d','embedding_hot']:
   for seed in [11,101,202]:
    with self.subTest(kind=kind,seed=seed):
     addresses,metadata=kernel(kind,seed)
     self.assertTrue(metadata['numeric_reference_passed']);self.assertGreater(len(addresses),500)
     self.assertTrue(all(0<=a<=0xffffffff and a%4==0 for a in addresses))
     config=metadata['config']
     if kind=='gemm_tiled':self.assertEqual(len(addresses),2*config['m']*config['n']*config['k'])
     if kind=='conv1d':self.assertEqual(len(addresses),2*config['output_channels']*(config['length']-config['kernel_width']+1)*config['input_channels']*config['kernel_width'])
 def test_reproducible_seed_and_geometry_variation(self):
  self.assertEqual(kernel('gemm_tiled',11),kernel('gemm_tiled',11))
  self.assertNotEqual(kernel('gemm_tiled',11)[0],kernel('gemm_tiled',101)[0])
 def test_twelve_boundaries_and_feedback_coupling_probes(self):
  cases=stress_cases();self.assertEqual(len(cases),12)
  self.assertEqual({name for name,_,_,_ in cases},{'boundary_crossing','same_region_interleave','mixed_regions'})
  self.assertEqual({(gap,latency) for _,_,gap,latency in cases},{(0,0),(24,0),(0,48),(24,48)})
 def test_corpus_mapper_repetition_and_no_learned_vocab(self):
  addresses,m=corpus_embedding({'text':'alpha beta alpha'})
  self.assertEqual(addresses[:8],addresses[16:24]);self.assertNotEqual(addresses[:8],addresses[8:16])
  self.assertEqual(m['tokens'],3);self.assertEqual(m['unique_tokens'],2);self.assertTrue(m['numeric_reference_passed'])
 def test_corpus_requires_explicit_fetch_or_verified_snapshot(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileNotFoundError):load(d,False)
   Path(d,'wikitext_train.json').write_text(json.dumps({'rows':[{'row':{'text':'tampered'}}],'num_rows_total':1}))
   with self.assertRaises(ValueError):load(d,False)
if __name__=='__main__':unittest.main()
