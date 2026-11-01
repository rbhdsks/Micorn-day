"""Validate measured RTL records and render deterministic comparison outputs."""
from collections import defaultdict
from pathlib import Path
import csv

POLICIES = ('none', 'next_line', 'stride')
REQUIRED = ('accesses','hits','misses','prefetch_issued','timely_useful','late_useful',
            'unused_evicted','resident_unconsumed','dram_reads','completion_cycles',
            'quiescent_cycles','latency_sum','max_latency','offer_latency_sum',
            'max_offer_latency','request_wait_cycles','total_compute_gap_cycles')


def read_measurement(path, expected_accesses, prefetch):
    with Path(path).open(newline='') as source:
        records=list(csv.DictReader(source))
    if len(records)!=1 or not all(key in records[0] for key in REQUIRED):
        raise ValueError('expected one RTL result with complete measured metric fields')
    row={key:int(value) for key,value in records[0].items()}
    if any(value<0 for value in row.values()):
        raise ValueError('negative measured counters are invalid')
    if row['accesses']!=expected_accesses or row['accesses']!=row['hits']+row['misses']:
        raise ValueError('demand classification mismatch')
    if row['prefetch_issued']!=sum(row[k] for k in ('timely_useful','late_useful','unused_evicted','resident_unconsumed')):
        raise ValueError('prefetch outcomes do not conserve at quiescence')
    if not prefetch and row['prefetch_issued']:
        raise ValueError('disabled prefetch mode generated requests')
    if row['completion_cycles']<=0 or row['quiescent_cycles']<row['completion_cycles']:
        raise ValueError('invalid completion/drain cycle accounting')
    if row['dram_reads']<row['prefetch_issued']:
        raise ValueError('total DRAM count excludes prefetch traffic')
    return row


def summarize(measurements):
    grouped=defaultdict(dict)
    for record in measurements:
        if record['policy'] in grouped[record['workload']]:
            raise ValueError('duplicate workload/policy measurement')
        grouped[record['workload']][record['policy']]=record
    summaries=[]
    for name,modes in sorted(grouped.items()):
        if set(modes)!=set(POLICIES):
            raise ValueError('every workload requires all three RTL policies')
        baseline=modes['none']
        n=baseline['accesses']
        for policy in POLICIES:
            row=modes[policy]
            if row['accesses']!=n:
                raise ValueError('paired modes used different demand counts')
            issued=row['prefetch_issued']
            summaries.append({
                'workload':name,'trace_kind':row['trace_kind'],'policy':policy,
                'accesses':n,'hits':row['hits'],'misses':row['misses'],
                'demand_hit_rate':row['hits']/n,'demand_miss_rate':row['misses']/n,
                'mean_accept_to_response_cycles':row['latency_sum']/n,
                'mean_offer_to_response_cycles':row['offer_latency_sum']/n,
                'max_accept_to_response_cycles':row['max_latency'],
                'max_offer_to_response_cycles':row['max_offer_latency'],
                'request_wait_cycles':row['request_wait_cycles'],
                'prefetch_issued':issued,'timely_useful':row['timely_useful'],
                'late_useful':row['late_useful'],'unused_evicted':row['unused_evicted'],
                'resident_unconsumed':row['resident_unconsumed'],
                'prefetch_consumption_accuracy':(row['timely_useful']+row['late_useful'])/issued if issued else '',
                'dram_reads':row['dram_reads'],
                'dram_bytes':16*row['dram_reads'],
                'dram_overhead_fraction':row['dram_reads']/baseline['dram_reads']-1,
                'completion_cycles':row['completion_cycles'],
                'quiescent_cycles':row['quiescent_cycles'],
                'speedup':baseline['completion_cycles']/row['completion_cycles'],
                'quiescent_speedup':baseline['quiescent_cycles']/row['quiescent_cycles'],
                'total_compute_gap_cycles':row['total_compute_gap_cycles'],
            })
    return summaries


def markdown_report(rows, geometry, latency):
    text=['# Phase 1 measured RTL comparison','',
          f'Cache: {16*(1<<geometry)} data bytes, {1<<geometry} direct-mapped lines, 16 bytes per line. Memory model LATENCY={latency}; this is an internal countdown parameter, not physical DRAM latency.','',
          'All three modes replay the same demand addresses, post-response gaps, response-stall schedule and cache/memory geometry. none disables speculation; next_line and stride use distinct candidate generators through the same controller. Every returned word is checked against the deterministic backing-memory reference.','',
          '## Completion cycles and latency','',
          '| Trace | Policy | Demand hit rate | Mean accept→response | Mean offer→response | Completion cycles | Speedup | DRAM reads |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        text.append(f"| {row['workload']} | {row['policy']} | {row['demand_hit_rate']:.2%} | {row['mean_accept_to_response_cycles']:.3f} | {row['mean_offer_to_response_cycles']:.3f} | {row['completion_cycles']} | {row['speedup']:.3f}× | {row['dram_reads']} |")
    text+=['','## Prefetch outcomes','',
           '| Trace | Policy | Issued | Timely | Late | Unused evicted | Resident | Consumption accuracy | DRAM overhead |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        accuracy=f"{row['prefetch_consumption_accuracy']:.2%}" if row['prefetch_consumption_accuracy']!='' else 'N/A'
        text.append(f"| {row['workload']} | {row['policy']} | {row['prefetch_issued']} | {row['timely_useful']} | {row['late_useful']} | {row['unused_evicted']} | {row['resident_unconsumed']} | {accuracy} | {row['dram_overhead_fraction']:+.2%} |")
    text+=['','## Definitions and interpretation limits','',
      '- Demand hit rate = demand hits / total demand accesses. Prefetch transactions are never added to either demand count.',
      '- Speedup = no-prefetch completion cycles / policy completion cycles. Completion ends at final demand response consumption and excludes the final unused compute gap. Earlier gaps and consumer stalls remain part of the offered workload.',
      '- quiescent_cycles additionally includes bounded natural draining of predictor/candidate/controller state; no fixed padding is added. summary.csv publishes both cycle definitions and both ratios.',
      '- Accept-to-response latency ends when data becomes available and excludes consumer stalls afterward. Offer-to-response additionally includes request waiting before acceptance. Consumer stalls still affect completion cycles.',
      '- The driver serializes reads, then waits the trace gap. Gap zero does not mean a fully pipelined one-request-per-cycle processor.',
      '- Consumption accuracy = (first timely consumption + late consumption) / issued prefetch reads. Resident lines remain unresolved but stay in the denominator. N/A means no prefetch was issued.',
      '- At quiescence: issued = timely + late + unused evicted + resident. Raw run CSVs record all terms. unused_evicted is not by itself a measurement of demand-cache pollution.',
      '- Total memory traffic includes demand and prefetch reads. Bytes = 16 × transactions for this fixed-line simulation, not measured DDR bandwidth.',
      '- Synthetic patterns are diagnostic examples. modelled_matmul traces preserve only logical immutable A/B compute reads from Nitesh’s Level 1 generator; C, writes and initialization are excluded. They are not captured instructions, a complete inference trace or application timing.',
      '- Matmul numeric correctness is checked by the Level 1 generator. RTL replay uses address-derived memory words, so it checks data transport rather than executing the numeric matmul.',
      '- One fixed irregular seed is provided. Deterministic reruns establish reproducibility, not statistical confidence or a universal speedup.',
      '- Phase 1 intentionally retains direct-map speculative insertion and a global single-stride predictor. Pollution, useless short-burst predictions and interleaved-stream failures are exposed, not hidden. Buffering/feedback upgrades belong to Phase 2.',
      '- Comparisons against the older audited package need care: old cycle counts included fixed drains and the final gap. The cycle definition here is explicitly different.',
      '', '## Evidence files','',
      '`summary.csv` contains full derived metrics. `runs/` contains each simulator CSV and transcript. `analysis/` contains 16-byte-line Level 1 summaries. `traces/manifest.json` records provenance and checksums. `provenance.json` records commands, parameters, source hashes and tool versions.', '']
    return '\n'.join(text)


def write_outputs(directory, rows, geometry, latency):
    directory=Path(directory)
    with (directory/'summary.csv').open('w',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=rows[0])
        writer.writeheader();writer.writerows(rows)
    (directory/'report.md').write_text(markdown_report(rows,geometry,latency))
