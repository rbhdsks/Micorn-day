#!/usr/bin/env python3
"""Deterministic synthetic probes plus filtered modelled A/B-read traces.

Neither family is a captured CPU/GPU trace or a measured inference execution.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path
from trace_io import TraceRow, write_trace

PHASE_ROOT = Path(__file__).resolve().parents[2]
SEED = 20261101


def synthetic_traces():
    rng = random.Random(SEED)
    row = lambda address, gap: TraceRow(address, gap)
    traces = {
        'zero_gap_stream': [row(0x1000+16*i, 0) for i in range(512)],
        'tensor_stream': [row(0x1000+4*i, 6) for i in range(512)],
        'column_stride': [row(0x10000+64*i, 20) for i in range(512)],
        'tiled_reuse': [row(0x20000+(i//128)*256+(i%64)*4, 6) for i in range(512)],
        'embedding_gather': [row(0x40000+rng.randrange(2048)*16, 4) for i in range(512)],
        'interleaved_conflicting': [row(0x1000+(i//2)*16+(0x10000 if i%2 else 0), 20) for i in range(512)],
        'phase_shift': [row(0x1000+i*16 if i<256 else 0x10000+(i-256)*64, 20) for i in range(512)],
        'pollution_return': [row(a, 20) for _ in range(64) for a in [0x1000, 0x13d0, 0x13e0, 0x13f0, 0x1000]],
        'three_line_bursts': [row(0x10000+burst*0x1000+j*16, 20) for burst in range(64) for j in range(3)],
        'two_stream_disjoint_sets': [row(0x1000+(i//2)*32 if i%2==0 else 0x40010+(i//2)*32, 20) for i in range(512)],
        'same_line': [row(0x1000+4*(i%4), 0) for i in range(16)],
    }
    return traces


def load_matmul_generator():
    path = PHASE_ROOT/'level1/generate_matmul_trace.py'
    spec = importlib.util.spec_from_file_location('phase1_modelled_matmul', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolves its defining module.
    spec.loader.exec_module(module)
    return module


def filter_immutable_reads(source, gap=6):
    """Retain only compute reads of assigned immutable A/B regions.

    Original ordering is preserved. Mutable C and all writes/initialisation are
    excluded. The resulting stream is an intentionally filtered address study.
    """
    rows = []
    excluded = 0
    with Path(source).open(newline='') as file:
        for record in csv.DictReader(file):
            if record['phase']=='compute' and record['operation']=='R' and record['operand'] in ('A','B'):
                if int(record['size_bytes']) != 4:
                    raise ValueError('bridge only supports aligned four-byte accesses')
                rows.append(TraceRow(int(record['address'], 16), gap))
            else:
                excluded += 1
    return rows, excluded


def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 1, 'trace_contract': 'aligned immutable 32-bit reads; hex 0x byte address and post-response gap',
                'seed': SEED, 'line_size_bytes': 16, 'traces': []}
    for name, rows in synthetic_traces().items():
        path = output/f'{name}.csv'
        write_trace(path, rows)
        manifest['traces'].append({'name':name, 'file':path.name, 'kind':'synthetic_pattern',
            'rows':len(rows), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'provenance':'locally generated deterministic access-pattern probe; not an application capture',
            'seed':SEED if name=='embedding_gather' else None})
    module = load_matmul_generator()
    for order in ('ijk','ikj'):
        source_dir = output/'modelled_sources'/order
        config = module.Config(m=4,k=8,n=8)
        metadata = module.generate(source_dir, config, order)
        source = source_dir/'trace.csv'
        rows, excluded = filter_immutable_reads(source)
        name = f'modelled_matmul_{order}_ab_reads'
        path = output/f'{name}.csv'
        write_trace(path, rows)
        manifest['traces'].append({'name':name,'file':path.name,'kind':'filtered_modelled_algorithm',
            'rows':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'provenance':'Nitesh Level 1 scalar matmul generator; logical A/B compute reads only; not captured machine accesses',
            'source_generator':'level1/generate_matmul_trace.py',
            'source_generator_sha256':hashlib.sha256((PHASE_ROOT/'level1/generate_matmul_trace.py').read_bytes()).hexdigest(),
            'source_file':str(source.relative_to(output)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'config':metadata['config'],'loop_order':order,'excluded_rows':excluded,
            'filter':'phase=compute AND operation=R AND operand in {A,B}; exclude C, writes and initialisation',
            'gap_cycles':6,'gap_source':'explicit replay assumption, not measured compute timing',
            'numerical_generator_reference_passed':metadata['reference_check_passed'],
            'rtl_memory_contents':'address-derived deterministic word pattern, not matrix numeric values'})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('build/benchmarks/traces'))
    args=parser.parse_args()
    manifest=generate(args.output)
    print(f'Generated {len(manifest["traces"])} documented read-only traces in {args.output}')

if __name__=='__main__': main()
