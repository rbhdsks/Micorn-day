"""Paired measurements, explicit aggregation and predeclared selection rule."""
import csv,math
from collections import defaultdict
from pathlib import Path
VARIANTS=('none','next_line','stride','victim_buffer','global_buffer','region_buffer','context_feedback')
UPGRADES=('victim_buffer','global_buffer','region_buffer','context_feedback')
REQUIRED=('accesses','hits','misses','prefetch_issued','timely_useful','late_useful','unused_evicted','resident_unconsumed',
 'dram_reads','completion_cycles','quiescent_cycles','latency_sum','max_latency','offer_latency_sum','max_offer_latency','request_wait_cycles','total_compute_gap_cycles')
def read_measurement(path,expected_accesses,enabled):
 with Path(path).open() as f:rows=list(csv.DictReader(f))
 if len(rows)!=1 or any(k not in rows[0] for k in REQUIRED):raise ValueError('one complete measurement row required')
 row={k:int(v) for k,v in rows[0].items()}
 if any(v<0 for v in row.values()):raise ValueError('negative counter')
 if row['accesses']!=expected_accesses or row['hits']+row['misses']!=expected_accesses:raise ValueError('classification mismatch')
 if row['prefetch_issued']!=sum(row[k] for k in ['timely_useful','late_useful','unused_evicted','resident_unconsumed']):raise ValueError('prefetch fate mismatch')
 if not enabled and row['prefetch_issued']:raise ValueError('disabled speculation issued')
 if row['dram_reads']<row['prefetch_issued'] or row['completion_cycles']<=0 or row['quiescent_cycles']<row['completion_cycles']:raise ValueError('traffic/timing mismatch')
 for k in ['buffer_hits','predictions_suppressed','feedback_quality']:row.setdefault(k,0)
 if row['hits']+row['buffer_hits']>expected_accesses:raise ValueError('double-counted service hit')
 return row
def quantile(values,fraction):
 if not values or not 0<fraction<=1:raise ValueError('nonempty samples and fraction in(0,1] required')
 return sorted(values)[math.ceil(fraction*len(values))-1]
def validate_samples(path,row):
 with Path(path).open() as f:data=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
 if len(data)!=row['accesses'] or [r['request_index'] for r in data]!=list(range(len(data))):raise ValueError('sample count/order mismatch')
 for field,total,maximum in [('accept_latency','latency_sum','max_latency'),('offer_latency','offer_latency_sum','max_offer_latency')]:
  if sum(r[field] for r in data)!=row[total] or max(r[field] for r in data)!=row[maximum]:raise ValueError('sample/summary latency mismatch')
 if sum(r['request_wait'] for r in data)!=row['request_wait_cycles']:raise ValueError('sample waiting mismatch')
 return {'p50_offer_latency':quantile([r['offer_latency'] for r in data],.5),'p95_offer_latency':quantile([r['offer_latency'] for r in data],.95)}
def derive(records):
 grouped=defaultdict(dict)
 for row in records:
  if row['variant'] in grouped[row['case_id']]:raise ValueError('duplicate case/variant')
  grouped[row['case_id']][row['variant']]=row
 result=[]
 for case,modes in sorted(grouped.items()):
  if set(modes)!=set(VARIANTS):raise ValueError('incomplete matched variants: '+case)
  baseline=modes['none'];stride=modes['stride']
  for variant in VARIANTS:
   r=modes[variant];n=r['accesses'];issued=r['prefetch_issued']
   if n!=baseline['accesses']:raise ValueError('mismatched demands')
   metadata={k:r[k] for k in ['case_id','workload','family','split','source_kind','seed','gap_cycles','memory_latency','variant','index_bits']}
   result.append({**metadata,**{k:r[k] for k in ['accesses','hits','misses','buffer_hits']},
    'demand_hit_rate':r['hits']/n,'service_hit_rate':(r['hits']+r['buffer_hits'])/n,
    **{k:r[k] for k in ['prefetch_issued','timely_useful','late_useful','unused_evicted','resident_unconsumed']},
    'prefetch_consumption_accuracy':(r['timely_useful']+r['late_useful'])/issued if issued else '',
    'dram_reads':r['dram_reads'],'dram_bytes':16*r['dram_reads'],'dram_ratio':r['dram_reads']/baseline['dram_reads'],
    'completion_cycles':r['completion_cycles'],'quiescent_cycles':r['quiescent_cycles'],
    'speedup':baseline['completion_cycles']/r['completion_cycles'],'stride_speedup':stride['completion_cycles']/r['completion_cycles'],
    'mean_accept_latency':r['latency_sum']/n,'mean_offer_latency':r['offer_latency_sum']/n,
    **{k:r[k] for k in ['p50_offer_latency','p95_offer_latency','max_offer_latency','request_wait_cycles','total_compute_gap_cycles','predictions_suppressed','feedback_quality']}})
 return result
def geomean(values):
 if not values or any(x<=0 for x in values):raise ValueError('positive nonempty geometric mean required')
 return math.exp(sum(math.log(x) for x in values)/len(values))
def family_balanced(rows,key):
 grouped=defaultdict(list)
 for r in rows:grouped[r['family']].append(float(r[key]))
 return geomean([geomean(v) for v in grouped.values()])
def aggregate(rows,split):
 result=[]
 for variant in VARIANTS:
  group=[r for r in rows if r['split']==split and r['variant']==variant]
  if not group:continue
  worst=max(1/r['speedup'] for r in group)
  result.append({'split':split,'variant':variant,'cases':len(group),'families':len({r['family'] for r in group}),
   'family_balanced_speedup':family_balanced(group,'speedup'),'family_balanced_dram_ratio':family_balanced(group,'dram_ratio'),
   'case_geomean_speedup':geomean([r['speedup'] for r in group]),'worst_completion_ratio':worst,
   'p95_case_completion_ratio':quantile([1/r['speedup'] for r in group],.95),
   'slowdown_cases':sum(r['speedup']<1-1e-12 for r in group),'total_dram_reads':sum(r['dram_reads'] for r in group),
   'total_accesses':sum(r['accesses'] for r in group)})
 return result
def select(rows,budget=1.25):
 scores=aggregate(rows,'validation');eligible=[r for r in scores if r['variant'] in UPGRADES and r['family_balanced_dram_ratio']<=budget]
 order={v:i for i,v in enumerate(UPGRADES)}
 eligible.sort(key=lambda r:(-round(r['family_balanced_speedup'],12),order[r['variant']]))
 return {'selection_split':'validation','traffic_budget':budget,'candidate_variants':list(UPGRADES),
  'selection_rule':'maximum family-balanced geometric-mean completion speedup subject to family-balanced geometric-mean DRAM ratio <=1.25; ties rounded12decimals choose victim_buffer,global_buffer,region_buffer,context_feedback',
  'selected_variant':eligible[0]['variant'] if eligible else None,'validation_scores':scores,
  'thresholds_frozen':{'REGION_ENTRIES':4,'REGION_LINE_BITS':8,'PROBE_INTERVAL':16,'quality_bits':2,'quality_initial':2},
  'held_out_results_used_for_selection':False}
def pareto(scores):
 return [r['variant'] for r in scores if not any(
  q['family_balanced_speedup']>=r['family_balanced_speedup'] and q['family_balanced_dram_ratio']<=r['family_balanced_dram_ratio'] and
  (q['family_balanced_speedup']>r['family_balanced_speedup'] or q['family_balanced_dram_ratio']<r['family_balanced_dram_ratio']) for q in scores)]
def write_csv(path,rows):
 if not rows:raise ValueError('no rows')
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
