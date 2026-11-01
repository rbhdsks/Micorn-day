# Level 3 bounded context strategy

Context means address region and separately evaluated mature outcomes. It does not mean tensor semantics, a program counter or a trained CDM. The selected validation variant uses regional history with the outcome gate disabled. [The debate](../research/context_debate.md) explains both the case for context awareness and its limits.

For each accepted demand line, look up one of four4KiB region keys. On an unseen key, allocate an invalid entry or replace round-robin. Ignore the same line as its own preceding observation. Otherwise compute a signed delta. If it differs from the stored stride, retain it and set confidence1. If it repeats, saturate confidence upward; old confidence at least1 qualifies one candidate at current line plus stride. Reject negative or out-of-range28-bit line addresses.

```text
observe(line):
    entry = lookup(region(line))
    if missing: allocate(last=line, stride=0, confidence=0); return
    if line == entry.last: return
    delta = signed(line) - signed(entry.last)
    prediction = signed(line) + entry.stride
    if delta != 0 and delta == entry.stride:
        if old_confidence >= 1 and enabled and in_bounds(prediction): propose(prediction)
        confidence = min(3, old_confidence + 1)
    else:
        stride = delta; confidence = 1
    last = line
```

The controller filters cached/buffered lines and chooses pending demand before speculation. It keeps one advisory candidate and may lose a simultaneous new candidate when consuming an old one. This is opportunity loss, not incorrect demand data. A selected transaction is nonpreemptible.

The optional global gate starts at2, increases on timely/late first consumption, decreases on unused replacement and saturates at0/3. Resident unresolved entries supply no training event. At zero,16 accepted demands permit a recovery probe. Training continues while selection is suppressed. The gate measures coarse frequency, not expected time saved. The test suite covers saturation, disable, residents and recovery.

Regional history helps separable streams. Same-region objects, boundary retraining, table pressure, global gate coupling and short bursts remain failure modes. The complete ablations and counterexamples stay visible in [Level5](../level5/README.md).
