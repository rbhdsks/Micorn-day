#!/usr/bin/env python3
"""Retain compact measured evidence; omit binaries, full waveforms and raw corpus."""
from pathlib import Path
import shutil,json,hashlib
P=Path(__file__).resolve().parents[1];B=P/'build/benchmarks';O=P/'level5/results/reference'
def main():
 O.mkdir(parents=True,exist_ok=True)
 for name in ['summary.csv','aggregates.csv','selection.json','evaluation.json','provenance.json','predeclared_plan.json','sensitivity.csv']:
  shutil.copyfile(B/name,O/name)
 for name in ['runs','traces','sensitivity_runs']:
  target=O/name;target.mkdir(exist_ok=True)
  for f in (B/name).iterdir():
   if f.suffix in ['.csv','.log','.json']:shutil.copyfile(f,target/f.name)
 ref=P/'level4/reference';ref.mkdir(exist_ok=True)
 for src,name in [(P/'build/verification/verification.json','verification.json'),(P/'build/independent/summary.json','independent.json'),(P/'build/synthesis/summary.json','synthesis.json')]:shutil.copyfile(src,ref/name)
 # Full per-request samples remain reproducible in build. A measured subset
 # supports feedback/timing figures; exact numeric matrices are also retained.
 files=[p for p in O.rglob('*') if p.is_file()]
 (O/'checksums.json').write_text(json.dumps({str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.name!='checksums.json'},indent=2)+'\n')
 print('Exported',len(files),'compact evidence files; source text and executable builds excluded')
if __name__=='__main__':main()
