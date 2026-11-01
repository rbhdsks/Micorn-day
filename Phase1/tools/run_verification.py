#!/usr/bin/env python3
"""Run compiled RTL tests with strict exit/PASS checks and retained transcripts."""
import argparse
import json
import shlex
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vvp', default='vvp')
    parser.add_argument('benches', nargs='+', type=Path)
    args = parser.parse_args()
    results = []
    for bench in args.benches:
        command = shlex.split(args.vvp) + [str(bench)]
        run = subprocess.run(command, capture_output=True, text=True)
        transcript = run.stdout + run.stderr
        log = bench.with_suffix('.log')
        log.write_text(transcript)
        print(transcript, end='')
        result = {'bench': bench.stem, 'command': command, 'exit_code': run.returncode,
                  'pass': run.returncode == 0 and 'PASS' in run.stdout,
                  'log': log.as_posix()}
        results.append(result)
        if not result['pass']:
            raise SystemExit(f'FAILED {bench.stem}; see {log}')
    (Path('build/verification') / 'verification.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
