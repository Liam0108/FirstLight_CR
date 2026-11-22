"""Apply the 15.535.13 -> 16.635.1 relocation to the probe sources.

Inputs (produced by the analysis tools in this folder's README):
  offsets_15.535.13_to_16.635.1.json  code / vtable / data constants
  field_final.json                    struct field decisions per source line
Usage: python apply_port.py <analysis_dir> <repo_root> <new_libg.so>
"""
import json, re, sys, hashlib, pathlib, struct

A, ROOT, NEWLIB = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
PROBE = ROOT / 'native_runner' / 'probe'
lib = NEWLIB.read_bytes()

OLD_SHA = '110aa2b5cac391c498645e072b0d88729428c2c2845e7e2737ca8ee979059783'
OLD_BID = '90e6f351f0dec4a28b494c3812d2629fd45d5a83'
NEW_SHA = hashlib.sha256(lib).hexdigest()
NEW_BID = '179ac4bd38c205bc5041d372a79f1c2f929b1c30'

def va_to_off(va):
    # first PT_LOAD maps va == file offset for the text segment of this libg
    return va

# ---------------- code / data constants ----------------
offs = json.loads((A / 'offsets_15.535.13_to_16.635.1.json').read_text(encoding='utf-8'))
const_new = {}       # (file, name) -> new int (or 0 for removed)
for r in offs['rows']:
    nv = r['new']
    const_new[(r['file'], r['name'])] = int(nv, 16) if nv else 0

# ---------------- struct field decisions ----------------
fields = json.loads((A / 'field_final.json').read_text(encoding='utf-8'))
CONST_OVERRIDE = {
    'kGameAppPendingEventFlagsOffset': 0x1c0, 'kGameAppPendingEventOffset': 0x1c4,
    'kReplayBattleControllerSuspendedOffset': 0x17c,
    'kProjectileDragBackSpeedOffset': 0x1e8,
    'kAreaLifeDurationOffset': 0x148, 'kAreaRadiusOffset': 0x14c,
    'kAreaStayAfterParentDiesOffset': 0x170, 'kAreaFollowBehaviourOffset': 0x1a0,
    'kAttachedCharacterDataOffset': 0x2f8,
    'kResourceFixedValueOffset': 0x2f8,      # LogicPlayer elixir, unchanged
    'kContentPostProcessReadyOffset': 0x720,
}
INLINE_OVERRIDE = {  # (file, receiver, old) -> new
    ('cr_replay_probe.cpp', 'game_app', 0x1bc): 0x1c4,
    ('cr_replay_probe.cpp', 'manager', 0x208): 0x210,
    ('cr_replay_probe.cpp', 'card.card_data', 0x230): 0x268,
    ('combat_event_telemetry.inc', 'base_card_data', 0x230): 0x268,
    ('cr_replay_probe.cpp', 'candidate', 0x2a8): 0x2e0, ('cr_replay_probe.cpp', 'candidate', 0x2b0): 0x2e8,
    ('combat_event_telemetry.inc', 'candidate', 0x2a8): 0x2e0, ('combat_event_telemetry.inc', 'candidate', 0x2b0): 0x2e8,
    ('cr_replay_probe.cpp', 'ability_data', 0xb8): 0xbc,
}
KEEP_FAMILIES = {'champion_controller'}  # aligned evidence was contradictory; runtime-verified instead
edits = {}  # (file, line) -> list of (old, new, kind, name)
for f in fields:
    new = f['new']; old = f['old']
    if f['kind'] == 'field_const' and f['name'] in CONST_OVERRIDE:
        new = CONST_OVERRIDE[f['name']]
    key = (f['file'], f['name'].strip(), old)
    if key in INLINE_OVERRIDE:
        new = INLINE_OVERRIDE[key]
    if f['how'].endswith(':champion_controller'):
        new = old
    if new is None or new == old:
        continue
    edits.setdefault((f['file'], f['line']), []).append((old, new, f['kind'], f['name']))
# helper calls not covered by the inventory patterns
LINE_EDITS = [
    ('cr_replay_probe.cpp', r'read_native_vector\(card\.card_data, 0x220,', 'read_native_vector(card.card_data, 0x258,'),
    ('combat_event_telemetry.inc', r'read_native_vector\(base_card_data, 0x220,', 'read_native_vector(base_card_data, 0x258,'),
    # CaptureCharacterRuntime: the three int vectors rotated (active 0x60->0x80, completed 0x70->0x60, elapsed 0x80->0x70)
    ('cr_replay_probe.cpp', r'read_capture_i32_vector\(capture_runtime, 0x60, 0x68, 0x6c,', 'read_capture_i32_vector(capture_runtime, 0x80, 0x88, 0x8c,'),
    ('cr_replay_probe.cpp', r'read_capture_i32_vector\(capture_runtime, 0x70, 0x78, 0x7c,', 'read_capture_i32_vector(capture_runtime, 0x60, 0x68, 0x6c,'),
    ('cr_replay_probe.cpp', r'read_capture_i32_vector\(capture_runtime, 0x80, 0x88, 0x8c,(?=.*elapsed)', 'read_capture_i32_vector(capture_runtime, 0x70, 0x78, 0x7c,'),
]

files = {}
def text(name):
    if name not in files:
        files[name] = (PROBE / name).read_text(encoding='utf-8').split('\n')
    return files[name]

log = []
# 1. scalar constants (code/data)
decl = re.compile(r'^(\s*(?:inline\s+)?constexpr\s+(?:const\s+)?std::\w+\s+(k\w+)\s*=\s*)(0x[0-9a-fA-F]+)(u?;.*)$')
for name in sorted({k[0] for k in const_new} | {k[0] for k in edits}):
    lines = text(name)
    for i, line in enumerate(lines):
        m = decl.match(line)
        if m and (name, m.group(2)) in const_new:
            nv = const_new[(name, m.group(2))]
            width = len(m.group(3)) - 2
            lines[i] = f"{m.group(1)}0x{nv:0{width}x}{m.group(4)}"
            if lines[i] != line: log.append(f'{name}:{i + 1} {m.group(2)} {m.group(3)} -> 0x{nv:0{width}x}')
# 2. struct field literals per line
for (name, ln), lst in edits.items():
    lines = text(name); line = lines[ln - 1]
    for old, new, kind, nm in lst:
        pat = re.compile(r'(?<![0-9a-fA-Fx])0x0*' + format(old, 'x') + r'(?![0-9a-fA-F])', re.I)
        if kind == 'field_const':
            line2 = pat.sub(f'0x{new:x}', line, count=1)
        else:
            # replace the literal that follows the receiver expression
            idx = line.find(nm.strip())
            if idx < 0: idx = 0
            mm = pat.search(line, idx)
            line2 = line if not mm else line[:mm.start()] + f'0x{new:x}' + line[mm.end():]
        if line2 == line:
            log.append(f'!! {name}:{ln} could not place {nm} 0x{old:x}->0x{new:x}')
        else:
            log.append(f'{name}:{ln} {nm.strip()} 0x{old:x} -> 0x{new:x}')
        line = line2
    lines[ln - 1] = line
for name, pat, rep in LINE_EDITS:
    lines = text(name); rx = re.compile(pat); hits = 0
    for i, line in enumerate(lines):
        ctx = line + (lines[i + 1] if i + 1 < len(lines) else '')
        if rx.search(ctx if '(?=' in pat else line):
            lines[i] = re.sub(pat.split('(?=')[0], rep, line, count=1); hits += 1
            if '(?=' not in pat: break
    log.append(f'{name}: {pat} x{hits}')
# 3. regenerate 16-byte prologues / call fingerprints from the new binary
arr = re.compile(r'^(\s*(?:inline\s+)?constexpr\s+std::uint8_t\s+(k\w+?)(Prologue|CallFingerprint|Fingerprint)\[16\]\s*=\s*\{)')
for name in list(set(files) | {p.name for p in PROBE.iterdir() if p.suffix in ('.h', '.inc', '.cpp') and not p.name.startswith('test_')}):
    lines = text(name)
    for i, line in enumerate(lines):
        m = arr.match(line)
        if not m: continue
        base, kind = m.group(2), m.group(3)
        cands = [f'{base}Offset'] if kind == 'Prologue' else [f'{base}CallOffset', f'{base}OnlyCallOffset', f'{base}Offset']
        key = next(((name, c) for c in cands if (name, c) in const_new), None)
        if key is None:
            key = next(((f2, c) for c in cands for f2 in {k[0] for k in const_new} if (f2, c) in const_new), None)
        if key is None or const_new[key] == 0:
            log.append(f'!! {name}:{i + 1} no relocated offset for {base}{kind}'); continue
        va = const_new[key]; b = lib[va_to_off(va):va_to_off(va) + 16]
        body = ', '.join(f'0x{x:02x}' for x in b) + ','
        j = i + 1
        lines[j] = '    ' + body
        log.append(f'{name}:{j + 1} {base}{kind} <- bytes @0x{va:x}')
# 4. attestation strings
for p in PROBE.iterdir():
    if p.suffix in ('.h', '.inc', '.cpp') and not p.name.startswith('test_'):
        lines = text(p.name)
        for i, line in enumerate(lines):
            if OLD_SHA in line or OLD_BID in line:
                lines[i] = line.replace(OLD_SHA, NEW_SHA).replace(OLD_BID, NEW_BID)
for name, lines in files.items():
    (PROBE / name).write_text('\n'.join(lines), encoding='utf-8')
(A / 'apply_port.log').write_text('\n'.join(log), encoding='utf-8')
print(f'edited files: {len(files)}  log lines: {len(log)}  failures: {sum(1 for l in log if l.startswith("!!"))}')
print('\n'.join(l for l in log if l.startswith('!!')))
