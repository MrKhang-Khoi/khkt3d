import socket
import json
import sys

def capture_viewport(filepath):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30.0)
    s.connect(('127.0.0.1', 9876))
    params = {'filepath': filepath}
    s.sendall(json.dumps({'type': 'get_viewport_screenshot', 'params': params}).encode('utf-8'))
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
    fp = sys.argv[1] if len(sys.argv) > 1 else r'c:\Users\HPZBook\Desktop\TEST_BLENDER\viewport_shot.png'
    res = capture_viewport(fp)
    print("RESULT:", res)
