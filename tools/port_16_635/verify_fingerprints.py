"""Check every 16-byte prologue / call fingerprint in the probe sources against a libg.so.

Usage: python verify_fingerprints.py <probe_dir> <libg.so>
For each array k<Base>{Prologue,CallFingerprint}[16], look up the matching
k<Base>Offset / k<Base>CallOffset / k<Base>OnlyCallOffset constant and compare bytes.
"""
import pathlib, re, sys
probe, lib = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).read_bytes()
src = {p.name: p.read_text(encoding='utf-8') for p in probe.iterdir()
       if p.suffix in ('.h', '.inc', '.cpp') and not p.name.startswith('test_')}
consts = {}
for name, t in src.items():
    for m in re.finditer(r'constexpr\s+std::uintptr_t\s+(k\w+)\s*=\s*(0x[0-9a-fA-F]+)', t):
        consts.setdefault(m.group(1), int(m.group(2), 16))
bad = ok = skipped = 0
for name, t in src.items():
    for m in re.finditer(r'constexpr\s+std::uint8_t\s+(k\w+?)(Prologue|CallFingerprint)\[16\]\s*=\s*\{([^}]*)\}', t):
        base, kind = m.group(1), m.group(2)
        want = bytes(int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})', m.group(3)))
        keys = ([base + 'OnlyCallOffset', base + 'CallOffset'] if kind == 'CallFingerprint' else []) + \
               [base + 'Offset', base + 'FunctionOffset', base + 'CallOffset', base + 'OnlyCallOffset']
        if base == 'kCombatTerminal': keys.insert(0, 'kCombatProjectileTerminalOffset')
        va = next((consts[k] for k in keys if k in consts), None)
        if va is None or va == (1 << 64) - 1:
            skipped += 1; print(f'skip  {name}: {base}{kind} (no offset)'); continue
        got = lib[va:va + 16]
        if got == want: ok += 1
        else:
            bad += 1; print(f'BAD   {name}: {base}{kind} @0x{va:x}\n      want {want.hex()}\n      got  {got.hex()}')
print(f'ok={ok} bad={bad} skipped={skipped}')
sys.exit(1 if bad else 0)
