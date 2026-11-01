#!/usr/bin/env python3
"""Create portable, standard-Python starting notebooks for Levels 3-5 and CDM."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DISCOVERY='''from pathlib import Path
import sys, json, csv, subprocess
cwd=Path.cwd().resolve()
ROOT=next(p for b in [cwd,*cwd.parents] for p in [b,b/'Phase1'] if (p/'level4/rtl/ai_cache.sv').is_file())
print('Phase 1 source tree located')'''
def notebook(path,title,sections):
    cells=[]
    for kind,source in [('markdown',title),('code',DISCOVERY),*sections]:
        cell={'cell_type':kind,'id':hashlib.sha256(source.encode()).hexdigest()[:12],'metadata':{},'source':source.splitlines(True)}
        if kind=='code':cell.update(execution_count=None,outputs=[])
        cells.append(cell)
    path.write_text(json.dumps({'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.10'}},'nbformat':4,'nbformat_minor':5},indent=1)+'\n')

def main():
    notebook(ROOT/'level3/prefetch_walkthrough.ipynb','# Level 3 Prefetch decisions\n\nTrace predictor state without confusing it with memory timing.',[
      ('markdown','## Repeated deltas\nThe third distinct line is enough to propose one stride ahead.'),
      ('code',"sys.path.insert(0,str(ROOT/'level3'))\nfrom explain_prefetch import walk\nfor row in walk([100,100,104,108,112]):\n    print(row['line'], row['action'], row['after']['confidence'], row['candidate'])"),
      ('markdown','## Reverse and boundary cases'),
      ('code',"print([(r['line'],r['candidate']) for r in walk([30,20,10,0])])\nprint([(r['line'],r['candidate']) for r in walk([100,100,104,108],'next_line')])"),
      ('markdown','## Continue with RTL\nA candidate is advisory. Cache residency, memory service and pending demand decide whether it is useful. See Level 4 and the measured Level 5 report.')])
    notebook(ROOT/'level4/rtl_walkthrough.ipynb','# Level 4 RTL and verification\n\nRead the controller, then execute its actual tests. Requires Icarus Verilog and VVP.',[
      ('markdown','## Cache controller\nIDLE chooses demand first. SEND holds a request through backpressure. WAIT fills a line. Selected speculation is nonpreemptible.'),
      ('code',"source=(ROOT/'level4/rtl/ai_cache.sv').read_text().splitlines()\nprint('\\n'.join(f'{i+1:3} {line}' for i,line in enumerate(source) if 'assign ' in line or 'SEND:' in line or 'WAIT:' in line or 'IDLE:' in line))"),
      ('markdown','## Run actual data and protocol checks'),
      ('code',"run=subprocess.run(['make','rtl-test'],cwd=ROOT,text=True,capture_output=True)\nprint('\\n'.join(line for line in (run.stdout+run.stderr).splitlines() if 'PASS:' in line))\nif run.returncode: raise RuntimeError(run.stdout+run.stderr)\nprint('All RTL verification commands passed')"),
      ('markdown','## Synthesis evidence\nGeneric cells describe a tool mapping, not physical area, timing closure or an FPGA board test.'),
      ('code',"synthesis=json.loads((ROOT/'level4/synth/reference/summary.json').read_text())\nfor row in synthesis['runs']:print(row['policy'],row['generic_cells'],'generic cells;',row['check_problems'],'CHECK problems')")])
    notebook(ROOT/'level5/results_walkthrough.ipynb','# Level 5 Measured comparison\n\nInspect the retained RTL evidence and replay one workload with identical geometry.',[
      ('code',"with (ROOT/'level5/results/reference/summary.csv').open() as f: rows=list(csv.DictReader(f))\nfor r in rows:\n    if r['workload'] in ['column_stride','pollution_return','modelled_matmul_ijk_ab_reads']:\n        print(r['workload'],r['policy'],'cycles=',r['completion_cycles'],'speedup=',round(float(r['speedup']),3),'DRAM=',r['dram_reads'])"),
      ('markdown','## Correct evaluation\nDemand hit rate = hits / accepted demand accesses. Speedup = no-prefetch completion cycles / policy completion cycles. A late prediction can shorten a miss without creating a hit.'),
      ('code',"cmd=[sys.executable,'level5/scripts/run_benchmarks.py','--output','build/notebooks/level5','--workload','column_stride']\nrun=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)\nprint(run.stdout)\nif run.returncode:raise RuntimeError(run.stderr)"),
      ('markdown','## Interpret negative cases\nPollution causes additional demand misses. Filtered matrix A/B traces show no stride gain. Preserve these results when developing Phase 2.')])
    notebook(ROOT/'research/cdm/cdm_walkthrough.ipynb','# Low rank CDM research\n\nReproduce the supplied notes arithmetic. This model is separate from implemented cache RTL.',[
      ('code',"sys.path.insert(0,str(ROOT/'research/cdm'))\nfrom cdm_reference import FACTORS,probabilities,evaluate\nfor r in evaluate():print('rank',r['rank'],'mean initial-factor NLL',round(r['mean_nll'],6))"),
      ('markdown','## Diagonal exclusion\nOnly other alternatives in the available set contribute to a target score. The factor product has rank at most r; masking its diagonal can change matrix rank.'),
      ('code',"for rank,(t,c) in FACTORS.items():print(rank,probabilities(t,c,[0,1,2]))\nn=5000\nprint('Full stored entries',n*n)\nfor r in [1,2,3]:print('Rank',r,'factor entries',2*n*r,'float64 MiB',8*2*n*r/2**20)"),
      ('markdown','## Proposed cache connection\nA bounded policy selector could learn among no prefetch, next-line and stride. Choice-set context is not workload telemetry. A telemetry-conditioned extension and its training data require separate design and evaluation; no CDM cache gain is measured here.')])
if __name__=='__main__':main()
