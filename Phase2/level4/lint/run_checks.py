#!/usr/bin/env python3
"""Independent memory/scoreboard, strict lint and concurrent assertion execution."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[3];B=R/'Phase2/build/independent';B.mkdir(parents=True,exist_ok=True)
RTL=[*sorted((R/'Phase2/level4/rtl').glob('*.sv')),R/'Phase1/level4/rtl/stride_prefetcher.sv']
TEST=R/'Phase2/level4/audit_tests/tb_independent.sv'
CONFIG={'global_buffer':(0,0,0),'region_buffer':(1,0,0),'context_feedback':(1,1,0),'victim_buffer':(0,0,1)}
def run(cmd,name,expect=False):
 p=subprocess.run(cmd,cwd=R,text=True,capture_output=True,timeout=240)
 out=p.stdout+p.stderr;(B/(name+'.log')).write_text(out);p.check_returncode()
 if expect and 'PASS:' not in out:raise RuntimeError(name+' missing PASS')
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--no-verilator',action='store_true');a=p.parse_args();records=[]
 for name,cfg in CONFIG.items():
  params=dict(zip(['REGION_ENABLE','FEEDBACK_ENABLE','VICTIM_ENABLE'],cfg))
  run(['verilator','--lint-only','--timing','-Wall',str(R/'Phase2/level4/lint/intentional.vlt'),'--top-module','ai_cache_context',*[f'-G{k}={v}' for k,v in params.items()],*map(str,RTL)],name+'_lint')
  for seed in [0x93abc217,0x1234fabe]:
   tag=f'{name}_{seed:08x}';binary=B/(tag+'.vvp')
   run(['iverilog','-g2012','-Wall','-s','tb_independent',*[f'-Ptb_independent.{k}={v}' for k,v in {**params,'SEED':seed}.items()],'-o',str(binary),*map(str,RTL),str(TEST)],tag+'_compile')
   output=run(['vvp',str(binary),'+TELEMETRY='+str(B/(tag+'_wave.csv'))],tag,True)
   import re
   m=re.search(r'requests=(\d+) checked=(\d+) canceled=(\d+)',output)
   records.append({'variant':name,'seed':seed,'simulator':'Icarus','accepted':int(m[1]),'checked':int(m[2]),'reset_canceled':int(m[3]),'pass_line':next(l for l in output.splitlines() if l.startswith('PASS:'))})
   print('PASS',tag,flush=True)
 if not a.no_verilator:
  directory=B/'verilated';cmd=['verilator','--binary','--timing','--assert','-Wno-fatal','--top-module','tb_independent','--Mdir',str(directory)]
  # Some macOS CLT installations omit libc++ from the driver's default search.
  if sys.platform=='darwin':
   sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
   cmd+=['-CFLAGS','-isystem '+sdk+'/usr/include/c++/v1']
  run(cmd+list(map(str,RTL))+[str(TEST),str(R/'Phase2/level4/audit_tests/context_sva.sv')],'verilator_build')
  output=run([str(directory/'Vtb_independent')],'verilator_assertions',True)
  import re
  m=re.search(r'requests=(\d+) checked=(\d+) canceled=(\d+)',output)
  records.append({'variant':'context_feedback','seed':0x93abc217,'simulator':'Verilator with12concurrent properties','accepted':int(m[1]),'checked':int(m[2]),'reset_canceled':int(m[3]),'pass_line':next(l for l in output.splitlines() if l.startswith('PASS:'))})
 files=[*RTL,TEST,R/'Phase2/level4/audit_tests/context_sva.sv',R/'Phase2/level4/lint/intentional.vlt',Path(__file__)]
 result={'status':'pass','records':records,'checked_responses':sum(x['checked'] for x in records),'reset_canceled_demands':sum(x['reset_canceled'] for x in records),'strict_lint_configurations':4,'reviewed_waivers':['cpu_req_addr[1:0] unused because interface accepts aligned words only; importer/scoreboards assert alignment'],
 'source_sha256':{str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files},'limits':['Finite simulation, not formal proof','Simulator-dependent driver scheduling means correctness checks, not cycle equivalence between tools','Reset is shared with memory and cancels its outstanding epoch']}
 (B/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS independent checked responses',result['checked_responses'])
if __name__=='__main__':main()
