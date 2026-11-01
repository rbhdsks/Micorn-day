#!/usr/bin/env python3
"""Generate, analyse and replay read-only traces through three RTL policies."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from generate_traces import generate
from trace_io import read_trace, write_mem
from metrics import POLICIES, read_measurement, summarize, write_outputs

ROOT=Path(__file__).resolve().parents[2]
UPSTREAM_COMMIT='e0ab37c30e7a02dd1f3d868aef956ee88104a8b0'


def relative(path):
    return os.path.relpath(Path(path).resolve(),ROOT)


def simulator_path(path):
    value=relative(path)
    if any(character.isspace() for character in value):
        raise ValueError('simulator replay/output paths must not contain whitespace: '+value)
    return value


def invalidate_published_outputs(output):
    # Failed attempts must not expose an older successful summary as current.
    for name in ('summary.csv','report.md','provenance.json'):
        path=Path(output)/name
        if path.is_file():path.unlink()


def execute(command, log, commands, expected_pass=False):
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    log.parent.mkdir(parents=True,exist_ok=True)
    log.write_text(result.stdout+result.stderr)
    commands.append({'argv':command,'cwd':'Phase1','log':relative(log),'exit_code':result.returncode})
    if result.returncode or (expected_pass and 'PASS:' not in result.stdout):
        raise RuntimeError(f'command failed: {shlex.join(command)}\n{result.stdout}{result.stderr}')
    return result


def load_analyser():
    spec=importlib.util.spec_from_file_location('phase1_level1_analyser',ROOT/'level1/analyze_trace.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def run(output, trace_dir=None, index_bits=6, latency=12, workloads=None):
    output=Path(output).resolve()
    simulator_path(output)
    output.mkdir(parents=True,exist_ok=True)
    invalidate_published_outputs(output)
    if not 1<=index_bits<=12:
        raise ValueError('benchmark runner supports practical INDEX_BITS in 1..12')
    if not 0<=latency<=100000:
        raise ValueError('LATENCY must be in 0..100000 for this runner')
    if trace_dir is None:
        trace_dir=output/'traces';manifest=generate(trace_dir)
    else:
        trace_dir=Path(trace_dir).resolve()
        manifest_path=trace_dir/'manifest.json'
        if manifest_path.exists():
            manifest=json.loads(manifest_path.read_text())
        else:
            manifest={'schema_version':1,'traces':[{'name':p.stem,'file':p.name,'kind':'external_read_only',
                       'provenance':'user-supplied aligned read trace; provenance not independently established'} for p in sorted(trace_dir.glob('*.csv'))]}
    descriptions=manifest['traces']
    if not descriptions:
        raise ValueError('no trace inputs')
    if workloads:
        missing=set(workloads)-{d['name'] for d in descriptions}
        if missing:raise ValueError('unknown workloads: '+', '.join(sorted(missing)))
        descriptions=[d for d in descriptions if d['name'] in workloads]
    names=[d['name'] for d in descriptions]
    if len(names)!=len(set(names)):raise ValueError('duplicate trace names')
    for description in descriptions:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',description['name']) or description['file']!=description['name']+'.csv':
            raise ValueError('trace names must be safe basenames, and file must be name.csv')
    commands=[];measurements=[]
    iverilog=shlex.split(os.environ.get('IVERILOG','iverilog'))
    vvp=shlex.split(os.environ.get('VVP','vvp'))
    ivflags=shlex.split(os.environ.get('IVFLAGS',''))
    if not iverilog or not vvp:raise ValueError('IVERILOG and VVP must identify executables')
    versions={}
    for label,command in [('iverilog',iverilog+['-V']),('vvp',vvp+['-V'])]:
        result=execute(command,output/f'{label}_version.log',commands)
        versions[label]=(result.stdout+result.stderr).splitlines()[0]
    versions['python']=sys.version.split()[0]
    sources=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'level4/rtl').glob('*.sv'))]
    sources+=['level4/tb/dram_model.sv','level4/tb/tb_trace.sv']
    binaries={}
    for policy_number in (1,2):
        binary=output/f'trace_policy{policy_number}.vvp';binaries[policy_number]=binary
        command=iverilog+ivflags+['-g2012','-Wall','-s','tb_trace',f'-Ptb_trace.INDEX_BITS={index_bits}',
                    f'-Ptb_trace.LATENCY={latency}',f'-Ptb_trace.PREFETCH_POLICY={policy_number}','-o',relative(binary),*sources]
        execute(command,output/f'compile_policy{policy_number}.log',commands)
    analyser=load_analyser()
    trace_records=[]
    for description in descriptions:
        name=description['name'];path=trace_dir/description['file'];rows=read_trace(path)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if description.get('sha256') and description['sha256']!=digest:
            raise ValueError(f'{name}: manifest SHA256 does not match input')
        if 'rows' in description and description['rows']!=len(rows):
            raise ValueError(f'{name}: manifest row count does not match input')
        mem=output/'replay'/f'{name}.mem';mem.parent.mkdir(parents=True,exist_ok=True);write_mem(mem,rows)
        analysis=analyser.analyze((r.address for r in rows),line_size=16)
        analysis_dir=output/'analysis';analysis_dir.mkdir(exist_ok=True)
        (analysis_dir/f'{name}.summary.json').write_text(json.dumps(analysis,indent=2)+'\n')
        (analysis_dir/f'{name}.md').write_text(analyser.markdown_report(analysis))
        trace_records.append({**description,'rows':len(rows),'sha256':digest,'input':relative(path),
                              'replay':relative(mem),'analysis_line_size_bytes':16})
        for policy in POLICIES:
            number=2 if policy=='next_line' else 1;enabled=int(policy!='none')
            csv_out=output/'runs'/f'{name}__{policy}.csv';log=csv_out.with_suffix('.log')
            csv_out.parent.mkdir(exist_ok=True)
            command=vvp+[relative(binaries[number]),f'+TRACE={simulator_path(mem)}',f'+COUNT={len(rows)}',
                         f'+PF={enabled}',f'+OUT={simulator_path(csv_out)}']
            execute(command,log,commands,expected_pass=True)
            row=read_measurement(csv_out,len(rows),enabled)
            if row.get('prefetch_policy')!=number or row.get('index_bits')!=index_bits or row.get('memory_latency')!=latency:
                raise ValueError('RTL result configuration differs from requested paired experiment')
            measurements.append({'workload':name,'trace_kind':description.get('kind','external_read_only'),
                                 'policy':policy,**row})
            print(f"PASS {name:33} {policy:9} hits={row['hits']:5}/{len(rows)} completion={row['completion_cycles']:7} DRAM={row['dram_reads']}",flush=True)
    summary=summarize(measurements);write_outputs(output,summary,index_bits,latency)
    hashed_sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ('level4/rtl','level4/tb','level5/scripts') for p in sorted((ROOT/folder).glob('*')) if p.is_file()}
    for name in ('analyze_trace.py','generate_matmul_trace.py'):
        p=ROOT/'level1'/name;hashed_sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    provenance={'schema_version':1,'measurement_kind':'self-checking RTL simulation, not physical DRAM or application execution',
                'level1_upstream':{'repository':'https://github.com/rbhdsks/Micorn-day','branch':'nitesh/feat-level1','commit':UPSTREAM_COMMIT},
                'tool_versions':versions,'parameters':{'INDEX_BITS':index_bits,'LINE_BYTES':16,'LATENCY':latency,
                'policies':list(POLICIES),'response_stall_cycles':'request_index % 4','driver':'serialized reads with post-response compute gaps',
                'primary_cycles':'completion_cycles to final consumed demand response; final unused gap excluded',
                'drain':'bounded natural quiescence; separate quiescent_cycles'},
                'traces':trace_records,'source_sha256':hashed_sources,'commands':commands,
                'successful_runs':len(measurements),'checked_responses':sum(r['accesses'] for r in measurements)}
    (output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(f"Saved {len(measurements)} measured runs and {provenance['checked_responses']} checked responses to {relative(output)}")
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('build/benchmarks'))
    parser.add_argument('--trace-dir',type=Path,help='directory of strict address,gap CSVs and optional manifest.json; omit to generate bundled probes')
    parser.add_argument('--index-bits',type=int,default=6)
    parser.add_argument('--latency',type=int,default=12)
    parser.add_argument('--workload',action='append',help='run only this workload (repeatable)')
    args=parser.parse_args()
    try:run(args.output,args.trace_dir,args.index_bits,args.latency,args.workload)
    except (ValueError,OSError,RuntimeError,KeyError,json.JSONDecodeError) as exc:
        parser.exit(1,f'ERROR: {exc}\n')

if __name__=='__main__':main()
