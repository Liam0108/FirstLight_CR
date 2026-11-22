"""Rewrite hard-coded 15.535.13 libg addresses in the Python runner to 16.635.1.

Usage: python port_python_offsets.py <analysis_dir> <repo_root> [--dry-run]
analysis_dir must contain offsets_15.535.13_to_16.635.1.json and func_map.json.
"""
import json, pathlib, re, sys

A, ROOT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dry = '--dry-run' in sys.argv
rows = json.loads((A / 'offsets_15.535.13_to_16.635.1.json').read_text(encoding='utf-8'))['rows']
exact = {}
for r in rows:
    if r.get('new'):
        exact[int(r['old'], 16)] = int(r['new'], 16)
# manual decisions that differ from / extend the table
exact.update({0xF23110: 0x1080784, 0x1894588: 0x1A47298, 0x189E738: 0x1A51EC0})
# mid-function sites resolved by call-site / instruction alignment (midmap.py)
exact.update({0xF12D54: 0x106F900, 0xF2FFFC: 0x108D87C, 0xF5D16C: 0x10BB1CC,
              0xF5D314: 0x10BB470, 0xF5DA94: 0x10BBB2C})
# edges that no longer exist in 16.635.1 (inlined helper / tail call): never-matching sentinel
SENTINEL = (1 << 64) - 1
exact.update({0xF19314: SENTINEL, 0xF18FF4: SENTINEL, 0xF18FF0: SENTINEL, 0xF20DF0: SENTINEL})
fm = {int(k): v for k, v in json.loads((A / 'func_map.json').read_text()).items()}
call_sites = {o: n for o, n in exact.items()}

def map_addr(v):
    if v in exact: return exact[v], 'table'
    if v - 4 in call_sites: return call_sites[v - 4] + 4, 'return-after-call'
    if v in fm: return fm[v], 'function-map'
    return None, None

pat = re.compile(r'0x0*([0-9a-fA-F]{5,8})\b')
unresolved = []; changed = 0
for p in sorted((ROOT / 'native_runner').rglob('*.py')):
    if 'tests' in p.parts or 'resource_compiler' in p.parts: continue
    lines = p.read_text(encoding='utf-8').split('\n'); dirty = False
    for i, line in enumerate(lines):
        def rep(m):
            global changed
            v = int(m.group(1), 16)
            if not (0x700000 <= v < 0x1A00000): return m.group(0)
            nv, how = map_addr(v)
            if nv is None:
                unresolved.append(f'{p.relative_to(ROOT)}:{i + 1} 0x{v:x} | {line.strip()[:110]}'); return m.group(0)
            changed += 1
            upper = any(c.isupper() for c in m.group(1))
            s = f'{nv:X}' if upper else f'{nv:x}'
            return '0x' + s
        new = pat.sub(rep, line)
        if new != line: lines[i] = new; dirty = True
    if dirty and not dry: p.write_text('\n'.join(lines), encoding='utf-8')
print('replaced', changed, 'unresolved', len(unresolved))
print('\n'.join(unresolved))
