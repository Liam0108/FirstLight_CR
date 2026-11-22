"""Re-pin the Python-side runtime identity to the 16.635.1 engine.

Chain: runtime.json (content version / content manifest sha1 / libg build id)
  -> manifest.json files.runtime.{sha256,bytes}
  -> competitive_data.MANIFEST_SHA256
plus EXACT_LIBG_* constants in phase_runtime.py / visibility_runtime.py.
Card/effect/model catalogs are untouched (the shipped checkpoints are frozen to them).
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2] / 'native_runner'
NEW = dict(content_version='16.635.93',
           content_manifest_sha1='b54188c6d2744af7c28adcd436be73f120915c44',
           libg_build_id='179ac4bd38c205bc5041d372a79f1c2f929b1c30')
OLD = dict(content_version='15.535.86',
           content_manifest_sha1='41d8df308b22bf144c2a4f2b75f6e6fbf69a0c82',
           libg_build_id='90e6f351f0dec4a28b494c3812d2629fd45d5a83')
OLD_LIBG = '110aa2b5cac391c498645e072b0d88729428c2c2845e7e2737ca8ee979059783'
NEW_LIBG = '0b580222e5a3502cf153bb5e6297ec32d2b154b605b777c74873dd75722e4eaa'

def sub_once(text, old, new, what):
    if text.count(old) != 1:
        sys.exit(f'{what}: expected exactly one occurrence of {old!r}, found {text.count(old)}')
    return text.replace(old, new)

rt_path = ROOT / 'data' / 'competitive' / 'runtime.json'
rt = rt_path.read_bytes().decode('utf-8')
old_rt_sha = hashlib.sha256(rt.encode('utf-8')).hexdigest()
for k in NEW:
    rt = sub_once(rt, f'"{k}": "{OLD[k]}"', f'"{k}": "{NEW[k]}"', 'runtime.json')
rt_bytes = rt.encode('utf-8')
rt_path.write_bytes(rt_bytes)
new_rt_sha = hashlib.sha256(rt_bytes).hexdigest()

mf_path = ROOT / 'data' / 'competitive' / 'manifest.json'
mf = mf_path.read_bytes().decode('utf-8')
old_mf_sha = hashlib.sha256(mf.encode('utf-8')).hexdigest()
mf = sub_once(mf, old_rt_sha, new_rt_sha, 'manifest.json runtime sha')
m = re.search(r'("runtime":\s*\{[^}]*"bytes":\s*)(\d+)', mf)
if m:
    mf = mf[:m.start(2)] + str(len(rt_bytes)) + mf[m.end(2):]
mf_bytes = mf.encode('utf-8')
mf_path.write_bytes(mf_bytes)
new_mf_sha = hashlib.sha256(mf_bytes).hexdigest()

cd_path = ROOT / 'competitive_data.py'
cd = cd_path.read_text(encoding='utf-8')
cd = sub_once(cd, old_mf_sha, new_mf_sha, 'competitive_data.MANIFEST_SHA256')
cd_path.write_text(cd, encoding='utf-8')

for name in ('phase_runtime.py', 'visibility_runtime.py'):
    p = ROOT / name; t = p.read_text(encoding='utf-8')
    t = sub_once(t, OLD_LIBG, NEW_LIBG, name); t = sub_once(t, OLD['libg_build_id'], NEW['libg_build_id'], name)
    p.write_text(t, encoding='utf-8')
print('runtime.json', old_rt_sha[:12], '->', new_rt_sha[:12])
print('manifest.json', old_mf_sha[:12], '->', new_mf_sha[:12])
