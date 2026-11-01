#!/usr/bin/env python3
"""Compile/run Phase2 verification; check subprocesses before recording evidence."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, time
ROOT=Path(__file__).resolve().parents[2]
LEVEL=ROOT/'Phase2/level4'
BUILD=ROOT/'Phase2/build/verification'
VARIANTS={
 'global_buffer':{'REGION_ENABLE':0,'FEEDBACK_ENABLE':0},
 'region_buffer':{'REGION_ENABLE':1,'FEEDBACK_ENABLE':0},
 'context_feedback':{'REGION_ENABLE':1,'FEEDBACK_ENABLE':1},
 'victim_buffer':{'REGION_ENABLE':0,'FEEDBACK_ENABLE':0,'VICTIM_ENABLE':1},
}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--quick',action='store_true',help='Run only one context seed; full suite is the sign-off reference')
 args=parser.parse_args();BUILD.mkdir(parents=True,exist_ok=True)
 iv=os.environ.get('IVERILOG','iverilog');vvp=os.environ.get('VVP','vvp')
 rtl=[ROOT/'Phase1/level4/rtl/stride_prefetcher.sv',*sorted((LEVEL/'rtl').glob('*.sv'))]
 support=[ROOT/'Phase1/level4/tb/dram_model.sv',LEVEL/'tb/context_protocol_monitor.sv']
 cases=[]
 for top in ['tb_region_predictor','tb_context_directed','tb_victim_directed','tb_context_nonpreemptible']:
  cases.append((top,'directed',{},[LEVEL/f'tb/{top}.sv']))
 for name,params in VARIANTS.items():
  if args.quick and name!='context_feedback':continue
  for seed in ([0x4d2d3f97] if args.quick else [0x4d2d3f97,0x91e10da5]):
   for top in ['tb_context_stress','tb_context_adversarial']:
    cases.append((top,f'{name}_{seed:08x}',dict(params,SEED=seed),[LEVEL/f'tb/{top}.sv']))
 records=[]
 for top,label,params,tests in cases:
  stem=f'{top}_{label}';binary=BUILD/f'{stem}.vvp'
  cmd=[iv,'-g2012','-Wall','-s',top,*[f'-P{top}.{k}={v}' for k,v in params.items()],'-o',str(binary),*map(str,rtl+support+tests)]
  start=time.monotonic();compile_run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=90)
  (BUILD/f'{stem}.compile.log').write_text(compile_run.stdout+compile_run.stderr)
  compile_run.check_returncode()
  run=subprocess.run([vvp,str(binary)],cwd=ROOT,capture_output=True,text=True,timeout=180)
  output=run.stdout+run.stderr;(BUILD/f'{stem}.log').write_text(output);run.check_returncode()
  if 'PASS:' not in output:raise RuntimeError(f'missing PASS marker: {stem}')
  response_count=10000 if 'adversarial' in top else 2000 if 'stress' in top else 23 if top=='tb_context_directed' else 13 if top=='tb_victim_directed' else 3 if top=='tb_context_nonpreemptible' else 0
  records.append({'top':top,'configuration':label,'parameters':params,'checked_responses':response_count,'elapsed_seconds':round(time.monotonic()-start,3),'pass_line':next(x for x in output.splitlines() if x.startswith('PASS:'))})
  print(label,top,records[-1]['pass_line'],flush=True)
 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*rtl,*support,*sorted((LEVEL/'tb').glob('*.sv'))]}
 result={'status':'pass','suite':'quick' if args.quick else 'full','seed_count':1 if args.quick else 2,'cases':records,'checked_responses':sum(x['checked_responses'] for x in records),'source_sha256':sources,'limits':['Bounded simulation, not formal proof or coverage closure','Counters are32bit and tests do not cover wraparound','Shared reset flushes both cache and memory; stale external responses unsupported']}
 (BUILD/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS',len(records),'runs;',result['checked_responses'],'checked demand responses')
if __name__=='__main__':main()
