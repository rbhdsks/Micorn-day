#!/usr/bin/env python3
"""Execute scalar matrix multiplication and log MODELLED array addresses.

Not a CPU/GPU instruction trace: Python interpreter, registers, optimisations,
stack accesses, physical addresses and hardware caches are not represented.
"""
import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    m: int = 16
    k: int = 16
    n: int = 32
    element_size: int = 4
    alignment: int = 4096

    def __post_init__(self):
        if min(self.m, self.k, self.n) <= 0:
            raise ValueError('matrix dimensions must be positive')
        if self.element_size != 4:
            raise ValueError('this model uses four-byte integer elements')
        if self.alignment < 64 or self.alignment & (self.alignment - 1):
            raise ValueError('alignment must be a power of two >= 64')


def layout(config):
    sizes = {'A': config.m * config.k * 4,
             'B': config.k * config.n * 4,
             'C': config.m * config.n * 4}
    cursor = config.alignment
    result = {}
    for name, size in sizes.items():
        cursor = (cursor + config.alignment - 1) // config.alignment * config.alignment
        result[name] = {'base': cursor, 'size_bytes': size}
        cursor += size
    return result


def generate(output, config=Config(), order='ijk'):
    if order not in ('ijk', 'ikj'):
        raise ValueError('order must be ijk or ikj')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    regions = layout(config)
    # Small deterministic integer values; no download, random seed, or overflow.
    a = [[(i + 2 * k) % 7 - 3 for k in range(config.k)] for i in range(config.m)]
    b = [[(3 * k + j) % 5 - 2 for j in range(config.n)] for k in range(config.k)]
    c = [[0] * config.n for _ in range(config.m)]
    count = 0
    with (output / 'trace.csv').open('w', newline='') as target:
        writer = csv.writer(target)
        writer.writerow(['sequence', 'phase', 'operation', 'operand', 'address', 'size_bytes', 'i', 'j', 'k'])

        def emit(phase, operation, operand, offset, i, j='', k=''):
            nonlocal count
            writer.writerow([count, phase, operation, operand,
                             hex(regions[operand]['base'] + offset * 4), 4, i, j, k])
            count += 1

        for i in range(config.m):
            for j in range(config.n):
                emit('initialise', 'W', 'C', i * config.n + j, i, j)
        for i in range(config.m):
            pairs = ((j, k) for j in range(config.n) for k in range(config.k)) if order == 'ijk' else ((j, k) for k in range(config.k) for j in range(config.n))
            for j, k in pairs:
                # Explicit model: every multiply-accumulate reads A, B, C and
                # writes C. No hoisting A or retaining C in a register.
                emit('compute', 'R', 'A', i * config.k + k, i, j, k)
                emit('compute', 'R', 'B', k * config.n + j, i, j, k)
                emit('compute', 'R', 'C', i * config.n + j, i, j, k)
                c[i][j] += a[i][k] * b[k][j]
                emit('compute', 'W', 'C', i * config.n + j, i, j, k)
    reference = [[sum(a[i][k] * b[k][j] for k in range(config.k))
                  for j in range(config.n)] for i in range(config.m)]
    if c != reference:
        raise AssertionError('matrix multiplication differs from reference')
    metadata = {
        'provenance': 'modelled scalar algorithm accesses; NOT captured hardware accesses',
        'config': asdict(config), 'loop_order': order, 'storage': 'row-major',
        'regions': regions, 'access_count': count,
        'expected_access_count': config.m * config.n + 4 * config.m * config.n * config.k,
        'reference_check_passed': True, 'result_checksum': sum(map(sum, c)),
        'assumptions': [
            'Deterministic small integer inputs; four-byte modelled elements.',
            'Input construction is excluded; C initialisation is logged separately.',
            'Each compute step logs A read, B read, C read, C write in that order.',
            'No register reuse, vectorisation, threading, compiler or hardware effects.',
            'Sequence is logical access order, not a timestamp; addresses are assigned model addresses.'
        ]
    }
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    (output / 'result.json').write_text(json.dumps(c) + '\n')
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--m', type=int, default=16)
    parser.add_argument('--k', type=int, default=16)
    parser.add_argument('--n', type=int, default=32)
    parser.add_argument('--order', choices=['ijk', 'ikj'], default='ijk')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata = generate(args.output, Config(args.m, args.k, args.n), args.order)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'error: {exc}\n')
    print(f'Generated {metadata["access_count"]} MODELLED accesses in {args.output}')


if __name__ == '__main__':
    main()
