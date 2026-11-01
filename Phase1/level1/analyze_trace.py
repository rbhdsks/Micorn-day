#!/usr/bin/env python3
"""Address-only trace analysis. Python standard library; no cache/timing model."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def parse_address(value):
    value = value.strip()
    address = int(value, 16 if value.lower().startswith('0x') else 10)
    if address < 0:
        raise ValueError('addresses must be nonnegative')
    return address


def read_addresses(path, trace_format):
    with Path(path).open(newline='') as source:
        if trace_format == 'csv':
            reader = csv.DictReader(source)
            if not reader.fieldnames or 'address' not in reader.fieldnames:
                raise ValueError('CSV must have an address column')
            for row_number, row in enumerate(reader, 2):
                try:
                    yield parse_address(row['address'])
                except (ValueError, AttributeError, TypeError) as exc:
                    raise ValueError(f'row {row_number}: invalid address') from exc
        else:
            for row_number, row in enumerate(source, 1):
                value = row.split('#', 1)[0].strip()
                if value:
                    try:
                        yield parse_address(value)
                    except ValueError as exc:
                        raise ValueError(f'line {row_number}: invalid address') from exc


def top_counts(counts, name, limit=10):
    return [{name: key, 'count': count} for key, count in counts.most_common(limit)]


def analyze(addresses, line_size=64, region_size=4096):
    if line_size <= 0 or line_size & (line_size - 1):
        raise ValueError('line size must be a positive power of two')
    if region_size < line_size or region_size % line_size:
        raise ValueError('region size must be a multiple of line size and at least one line')
    lines, regions, deltas, transitions, gaps = (Counter() for _ in range(5))
    last_seen = {}
    previous = None
    count = same_line = 0
    minimum = maximum = None
    for index, address in enumerate(addresses):
        if address < 0:
            raise ValueError('addresses must be nonnegative')
        line = address // line_size
        count += 1
        minimum = address if minimum is None else min(minimum, address)
        maximum = address if maximum is None else max(maximum, address)
        lines[line] += 1
        regions[address // region_size] += 1
        if previous is not None:
            delta = line - previous
            deltas[delta] += 1
            if delta == 0:
                same_line += 1
            else:
                transitions[delta] += 1
        if line in last_seen:
            gaps[index - last_seen[line]] += 1
        last_seen[line] = index
        previous = line
    if not count:
        raise ValueError('trace contains no accesses')
    reuse_count = sum(gaps.values())
    return {
        'accesses': count,
        'line_size_bytes': line_size,
        'region_size_bytes': region_size,
        'unique_cache_lines': len(lines),
        'touched_line_footprint_bytes': len(lines) * line_size,
        'minimum_byte_address': minimum,
        'maximum_byte_address': maximum,
        'adjacent_same_line_accesses': same_line,
        'adjacent_same_line_fraction': same_line / (count - 1) if count > 1 else None,
        'accesses_to_previously_seen_line': reuse_count,
        'mean_reuse_gap_accesses': sum(gap * n for gap, n in gaps.items()) / reuse_count if reuse_count else None,
        'top_line_access_counts': top_counts(lines, 'line_number'),
        'top_line_deltas': top_counts(deltas, 'delta_lines'),
        'top_nonzero_line_deltas': top_counts(transitions, 'delta_lines'),
        'top_reuse_gaps': top_counts(gaps, 'gap_accesses'),
        'top_regions': top_counts(regions, 'region_number'),
    }


def markdown_report(result):
    rows = '\n'.join(f'| {key} | {value} |' for key, value in result.items() if not isinstance(value, list))
    text = '# Trace analysis\n\n| Measurement | Value |\n|---|---|\n' + rows + '\n'
    for key, label in [('top_line_access_counts', 'Most accessed lines'), ('top_line_deltas', 'Consecutive line deltas'), ('top_nonzero_line_deltas', 'Line transitions (zero deltas excluded)'), ('top_reuse_gaps', 'Reuse gaps'), ('top_regions', 'Most accessed regions')]:
        records = result[key]
        text += f'\n## {label}\n\n'
        if records:
            column = next(iter(records[0]))
            text += f'| {column} | count |\n|---|---|\n'
            text += ''.join(f'| {row[column]} | {row["count"]} |\n' for row in records)
        else:
            text += 'No observations.\n'
    return text + '\n## Interpretation limits\n\nEach row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--format', choices=['text', 'csv'], required=True)
    parser.add_argument('--line-size', type=int, default=64)
    parser.add_argument('--region-size', type=int, default=4096)
    parser.add_argument('--output', type=Path, required=True, help='directory for summary.json and report.md')
    args = parser.parse_args()
    try:
        result = analyze(read_addresses(args.trace, args.format), args.line_size, args.region_size)
        result['source_path'] = str(args.trace.resolve())
        result['trace_format'] = args.format
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
        (args.output / 'report.md').write_text(markdown_report(result))
    except (ValueError, OSError, csv.Error) as exc:
        parser.exit(2, f'error: {exc}\n')
    print(f'Analysed {result["accesses"]} accesses; reports in {args.output}')


if __name__ == '__main__':
    main()
