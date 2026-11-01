#!/usr/bin/env python3
from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[2];P=R/'Phase2';B=P/'build/benchmarks'
if not (B/'summary.csv').exists():B=P/'level5/results/reference'
def measured_json(build_path,reference_name):
 path=P/build_path
 if not path.exists():path=P/'level4/reference'/reference_name
 return json.loads(path.read_text())
rows=list(csv.DictReader((B/'summary.csv').open()));agg=list(csv.DictReader((B/'aggregates.csv').open()))
def number(v):
 try:return float(v)
 except ValueError:return v
g={}
for r in rows:g.setdefault(r['case_id'],{})[r['variant']]={k:number(v) for k,v in r.items()}
a={}
for r in agg:a.setdefault(r['split'],{})[r['variant']]={k:number(v) for k,v in r.items()}
manifest=json.loads((B/'traces/manifest.json').read_text());families=sorted({r['family'] for r in rows})
coverage={f:[sum(c['family']==f and c['split']==s for c in manifest['cases']) for s in ['validation','held_out','regression','stress']] for f in families}
family={}
for f in families:
 family[f]={}
 for v in a['held_out']:
  z=[float(r['speedup']) for r in rows if r['split']=='held_out' and r['family']==f and r['variant']==v]
  if z:family[f][v]=math.exp(sum(map(math.log,z))/len(z))
data={'repo_url':'https://github.com/presish1/micron-context-aware-cache','rows':g,'aggregates':a,'coverage':coverage,'family':family,
 'selection':json.loads((B/'selection.json').read_text()),'evaluation':json.loads((B/'evaluation.json').read_text()),
 'verification':measured_json('build/verification/verification.json','verification.json'),'independent':measured_json('build/independent/summary.json','independent.json'),
 'synthesis':measured_json('build/synthesis/summary.json','synthesis.json'),'audit':json.loads((P/'audit/results_second_pass.json').read_text())}
(R/'Final/source/evidence.json').write_text(json.dumps(data,indent=2)+'\n')
print('Prepared final deck/report evidence from exact measurements')
