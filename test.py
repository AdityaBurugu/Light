import socket
import json
import time
LightContrlInfo = {
    'IPAddr': '192.168.1.60',
    'Channel': 'Only Right',
    'Status': 'OFF'
}
sock = socket.socket()
sock.connect(('192.168.1.150', 5556))
xx = json.dumps(LightContrlInfo)
sock.send(bytes(xx, encoding="utf-8"))
#sock.send(b'Bhaskar')
time.sleep(2)