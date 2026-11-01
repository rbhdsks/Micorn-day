"""Strict read-only trace interchange for the Phase 1 RTL replay harness."""
from dataclasses import dataclass
from pathlib import Path
import csv
import re

MAX_ROWS = 65536
MAX_GAP = 100000
ADDRESS_RE = re.compile(r'0x[0-9a-fA-F]+\Z')

@dataclass(frozen=True)
class TraceRow:
    address: int
    gap: int

    def __post_init__(self):
        if type(self.address) is not int or not 0 <= self.address <= 0xffffffff or self.address % 4:
            raise ValueError('address must be an aligned unsigned 32-bit byte address')
        if type(self.gap) is not int or not 0 <= self.gap <= MAX_GAP:
            raise ValueError(f'gap must be an integer in 0..{MAX_GAP}')


def read_trace(path):
    rows = []
    with Path(path).open(newline='') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ['address', 'gap']:
            raise ValueError('trace header must be exactly address,gap')
        for number, record in enumerate(reader, 2):
            address = record.get('address', '')
            gap = record.get('gap', '')
            if None in record or not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
                raise ValueError(f'row {number}: address requires explicit lowercase 0x prefix')
            if not isinstance(gap, str) or not re.fullmatch(r'[0-9]+', gap):
                raise ValueError(f'row {number}: gap requires a nonnegative decimal integer')
            try:
                rows.append(TraceRow(int(address, 16), int(gap)))
            except ValueError as exc:
                raise ValueError(f'row {number}: {exc}') from exc
            if len(rows) > MAX_ROWS:
                raise ValueError(f'trace exceeds {MAX_ROWS} rows')
    if not rows:
        raise ValueError('trace contains no requests')
    return rows


def write_trace(path, rows):
    rows = list(rows)
    if not rows or len(rows) > MAX_ROWS or any(not isinstance(row, TraceRow) for row in rows):
        raise ValueError(f'trace requires 1..{MAX_ROWS} validated TraceRow entries')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as target:
        writer = csv.writer(target)
        writer.writerow(['address', 'gap'])
        writer.writerows((f'0x{row.address:08x}', row.gap) for row in rows)
    return rows


def write_mem(path, rows):
    Path(path).write_text(''.join(f'{row.address:08x}{row.gap:08x}\n' for row in rows))
