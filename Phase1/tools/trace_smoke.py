#!/usr/bin/env python3
"""Check settled draining at latency 128 and same-line replay for both policies."""
import csv
import os
import shlex
import subprocess
from pathlib import Path


def checked(command, log):
    result = subprocess.run(command, text=True, capture_output=True)
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        print(result.stdout + result.stderr)
        raise SystemExit(f'Failed {command}; see {log}')
    return result.stdout


def main():
    root = Path('build/verification')
    root.mkdir(parents=True, exist_ok=True)
    scenarios = {'high_latency': [(0x1000, 0), (0x1010, 0), (0x1020, 0)],
                 'same_line': [(0x1000, 0), (0x1004, 0)]}
    for policy in (1, 2):
        executable = root / f'trace_smoke_policy{policy}.vvp'
        sources = sorted(Path('level4/rtl').glob('*.sv'))
        command = shlex.split(os.getenv('IVERILOG', 'iverilog')) + shlex.split(os.getenv('IVFLAGS', ''))
        command += ['-g2012', '-Wall', '-s', 'tb_trace', '-Ptb_trace.LATENCY=128',
                    f'-Ptb_trace.PREFETCH_POLICY={policy}', '-o', str(executable)]
        command += [str(p) for p in sources] + ['level4/tb/dram_model.sv', 'level4/tb/tb_trace.sv']
        checked(command, root / f'trace_smoke_policy{policy}_compile.log')
        for name, rows in scenarios.items():
            trace = root / f'{name}.mem'
            trace.write_text(''.join(f'{a:08x}{g:08x}\n' for a, g in rows))
            for mode in (0, 1):
                stem = f'{name}_policy{policy}_pf{mode}'
                output = root / f'{stem}.csv'
                command = shlex.split(os.getenv('VVP', 'vvp')) + [str(executable),
                    f'+TRACE={trace}', f'+COUNT={len(rows)}', f'+PF={mode}', f'+OUT={output}']
                text = checked(command, root / f'{stem}.log')
                if 'PASS:' not in text:
                    raise SystemExit(f'Missing PASS: {stem}')
                with output.open() as file:
                    row = {key: int(value) for key, value in next(csv.DictReader(file)).items()}
                if row['accesses'] != len(rows) or row['quiescent_cycles'] < row['completion_cycles']:
                    raise SystemExit(f'Invalid counts: {stem}')
                if name == 'high_latency' and policy == 1 and mode == 1:
                    if row['quiescent_cycles'] - row['completion_cycles'] <= 100:
                        raise SystemExit('High-latency probe no longer exercises the old short-drain failure')
                print(text.splitlines()[0])


if __name__ == '__main__':
    main()
