#!/usr/bin/env python3
"""Untimed, demand-only model of the Phase 1 direct-mapped read cache.

This model checks placement, identity, replacement, word selection and counts.
Misses fill immediately: it has no prefetcher, memory latency or ready/valid FSM.
Use the Level 5 RTL replay for timing and prefetch performance measurements.
"""
import argparse
import csv
import json
from pathlib import Path
import re

LINE_BYTES = 16
WORD_BYTES = 4
MAX_TRACE_ROWS = 65536
ADDRESS = re.compile(r'0x[0-9a-fA-F]+\Z')
DEMO_ADDRESSES = (0x1000, 0x1004, 0x100c, 0x1010, 0x1000, 0x1400, 0x1000)


def validate_address(address):
    if type(address) is not int or not 0 <= address <= 0xffffffff or address % WORD_BYTES:
        raise ValueError('address must be an aligned unsigned 32-bit byte address')
    return address


def word_at(address):
    """Independent deterministic backing-data convention shared with RTL tests."""
    return (validate_address(address) >> 2) ^ 0xcafe1234


class DirectMappedCache:
    """One 16-byte line per index; demand misses unconditionally replace a slot."""

    def __init__(self, index_bits=6):
        if type(index_bits) is not int or not 1 <= index_bits <= 12:
            raise ValueError('model supports practical index_bits in 1..12')
        self.index_bits = index_bits
        self.line_count = 1 << index_bits
        self.reset()

    def reset(self):
        self._tags = [None] * self.line_count
        self._data = [None] * self.line_count
        self.accesses = self.hits = self.misses = 0

    def decode(self, address):
        address = validate_address(address)
        line = address >> 4
        return {'address': address, 'line_identity': line,
                'index': line & (self.line_count - 1),
                'conventional_tag': line >> self.index_bits,
                'word_offset': (address >> 2) & 3,
                'aligned_line_address': line << 4}

    def read(self, address):
        mapping = self.decode(address)
        index, line = mapping['index'], mapping['line_identity']
        old = self._tags[index]
        hit = old == line
        self.accesses += 1
        if hit:
            self.hits += 1
        else:
            self.misses += 1
            self._tags[index] = line
            base = mapping['aligned_line_address']
            self._data[index] = tuple(word_at(base + WORD_BYTES * word) for word in range(4))
        return {**mapping, 'hit': hit,
                'event': 'resident_hit' if hit else 'empty_slot_fill' if old is None else 'replacement_fill',
                'evicted_line_identity': old if not hit and old is not None else None,
                'data': self._data[index][mapping['word_offset']]}

    def summary(self):
        return {'model': 'untimed demand-only direct mapping; immediate demand refill',
                'index_bits': self.index_bits, 'line_bytes': LINE_BYTES,
                'line_count': self.line_count, 'data_capacity_bytes': self.line_count * LINE_BYTES,
                'accesses': self.accesses, 'hits': self.hits, 'misses': self.misses,
                'demand_hit_rate': self.hits / self.accesses if self.accesses else None,
                'demand_dram_reads': self.misses,
                'counter_semantics': 'unbounded Python counts; hardware counters wrap at 32 bits',
                'timing_or_prefetch_modelled': False}


def simulate(addresses, index_bits=6):
    cache = DirectMappedCache(index_bits)
    events = [cache.read(address) for address in addresses]
    if not events:
        raise ValueError('input contains no demand reads')
    return {'summary': cache.summary(), 'events': events}


def read_addresses(path):
    """Read the strict Level 5 address,gap format; validate but ignore timing gaps."""
    addresses = []
    with Path(path).open(newline='') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ['address', 'gap']:
            raise ValueError('trace header must be exactly address,gap')
        for number, row in enumerate(reader, 2):
            value, gap = row.get('address'), row.get('gap')
            if None in row or not isinstance(value, str) or not ADDRESS.fullmatch(value):
                raise ValueError(f'row {number}: address requires an explicit lowercase 0x prefix')
            if not isinstance(gap, str) or not re.fullmatch(r'[0-9]+', gap) or int(gap) > 100000:
                raise ValueError(f'row {number}: gap must be an integer in 0..100000')
            try:
                addresses.append(validate_address(int(value, 16)))
            except ValueError as exc:
                raise ValueError(f'row {number}: {exc}') from exc
            if len(addresses) > MAX_TRACE_ROWS:
                raise ValueError(f'trace exceeds {MAX_TRACE_ROWS} rows')
    if not addresses:
        raise ValueError('trace contains no demand reads')
    return addresses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--demo', action='store_true', help='walk through word hits and a direct-map conflict')
    source.add_argument('--trace', type=Path, help='strict address,gap CSV; gaps are ignored by this untimed model')
    parser.add_argument('--index-bits', type=int, default=6)
    parser.add_argument('--output', type=Path, help='write summary and per-access mapping/events as JSON')
    args = parser.parse_args()
    try:
        addresses = DEMO_ADDRESSES if args.demo else read_addresses(args.trace)
        result = simulate(addresses, args.index_bits)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + '\n')
        if args.demo:
            print('Address     Line       Index Word Hit   Evicted line')
            for event in result['events']:
                victim = event['evicted_line_identity']
                print(f"0x{event['address']:08x} 0x{event['line_identity']:07x} {event['index']:5} {event['word_offset']:4} {str(event['hit']):5} "
                      f"{'-' if victim is None else hex(victim)}")
        print(json.dumps(result['summary'], indent=2))
    except (ValueError, OSError, csv.Error) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
