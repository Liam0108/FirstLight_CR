"""Re-pin the device-downloaded content update for the 16.635.1 port.

Run AFTER the unmodified 16.635.1 APK was installed on the dedicated Android 12
MuMu instance and the game finished its own content update (lobby reached).

It reads /data/user/0/nullsroyale.rel.free/update/** hashes over root adb and
rewrites:
  native_runner/supported_engine.json  runtime_fingerprint_sha256, runtime_content_version
  native_runner/data/competitive/manifest.json  every "runtime-update/<file>" source hash
Files pinned for 15.535.86 that no longer exist in the new update are dropped
from the runtime-update pin set (listed in the output).

The competitive model catalogs themselves are NOT regenerated: the shipped
checkpoints are frozen to the 15.535.86 card contract, so the resource compiler
will report a mismatch by design. Only the device-content attestation is moved.

Usage: python tools/port_16_635/repin_device_resources.py --adb <adb.exe> --serial 127.0.0.1:<port>
"""
import argparse, json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_UPDATE = '/data/user/0/nullsroyale.rel.free/update'


def adb(args, cmd):
    r = subprocess.run([args.adb, '-s', args.serial, 'shell', cmd], capture_output=True, timeout=300)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    if r.returncode:
        raise SystemExit(out)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', required=True)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    if adb(args, 'id -u').strip() != '0':
        raise SystemExit('root adb required (enable root for the instance, then: adb root)')
    text = adb(args, f'cd {APP_UPDATE} && find . -type f -exec sha256sum {{}} +')
    hashes = {}
    for line in text.splitlines():
        m = re.fullmatch(r'([0-9a-f]{64})\s+\./(.+)', line.strip())
        if m:
            hashes[m.group(2)] = m.group(1)
    if 'fingerprint.json' not in hashes:
        raise SystemExit('fingerprint.json missing: open the game and let it finish updating first')
    fp = json.loads(adb(args, f'cat {APP_UPDATE}/fingerprint.json'))
    engine_path = ROOT / 'native_runner' / 'supported_engine.json'
    engine = json.loads(engine_path.read_text(encoding='utf-8'))
    engine['runtime_fingerprint_sha256'] = hashes['fingerprint.json']
    engine['runtime_content_version'] = fp.get('version', engine['runtime_content_version'])
    # The competitive manifest is SHA-pinned in competitive_data.py; device pins live in their own file.
    pins_path = ROOT / 'native_runner' / 'runtime_update_pins.json'
    pins = {
        'schema': 'firstlight-runtime-update-pins.v1',
        'runtime_content_version': engine['runtime_content_version'],
        'note': 'Device-downloaded content captured from the dedicated VM after the stock game finished updating.',
        'source_files': {f'runtime-update/{k}': v for k, v in sorted(hashes.items())},
    }
    print(f"device files: {len(hashes)}  content version: {engine['runtime_content_version']}")
    print(f"fingerprint.json sha256: {engine['runtime_fingerprint_sha256']}")
    if not args.dry_run:
        engine_path.write_text(json.dumps(engine, indent=2) + '\n', encoding='utf-8')
        pins_path.write_text(json.dumps(pins, indent=2) + '\n', encoding='utf-8')
        print('written', engine_path.name, pins_path.name)


if __name__ == '__main__':
    main()
