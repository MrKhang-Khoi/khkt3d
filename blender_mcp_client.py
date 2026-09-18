import socket
import json
import time
import sys

def send_blender_command(command, host=localhost, port=9876, timeout=15):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        cmd_bytes = json.dumps(command).encode(utf-8)
        sock.sendall(cmd_bytes)
        
        # Read response
        response_bytes = b"
 while True:
 chunk = sock.recv(8192)
 if not chunk:
 break
 response_bytes += chunk
 try:
 # Check if complete JSON
 res = json.loads(response_bytes.decode(utf-8))
 return res
 except Exception:
 continue
 finally:
 sock.close()

if __name__ == __main__:
 action = sys.argv[1] if len(sys.argv) > 1 else ping
 if action == ping:
 res = send_blender_command({type: ping})
 print(Ping result:, res)
 elif action == exec:
 code_file = sys.argv[2]
 with open(code_file, r, encoding=utf-8) as f:
 code_text = f.read()
 res = send_blender_command({type: execute_code, params: {code: code_text}})
 print(Exec result:, res)
