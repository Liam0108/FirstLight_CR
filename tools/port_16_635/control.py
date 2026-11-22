"""Send one raw control command to the running offline engine (port diagnostics).
Usage: python tools/port_16_635/control.py "debug-player-dump" [port]"""
import socket, sys
from native_runner.cr_native_env import DEFAULT_HOST, DEFAULT_PORT
port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
with socket.create_connection((DEFAULT_HOST, port), timeout=10) as c:
    c.sendall(sys.argv[1].encode() + b'\n')
    data = b''
    while not data.endswith(b'\n'):
        chunk = c.recv(65536)
        if not chunk: break
        data += chunk
print(data.decode('utf-8', 'replace'))
