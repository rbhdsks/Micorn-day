#!/usr/bin/env python3
"""Prepare a clean final-only publication tree without private working history."""
from pathlib import Path
import hashlib,os,re,shutil,subprocess
R=Path(__file__).resolve().parents[2];O=R.parent/'micron-context-aware-cache-final'
def main():
 O.mkdir(exist_ok=True)
 paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=R).decode().split('\0')
 for rel in paths:
  if not rel or rel=='SHA256SUMS' or rel.startswith(('Phase1/presentation/','Phase1/report/','.chart-data-')) or rel.endswith('.zip'):continue
  src=R/rel
  if not src.is_file():continue
  dst=O/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 # A single final deck/report replaces earlier binary deliverables. Retain all
 # baseline source/tests/results while redirecting their old artifact links.
 for p in O.rglob('*.md'):
  def fix(m):
   target=m.group(2)
   if '://' in target or target.startswith('#'):return m.group(0)
   absolute=(p.parent/target.split('#')[0]).resolve()
   if not absolute.exists() and ('presentation' in target or 'report' in target):
    dest=O/'Final'/('Hackathon_Presentation.pptx' if 'presentation' in target else 'Hackathon_Report.pdf')
    return '['+m.group(1)+']('+os.path.relpath(dest,p.parent)+')'
   return m.group(0)
  p.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)',fix,p.read_text()))
 (O/'README.md').write_text('''# Context aware cache and prefetch engine

[Final presentation](Final/Hackathon_Presentation.pptx) | [Final technical report](Final/Hackathon_Report.pdf) | [Scientific figure gallery](Phase2/plots/README.md)

This is the clean final hackathon submission. Earlier draft decks, build outputs, raw corpus text and private attachments are excluded.

| Team member | Identifier | Programme | Department |
|---|---|---|---|
| Presish Gautam | GE26Z817 | B.Tech, 3rd year | Data Science and AI |
| Nitesh Kumar Shah | ID25M806 | M.Tech, 2nd year | Data Science and AI |

Regional history reduces the conflicting-stream diagnostic from 21,258 to 12,626 completion cycles with 514 versus 512 memory reads. A two-line speculative buffer repairs the baseline pollution mechanism. The equal-extra-data victim control outperforms the region design on held-out aggregate time and traffic; the final report preserves that counterexample.

## Five challenge levels

| Level | Read and run |
|---|---|
|1 Memory trace analysis|[Complete numeric kernels, authentic input and split policy](Phase2/level1/README.md)|
|2 Cache architecture|[Storage, placement and resource control](Phase2/level2/README.md)|
|3 Prefetch strategy|[Regional algorithm and mature feedback ablation](Phase2/level3/README.md)|
|4 RTL implementation|[Typed FSM, SystemVerilog assertions, independent scoreboards and AMD flow](Phase2/level4/README.md)|
|5 Performance validation|[55 cases, seven variants and 385 primary runs](Phase2/level5/README.md)|

```sh
make -C Phase2 test
make -C Phase2 independent
make -C Phase2 benchmark
make -C Phase2 figures
```

The executed upgrade evidence includes 96,039 primary RTL regression checks,35,982 independent returned responses,338,232 benchmark response checks and ten generic synthesis views. The 13 new Python tests cover dataset and metric logic. [Phase1](Phase1/README.md) preserves the source/test baseline. [Audits](Phase2/audit/PLAN.md), [raw results](Phase2/level5/results/reference/summary.csv), [math](Phase2/docs/MATH_AND_CONTEXT.md) and [research](Phase2/research/literature_review.md) make each claim reviewable.

Icarus, Verilator, Yosys and GNU Octave executed. Native MATLAB and AMD Vivado/xsim were unavailable. Vendor scripts are provided without claiming routed timing, FPGA board operation, device energy or full-model inference speedup. CDM remains separate research. AI assistance is disclosed in provenance. No company endorsement or judging outcome is implied.
''')
 (O/'Makefile').write_text('.PHONY: all test benchmark figures independent synth\nall test benchmark figures independent synth:\n\t$(MAKE) -C Phase2 $@\n')
 workflow=O/'.github/workflows/final.yml';workflow.parent.mkdir(parents=True,exist_ok=True)
 workflow.write_text('''name: Final RTL verification
on: [push, pull_request, workflow_dispatch]
jobs:
  verify:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: sudo apt-get update && sudo apt-get install -y iverilog verilator
      - run: make -C Phase2 test
      - run: make -C Phase2 independent
''')
 old=O/'.github/workflows/phase1.yml'
 if old.exists():old.unlink()
 files=sorted(p for p in O.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip') and p.name!='SHA256SUMS' and 'build' not in p.relative_to(O).parts)
 (O/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(O)}\n' for p in files))
 print(O,'prepared',len(files),'files; exactly one final PPTX and one final report')
if __name__=='__main__':main()
