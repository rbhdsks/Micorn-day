#!/usr/bin/env python3
"""Run seven matched RTL variants with validation-first frozen selection."""
from pathlib import Path
import argparse,hashlib,json,os,shlex,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'level1'))
from generate_suite import generate
from metrics import VARIANTS,read_measurement,validate_samples,derive,select,aggregate,pareto,write_csv
CONFIG={
 'none':{'baseline':True,'policy':1,'enabled':0},'next_line':{'baseline':True,'policy':2,'enabled':1},'stride':{'baseline':True,'policy':1,'enabled':1},
 'victim_buffer':{'baseline':False,'region':0,'feedback':0,'victim':1,'enabled':0},
 'global_buffer':{'baseline':False,'region':0,'feedback':0,'victim':0,'enabled':1},
 'region_buffer':{'baseline':False,'region':1,'feedback':0,'victim':0,'enabled':1},
 'context_feedback':{'baseline':False,'region':1,'feedback':1,'victim':0,'enabled':1}}
def relative(path):return os.path.relpath(Path(path).resolve(),REPO)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def execute(command,log,commands,expect_pass=False):
 completed=subprocess.run(command,cwd=REPO,text=True,capture_output=True)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(completed.stdout+completed.stderr)
 commands.append({'argv':command,'cwd':'repository root','log':relative(log),'exit_code':completed.returncode})
 if completed.returncode or expect_pass and 'PASS:' not in completed.stdout:raise RuntimeError(shlex.join(command)+'\n'+completed.stdout+completed.stderr)
 return completed
def source_hashes():
 paths=[*sorted((ROOT/'level4/rtl').glob('*.sv')),ROOT/'level4/tb/tb_trace_context.sv',*sorted((ROOT/'level5/scripts').glob('*.py')),
  *sorted((ROOT/'level5/bench').glob('*.sv')),*sorted((ROOT/'level1').glob('*.py')),*sorted((REPO/'Phase1/level4/rtl').glob('*.sv')),REPO/'Phase1/level4/tb/dram_model.sv',
  REPO/'Phase1/level5/scripts/generate_traces.py',REPO/'Phase1/level5/scripts/trace_io.py',REPO/'Phase1/level1/generate_matmul_trace.py',REPO/'Phase1/level5/results/reference/summary.csv']
 return {relative(p):digest(p) for p in paths}
def compile_binary(output,variant,latency,probe,commands):
 cfg=CONFIG[variant];tag=f'{variant}_l{latency}_p{probe}';binary=output/'binaries'/f'{tag}.vvp';binary.parent.mkdir(exist_ok=True)
 if cfg['baseline']:
  top='tb_trace_baseline';sources=[*sorted((REPO/'Phase1/level4/rtl').glob('*.sv')),REPO/'Phase1/level4/tb/dram_model.sv',ROOT/'level5/bench/tb_trace_baseline.sv']
  params=[f'-P{top}.PREFETCH_POLICY={cfg["policy"]}']
 else:
  top='tb_trace_context';sources=[*sorted((ROOT/'level4/rtl').glob('*.sv')),REPO/'Phase1/level4/rtl/stride_prefetcher.sv',REPO/'Phase1/level4/tb/dram_model.sv',ROOT/'level4/tb/tb_trace_context.sv']
  params=[f'-P{top}.REGION_ENABLE={cfg["region"]}',f'-P{top}.FEEDBACK_ENABLE={cfg["feedback"]}',f'-P{top}.VICTIM_ENABLE={cfg["victim"]}',f'-P{top}.PROBE_INTERVAL={probe}']
 cmd=shlex.split(os.environ.get('IVERILOG','iverilog'))+['-g2012','-Wall','-s',top,f'-P{top}.INDEX_BITS=6',f'-P{top}.LATENCY={latency}',*params,'-o',relative(binary),*[relative(p) for p in sources]]
 execute(cmd,output/'logs'/f'compile_{tag}.log',commands);return binary
def baseline_crosscheck(rows):
 with (REPO/'Phase1/level5/results/reference/summary.csv').open() as f:old=list(__import__('csv').DictReader(f))
 index={(r['workload'],r['policy']):r for r in old};checked=0
 for r in rows:
  if r['split']=='regression' and r['variant'] in ['none','next_line','stride']:
   reference=index[r['workload'],r['variant']]
   for key in ['accesses','hits','misses','prefetch_issued','timely_useful','late_useful','unused_evicted','resident_unconsumed','dram_reads','completion_cycles','quiescent_cycles']:
    if r[key]!=int(reference[key]):raise ValueError(f'Phase1-equivalence failure {r["case_id"]}/{r["variant"]}/{key}')
   checked+=1
 return checked
def run(output,download=False,no_corpus=False,sensitivity=True,only_split=None):
 output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
 for name in ['summary.csv','aggregates.csv','selection.json','evaluation.json','provenance.json']:
  p=output/name
  if p.exists():p.unlink()
 manifest=generate(output/'traces',ROOT/'build/data',download,not no_corpus);cases=manifest['cases']
 if only_split:cases=[c for c in cases if c['split']==only_split]
 commands=[];records=[];sensitivity_rows=[];versions={'python':sys.version.split()[0]};hashes=source_hashes()
 for tool in ['iverilog','vvp']:
  completed=execute(shlex.split(os.environ.get(tool.upper(),tool))+['-V'],output/'logs'/f'{tool}_version.log',commands)
  versions[tool]=(completed.stdout+completed.stderr).splitlines()[0]
 plan={'schema_version':1,'variants':CONFIG,'cases':len(cases),'expected_primary_runs':len(cases)*len(VARIANTS),
  'selection_candidates':['victim_buffer','global_buffer','region_buffer','context_feedback'],'selection_traffic_budget':1.25,
  'selection_objective':'family-balanced geometric mean completion speedup; choose using validation only',
  'thresholds_frozen':{'REGION_ENTRIES':4,'REGION_LINE_BITS':8,'PROBE_INTERVAL':16,'quality_bits':2,'quality_initial':2},
  'sensitivity':'validation only, intervals8and32; exploratory robustness only; never selects final thresholds',
  'source_sha256_before_execution':hashes,'manifest_sha256':digest(output/'traces/manifest.json')}
 (output/'predeclared_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 binaries={}
 def measure(case,variant,probe=16,suffix=''):
  key=(variant,case['memory_latency'],probe)
  if key not in binaries:binaries[key]=compile_binary(output,*key,commands)
  directory=output/('sensitivity_runs' if suffix else 'runs');directory.mkdir(exist_ok=True)
  stem=case['case_id']+'__'+variant+suffix
  raw=directory/(stem+'.csv');samples=output/'samples'/(stem+'.csv');samples.parent.mkdir(exist_ok=True)
  mem=output/'replay'/(case['case_id']+'.mem');mem.parent.mkdir(exist_ok=True)
  from trace_io import read_trace,write_mem
  write_mem(mem,read_trace(output/'traces'/case['file']))
  command=shlex.split(os.environ.get('VVP','vvp'))+[relative(binaries[key]),'+TRACE='+relative(mem),f'+COUNT={case["rows"]}',f'+PF={CONFIG[variant]["enabled"]}','+OUT='+relative(raw),'+SAMPLE_OUT='+relative(samples)]
  execute(command,raw.with_suffix('.log'),commands,True)
  r=read_measurement(raw,case['rows'],CONFIG[variant]['enabled'])
  if r['index_bits']!=6 or r['memory_latency']!=case['memory_latency']:raise ValueError('configuration mismatch')
  quantiles=validate_samples(samples,r)
  metadata={k:case[k] for k in ['case_id','workload','family','split','source_kind','seed','gap_cycles','memory_latency']}
  record={**metadata,'variant':variant,**r,**quantiles}
  if suffix:record['probe_interval']=probe
  print(f'PASS {case["case_id"]:36} {variant:18} p{probe} cycles={r["completion_cycles"]:8} reads={r["dram_reads"]:5}',flush=True)
  return record
 validation=[c for c in cases if c['split']=='validation'];remaining=[c for c in cases if c['split']!='validation']
 for case in validation:
  for variant in VARIANTS:records.append(measure(case,variant))
 if validation:
  selection=select(derive(records));selection['predeclared_plan_sha256']=digest(output/'predeclared_plan.json')
  selection['stage']='sealed before any held-out/regression/stress commands'
  (output/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
  selection_digest=digest(output/'selection.json')
  if sensitivity:
   for case in validation:
    for probe in [8,32]:sensitivity_rows.append(measure(case,'context_feedback',probe,f'_p{probe}'))
 else:selection_digest=None
 for case in remaining:
  for variant in VARIANTS:records.append(measure(case,variant))
 summary=derive(records);crosschecked=baseline_crosscheck(summary)
 if source_hashes()!=hashes:raise RuntimeError('sources changed while benchmark was running; rerun before publishing')
 write_csv(output/'summary.csv',summary)
 scores=[r for split in ['validation','held_out','regression','stress'] for r in aggregate(summary,split)]
 write_csv(output/'aggregates.csv',scores)
 if sensitivity_rows:
  # Keep raw counters alongside exact fixed probe interval; no selection here.
  write_csv(output/'sensitivity.csv',sensitivity_rows)
 evaluation={'primary_runs':len(summary),'sensitivity_runs':len(sensitivity_rows),'checked_responses':sum(r['accesses'] for r in records+sensitivity_rows),
  'baseline_reference_equivalence_checks':crosschecked,'selection_sha256_before_held_out':selection_digest,
  'selection_sha256_after_held_out':digest(output/'selection.json') if selection_digest else None,
  'pareto_by_split':{split:pareto([r for r in scores if r['split']==split]) for split in ['validation','held_out','regression','stress']},
  'statistical_scope':'exact outcomes for finite declared suite; no real-workload confidence interval; seeds change kernel shape/layout and synthetic indices, gaps are correlated replays'}
 (output/'evaluation.json').write_text(json.dumps(evaluation,indent=2)+'\n')
 provenance={'schema_version':1,'measurement_kind':'self-checking RTL subsystem simulation; not physical DRAM or end-to-end inference',
  'baseline_commit':'7851de10f6311847ded4ff04640c678ba3999437','tool_versions':versions,'source_sha256':hashes,
  'manifest_sha256':digest(output/'traces/manifest.json'),'commands':commands,
  'parameters':{'INDEX_BITS':6,'LINE_BYTES':16,'REGION_ENTRIES':4,'REGION_LINE_BITS':8,'PROBE_INTERVAL':16,'variants':CONFIG,
   'driver':'serial demand with post-response gap and request-index modulo4 consumer stalls','memory':'Phase1 deterministic ready/stall/jitter/countdown model'},**evaluation}
 (output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print('Saved',len(summary),'primary and',len(sensitivity_rows),'sensitivity runs;',evaluation['checked_responses'],'checked responses')
 return summary
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/benchmarks');p.add_argument('--download-corpus',action='store_true');p.add_argument('--no-corpus',action='store_true');p.add_argument('--no-sensitivity',action='store_true');p.add_argument('--only-split',choices=['validation','held_out','regression','stress']);a=p.parse_args()
 try:run(a.output,a.download_corpus,a.no_corpus,not a.no_sensitivity,a.only_split)
 except (ValueError,RuntimeError,OSError) as exc:p.exit(1,'ERROR: '+str(exc)+'\n')
if __name__=='__main__':main()
