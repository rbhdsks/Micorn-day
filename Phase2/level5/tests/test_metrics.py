import csv,tempfile,unittest
from pathlib import Path
from metrics import VARIANTS,aggregate,derive,family_balanced,geomean,pareto,quantile,read_measurement,select

def raw(variant):
 return {'case_id':'one','workload':'one','family':'one','split':'validation','source_kind':'unit','seed':11,'gap_cycles':0,'memory_latency':12,'variant':variant,'index_bits':6,
  'accesses':10,'hits':0,'misses':10,'buffer_hits':0,'prefetch_issued':0,'timely_useful':0,'late_useful':0,'unused_evicted':0,'resident_unconsumed':0,
  'dram_reads':10,'completion_cycles':100,'quiescent_cycles':102,'latency_sum':80,'max_latency':8,'offer_latency_sum':90,'max_offer_latency':9,
  'request_wait_cycles':10,'total_compute_gap_cycles':0,'p50_offer_latency':9,'p95_offer_latency':9,'predictions_suppressed':0,'feedback_quality':2}

class MetricsTests(unittest.TestCase):
 def test_geomean_and_family_balance_not_average_of_ratios(self):
  self.assertAlmostEqual(geomean([4,1]),2)
  self.assertAlmostEqual(family_balanced([{'family':'a','x':4},{'family':'b','x':1},{'family':'b','x':1}],'x'),2)
  with self.assertRaises(ValueError):geomean([0,1])
 def test_nearest_rank_percentiles(self):
  self.assertEqual(quantile(list(range(1,21)),.95),19)
  self.assertEqual(quantile([9,1,5],.5),5)
 def test_victim_buffer_hits_are_not_prefetch_accuracy(self):
  records=[raw(v) for v in VARIANTS]
  victim=next(r for r in records if r['variant']=='victim_buffer');victim.update(hits=2,misses=8,buffer_hits=4,dram_reads=4,completion_cycles=70)
  result=next(r for r in derive(records) if r['variant']=='victim_buffer')
  self.assertEqual(result['demand_hit_rate'],.2);self.assertEqual(result['service_hit_rate'],.6)
  self.assertEqual(result['prefetch_consumption_accuracy'],'');self.assertEqual(result['timely_useful'],0)
 def test_incomplete_pairs_rejected(self):
  with self.assertRaises(ValueError):derive([raw('none')])
 def test_selection_uses_validation_and_traffic_gate(self):
  rows=derive([raw(v) for v in VARIANTS])
  for r in rows:
   if r['variant']=='region_buffer':r.update(speedup=2,dram_ratio=1.3)
   if r['variant']=='global_buffer':r.update(speedup=1.5,dram_ratio=1.2)
  evaluation=[dict(r,split='held_out',speedup=100 if r['variant']=='context_feedback' else .1) for r in rows]
  self.assertEqual(select(rows+evaluation)['selected_variant'],'global_buffer')
 def test_no_feasible_upgrade_is_not_forced_winner(self):
  rows=derive([raw(v) for v in VARIANTS])
  for r in rows:
   if r['variant'] not in ['none','next_line','stride']:r['dram_ratio']=2
  self.assertIsNone(select(rows)['selected_variant'])
 def test_prefetch_fate_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d,'run.csv');r=raw('stride');r.pop('seed');r={k:v for k,v in r.items() if isinstance(v,int)};r['prefetch_issued']=1
   with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=r);w.writeheader();w.writerow(r)
   with self.assertRaises(ValueError):read_measurement(p,10,True)
 def test_pareto_retains_tradeoffs_and_removes_dominated(self):
  rows=[{'variant':'a','family_balanced_speedup':1.2,'family_balanced_dram_ratio':1.1},{'variant':'b','family_balanced_speedup':1.1,'family_balanced_dram_ratio':1.2},{'variant':'c','family_balanced_speedup':1,'family_balanced_dram_ratio':1}]
  self.assertEqual(pareto(rows),['a','c'])
if __name__=='__main__':unittest.main()
