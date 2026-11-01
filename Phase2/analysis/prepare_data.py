#!/usr/bin/env python3
"""Create transparent numeric MATLAB/Octave inputs from exact retained RTL rows."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
R=Path(__file__).resolve().parents[2];P=R/'Phase2'
VARIANTS=['none','next_line','stride','victim_buffer','global_buffer','region_buffer','context_feedback']
FIELDS=['speedup','dram_ratio','completion_cycles','dram_reads','demand_hit_rate','service_hit_rate','prefetch_issued','timely_useful','late_useful','unused_evicted','resident_unconsumed','mean_offer_latency','p50_offer_latency','p95_offer_latency','predictions_suppressed']
def main():
 default=P/'build/benchmarks' if (P/'build/benchmarks/summary.csv').exists() else P/'level5/results/reference'
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',type=Path,default=default);a=p.parse_args()
 rows=list(csv.DictReader((a.reference/'summary.csv').open()));cases=sorted({r['case_id'] for r in rows});g={(r['case_id'],r['variant']):r for r in rows}
 if len(rows)!=len(cases)*len(VARIANTS):raise ValueError('Incomplete matched matrix')
 out=P/'analysis/data';out.mkdir(parents=True,exist_ok=True)
 for field in FIELDS:
  with (out/(field+'.csv')).open('w') as f:
   for case in cases:f.write(','.join(g[case,v][field] for v in VARIANTS)+'\n')
 families=sorted({r['family'] for r in rows});splits=['validation','held_out','regression','stress']
 meta=[]
 for case in cases:
  r=g[case,'none'];meta.append([splits.index(r['split'])+1,families.index(r['family'])+1,int(r['accesses']),int(r['memory_latency']),int(r['gap_cycles']),int(r['seed']) if r['seed'] else -1])
 (out/'meta.csv').write_text(''.join(','.join(map(str,row))+'\n' for row in meta))
 for name,labels in [('cases',cases),('variants',VARIANTS),('families',families),('splits',splits)]: (out/(name+'.txt')).write_text('\n'.join(labels)+'\n')
 # Causal recovery and FSM traces remain actual simulation observations.
 for case in ['legacy_pollution_return','legacy_interleaved_conflicting','legacy_three_line_bursts']:
  for v in ['region_buffer','context_feedback']:
   path=a.reference/'samples'/f'{case}__{v}.csv'
   if path.exists():shutil.copyfile(path,out/(case+'__'+v+'.csv'))
 wave=P/'build/independent/context_feedback_93abc217_wave.csv'
 if wave.exists():shutil.copyfile(wave,out/'fsm_wave.csv')
 sens=list(csv.DictReader((a.reference/'sensitivity.csv').open()));values=[]
 for case in cases:
  if g[case,'none']['split']!='validation':continue
  base=float(g[case,'none']['completion_cycles']);db=float(g[case,'none']['dram_reads'])
  for probe in [8,16,32]:
   row=g[case,'context_feedback'] if probe==16 else next(r for r in sens if r['case_id']==case and int(r['probe_interval'])==probe)
   values.append([cases.index(case)+1,probe,base/float(row['completion_cycles']),float(row['dram_reads'])/db])
 (out/'probe_sensitivity.csv').write_text(''.join(','.join(map(str,r))+'\n' for r in values))
 synth=P/'build/synthesis/summary.json'
 if not synth.exists():synth=P/'level4/reference/synthesis.json'
 if synth.exists():
  data=json.loads(synth.read_text());cost=[]
  for v in ['stride','victim_buffer','global_buffer','region_buffer','context_feedback']:
   cost.append([next(r['generic_cells'] for r in data['measurements'] if r['variant']==v and r['view']==view) for view in ['functional','instrumented']])
  (out/'generic_cells.csv').write_text(''.join(','.join(map(str,r))+'\n' for r in cost))
 manifest={'source':str((a.reference/'summary.csv').relative_to(P)),'source_sha256':hashlib.sha256((a.reference/'summary.csv').read_bytes()).hexdigest(),
  'matrix_rows':'cases.txt order','matrix_columns':'variants.txt order','meta_columns':['split1based','family1based','accesses','memory_latency','gap_cycles','seed_or_minus1'],
  'evidence':'measured RTL values and explicitly labelled analytical transforms; no inferred energy, DRAM bandwidth or application execution speedup'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Prepared',len(cases),'matched cases and',len(FIELDS),'numeric matrices')
if __name__=='__main__':main()
