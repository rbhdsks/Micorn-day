#!/usr/bin/env python3
"""Second-pass arithmetic, paired inputs, source integrity and selection audit.

Intentionally does not import the benchmark's metrics or runner modules.
"""
from pathlib import Path
from collections import defaultdict
import argparse,csv,hashlib,json,math
R=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',type=Path,default=R/'Phase2/build/benchmarks');a=p.parse_args();b=a.reference
 def read(name):return list(csv.DictReader((b/name).open()))
 rows=read('summary.csv');pairs=defaultdict(dict);errors=[]
 def require(x,s):
  if not x:errors.append(s)
 def close(x,y):return math.isclose(float(x),float(y),rel_tol=1e-12,abs_tol=1e-12)
 for r in rows:pairs[r['case_id']][r['variant']]=r
 variants=['none','next_line','stride','victim_buffer','global_buffer','region_buffer','context_feedback']
 checked=0
 for case,group in pairs.items():
  require(set(group)==set(variants),case+' variant completeness');base=group['none']
  for v,r in group.items():
   n=int(r['accesses']);h=int(r['hits']);m=int(r['misses']);buf=int(r['buffer_hits'])
   require(h+m==n and 0<=buf<=m,case+'/'+v+' classification')
   require(close(r['demand_hit_rate'],h/n) and close(r['service_hit_rate'],(h+buf)/n),case+'/'+v+' hit formulas')
   require(close(r['speedup'],int(base['completion_cycles'])/int(r['completion_cycles'])),case+'/'+v+' speedup')
   require(close(r['dram_ratio'],int(r['dram_reads'])/int(base['dram_reads'])),case+'/'+v+' traffic')
   require(int(r['dram_bytes'])==16*int(r['dram_reads']),case+'/'+v+' transfer bytes')
   require(int(r['prefetch_issued'])==sum(int(r[k]) for k in ['timely_useful','late_useful','unused_evicted','resident_unconsumed']),case+'/'+v+' fates')
   require(int(r['quiescent_cycles'])>=int(r['completion_cycles']),case+'/'+v+' drain')
   for k in ['accesses','index_bits','memory_latency','gap_cycles','total_compute_gap_cycles']:require(r[k]==base[k],case+'/'+v+' paired '+k)
   raw=list(csv.DictReader((b/'runs'/f'{case}__{v}.csv').open()))
   require(len(raw)==1,case+'/'+v+' raw row count')
   for k in ['accesses','hits','misses','completion_cycles','dram_reads','prefetch_issued']:require(raw[0][k]==r[k],case+'/'+v+' raw '+k)
   samplepath=b/'samples'/f'{case}__{v}.csv'
   if samplepath.exists():
    samples=list(csv.DictReader(samplepath.open()));require(len(samples)==n,case+'/'+v+' sample count')
    offered=sorted(int(x['offer_latency']) for x in samples)
    require(int(r['p95_offer_latency'])==offered[math.ceil(.95*n)-1],case+'/'+v+' nearest-rank p95')
   checked+=n
 aggregates=read('aggregates.csv')
 def balanced(g,key):
  fam=defaultdict(list)
  for r in g:fam[r['family']].append(math.log(float(r[key])))
  return math.exp(sum(sum(xs)/len(xs) for xs in fam.values())/len(fam))
 for q in aggregates:
  g=[r for r in rows if r['split']==q['split'] and r['variant']==q['variant']]
  for src,dst in [('speedup','family_balanced_speedup'),('dram_ratio','family_balanced_dram_ratio')]:require(close(q[dst],balanced(g,src)),q['split']+'/'+q['variant']+' '+dst)
 selection=json.loads((b/'selection.json').read_text());order=['victim_buffer','global_buffer','region_buffer','context_feedback']
 eligible=[q for q in aggregates if q['split']=='validation' and q['variant'] in order and float(q['family_balanced_dram_ratio'])<=selection['traffic_budget']]
 eligible.sort(key=lambda q:(-round(float(q['family_balanced_speedup']),12),order.index(q['variant'])))
 require(selection['selected_variant']==(eligible[0]['variant'] if eligible else None),'validation selection')
 evidence=json.loads((b/'evaluation.json').read_text());require(evidence['selection_sha256_before_held_out']==evidence['selection_sha256_after_held_out']==hashlib.sha256((b/'selection.json').read_bytes()).hexdigest(),'selection seal')
 prov=json.loads((b/'provenance.json').read_text())
 for path,sha in prov['source_sha256'].items():require(hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,'source hash '+path)
 manifest=json.loads((b/'traces/manifest.json').read_text())
 for c in manifest['cases']:require(hashlib.sha256((b/'traces'/c['file']).read_bytes()).hexdigest()==c['sha256'],'trace hash '+c['case_id'])
 result={'status':'pass' if not errors else 'fail','primary_rows':len(rows),'matched_cases':len(pairs),'primary_checked_responses':checked,'aggregate_rows':len(aggregates),'selection':selection['selected_variant'],'errors':errors,
 'independence':'Recomputed without importing benchmark metrics/runner modules','limits':['This validates finite-suite arithmetic and integrity, not real application representativeness','Selection timestamp ordering follows retained runner command provenance; a matching seal alone is not an externally notarized experiment']}
 out=R/'Phase2/audit/results_second_pass.json';out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));require(not errors,'audit failed')
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
