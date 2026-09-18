import socket
import json
import sys

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_code_in_blender(code_str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(120.0)
    s.connect(('127.0.0.1', 9876))
    params = {'code': code_str}
    s.sendall(json.dumps({'type': 'execute_code', 'params': params}).encode('utf-8'))
    data = b''
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            res = json.loads(data.decode('utf-8'))
            break
        except Exception:
            continue
    s.close()
    return res

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    res = run_code_in_blender(code)
    print("STATUS:", res.get("status"))
    if res.get("status") == "success":
        out = res.get("result", {}).get("result", "")
        print("OUTPUT:\n", out)
    else:
        print("ERROR:\n", res.get("message"))
