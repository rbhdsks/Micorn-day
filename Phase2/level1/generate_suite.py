#!/usr/bin/env python3
"""Numerically checked kernel traces and predeclared context stress suite.

Input-data authenticity does not make assigned tensor addresses or gaps captured
machine traces. Only immutable input reads are recorded; output writes excluded.
"""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,math,random,sys
from fetch_corpus import load as load_corpus
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
sys.path.append(str(REPO/'Phase1/level5/scripts'))
from generate_traces import generate as generate_legacy
from trace_io import read_trace
SEEDS=(11,101,202)

class Operand:
 def __init__(self,values,base,trace):self.values=values;self.base=base;self.trace=trace
 def read(self,index):
  self.trace.append(self.base+4*index);return self.values[index]

def kernel(kind,seed):
 rng=random.Random(seed);trace=[]
 base_a=0x1000000+(seed%4)*0x100;base_b=0x2000000+((seed*3)%4)*0x100
 if kind=='gemm_tiled':
  m,n,k={11:(4,8,12),101:(6,8,8),202:(8,6,8)}[seed]
  av=[rng.randint(-4,4) for _ in range(m*k)];bv=[rng.randint(-4,4) for _ in range(k*n)]
  a=Operand(av,base_a,trace);b=Operand(bv,base_b,trace);out=[[0]*n for _ in range(m)]
  for ii in range(0,m,4):
   for jj in range(0,n,4):
    for kk in range(0,k,4):
     for i in range(ii,min(ii+4,m)):
      for j in range(jj,min(jj+4,n)):
       for z in range(kk,min(kk+4,k)):out[i][j]+=a.read(i*k+z)*b.read(z*n+j)
  reference=[[sum(av[i*k+z]*bv[z*n+j] for z in range(k)) for j in range(n)] for i in range(m)]
  config={'m':m,'n':n,'k':k,'tile':4,'layout':'row-major A,B; blocked ii,jj,kk,i,j,k'}
 elif kind=='conv1d':
  ci,co,length,width={11:(3,2,34,3),101:(4,2,28,3),202:(2,3,34,5)}[seed]
  av=[rng.randint(-3,3) for _ in range(ci*length)];bv=[rng.randint(-3,3) for _ in range(co*ci*width)]
  a=Operand(av,base_a,trace);b=Operand(bv,base_b,trace);out=[[0]*(length-width+1) for _ in range(co)]
  for o in range(co):
   for x in range(length-width+1):
    for c in range(ci):
     for z in range(width):out[o][x]+=a.read(c*length+x+z)*b.read((o*ci+c)*width+z)
  reference=[[sum(av[c*length+x+z]*bv[(o*ci+c)*width+z] for c in range(ci) for z in range(width)) for x in range(length-width+1)] for o in range(co)]
  config={'input_channels':ci,'output_channels':co,'length':length,'kernel_width':width,'stride':1,'padding':0,'layout':'channel-major valid cross-correlation'}
 elif kind=='depthwise1d':
  channels,length,width={11:(4,42,5),101:(3,50,5),202:(4,46,3)}[seed]
  av=[rng.randint(-3,3) for _ in range(channels*length)];bv=[rng.randint(-3,3) for _ in range(channels*width)]
  a=Operand(av,base_a,trace);b=Operand(bv,base_b,trace);out=[[0]*(length-width+1) for _ in range(channels)]
  for c in range(channels):
   for x in range(length-width+1):
    for z in range(width):out[c][x]+=a.read(c*length+x+z)*b.read(c*width+z)
  reference=[[sum(av[c*length+x+z]*bv[c*width+z] for z in range(width)) for x in range(length-width+1)] for c in range(channels)]
  config={'channels':channels,'length':length,'kernel_width':width,'stride':1,'padding':0,'layout':'channel-major depthwise valid cross-correlation'}
 elif kind=='embedding_hot':
  rows,dim,count=512,8,96
  weights=[1/math.pow(i+1,1.15) for i in range(rows)]
  ids=rng.choices(range(rows),weights=weights,k=count)
  values=[rng.randint(-8,8) for _ in range(rows*dim)];a=Operand(values,base_a,trace);out=[0]*dim
  for index in ids:
   for c in range(dim):out[c]+=a.read(index*dim+c)
  reference=[sum(values[index*dim+c] for index in ids) for c in range(dim)]
  config={'rows':rows,'dimension':dim,'lookups':count,'index_distribution':'finite rank weights proportional to (rank+1)^(-1.15)','output':'sum pooling'}
 else:raise ValueError('unknown kernel '+kind)
 assert out==reference,(kind,seed,'numerical mismatch')
 return trace,{'config':config,'numeric_reference_passed':True,'numeric_output_sha256':hashlib.sha256(json.dumps(out).encode()).hexdigest(),
  'operand_bases':[base_a,base_b] if kind!='embedding_hot' else [base_a],
  'instrumentation':'actual scalar input reads performed while calculating output; independent uninstrumented sum/product reference; no output writes replayed'}

def corpus_embedding(source):
 tokens=source['text'].split()[:256];dim=8
 # Fixed hashing avoids fitting vocabulary on any evaluation split. Collisions
 # are disclosed and counted; this is not a trained language-model tokenizer.
 ids=[int.from_bytes(hashlib.blake2b(t.encode(),digest_size=8).digest(),'big')%65536 for t in tokens]
 addr=[];out=[0]*dim
 value=lambda row,c:((row*17+c*13)%31)-15
 for row in ids:
  for c in range(dim):addr.append(0x3000000+(row*dim+c)*4);out[c]+=value(row,c)
 ref=[sum(value(row,c) for row in ids) for c in range(dim)];assert ref==out
 words=set(tokens);unique_ids=len(set(ids))
 return addr,{'source':{k:v for k,v in source.items() if k!='text'},'tokens':len(tokens),'dimension':dim,'table_rows':65536,
  'tokenizer':'UTF-8 whitespace tokens, case/punctuation preserved; BLAKE2b64 big-endian modulo65536; fixed mapper, not BPE or trained tokenizer',
  'unique_tokens':len(words),'unique_embedding_ids':unique_ids,'hash_collisions':len(words)-unique_ids,
  'numeric_reference_passed':True,'numeric_output_sha256':hashlib.sha256(json.dumps(out).encode()).hexdigest(),
  'timing_and_layout':'modelled row-major eight-word embeddings; no captured CPU/GPU instructions or inference timing'}

def stress_cases():
 # Twelve predeclared stress cases. These diagnose context boundaries and
 # cross-region global feedback coupling, not natural workload probabilities.
 traces={
 'boundary_crossing':[0x1000+i*0x800 for i in range(128)],
 'same_region_interleave':[0x1000+(i//2)*16+(0x400 if i%2 else 0) for i in range(128)],
 'mixed_regions':[a for i in range(32) for a in [0x10000+i*16,0x20000+(i//3)*0x1000+(i%3)*16]],
 }
 return [(name,addresses,gap,latency) for name,addresses in traces.items() for gap,latency in [(0,0),(24,0),(0,48),(24,48)]]

def write_trace(path,addresses,gap):
 with path.open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['address','gap'])
  w.writerows((f'0x{x:08x}',gap) for x in addresses)

def generate(output,corpus_dir=None,download=False,include_corpus=True):
 output=Path(output);output.mkdir(parents=True,exist_ok=True);records=[]
 def add(case_id,workload,family,split,source_kind,seed,gap,latency,addresses,metadata):
  path=output/f'{case_id}.csv';write_trace(path,addresses,gap)
  records.append(dict(case_id=case_id,workload=workload,family=family,split=split,source_kind=source_kind,seed=seed,
   gap_cycles=gap,memory_latency=latency,rows=len(addresses),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),file=path.name,metadata=metadata))
 legacy=generate_legacy(output/'legacy_sources')
 for d in legacy['traces']:
  rows=read_trace(output/'legacy_sources'/d['file']);name=d['name'];addresses=[r.address for r in rows]
  # Original probes have constant gap within each trace.
  add('legacy_'+name,name,'legacy_diagnostic','regression',d['kind'],d.get('seed'),rows[0].gap,12,addresses,{'source':d,'contract':'byte-for-byte same address/gap rows as Phase1 generator'})
 for kind in ['gemm_tiled','conv1d','depthwise1d','embedding_hot']:
  for seed in SEEDS:
   addresses,metadata=kernel(kind,seed)
   for gap in (0,12):add(f'{kind}_s{seed}_g{gap}',kind,kind,'validation' if seed==11 else 'held_out','instrumented_numeric_kernel',seed,gap,12,addresses,metadata)
 if include_corpus:
  corpus=load_corpus(corpus_dir or ROOT/'build/data',download)
  for split,source in corpus.items():
   addresses,metadata=corpus_embedding(source)
   for gap in (0,12):add(f'wikitext_{split}_g{gap}','wikitext_embedding','wikitext_embedding','validation' if split=='train' else 'held_out','authentic_input_modelled_layout',None,gap,12,addresses,metadata)
 for name,addresses,gap,latency in stress_cases():add(f'{name}_g{gap}_l{latency}',name,'context_stress','stress','synthetic_diagnostic',None,gap,latency,addresses,{'purpose':'address-region boundary/interference/global-feedback coupling diagnostic'})
 manifest={'schema_version':2,'cases':records,'line_bytes':16,'read_only_contract':'aligned immutable32-bit inputs; input reads only; fixed serial offered-demand driver',
  'selection_split':'validation only; seed11 and WikiText published train input; no evaluation results used for threshold or variant choice',
  'evaluation_split':'held_out: seeds101/202 and WikiText published validation/test; diagnostic/regression separate',
  'corpus_included':include_corpus,'raw_corpus_redistributed':False,
  'limitations':['No real model instruction trace or GPU/CPU timing','Small kernels do not establish production working-set representativeness','Per-family gaps/layouts are model choices','Seed variation is not independent application sampling','RTL returns deterministic address-derived words rather than running tensor arithmetic']}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/benchmarks/traces');p.add_argument('--corpus-dir',type=Path);p.add_argument('--download-corpus',action='store_true');p.add_argument('--no-corpus',action='store_true');a=p.parse_args()
 m=generate(a.output,a.corpus_dir,a.download_corpus,not a.no_corpus);print('Generated',len(m['cases']),'documented matched cases')
if __name__=='__main__':main()
