import network
import socket
import time
import sys
ssid = 'bbbb'
password = '12345678'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >=3:
        break
    max_wait -=1
    print('cekam')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('nepodařilo se připojit')
else:
    print('připojeno')
    ip = wlan.ifconfig()[0]
    print( 'ip = '+ ip)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('server beží na', ip)

def html():
    with open('index.html', 'r') as file:
        return file.read()

while True:
    cl, addr = s.accept()
    print('pripojeni od', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n'
    cl.send(response.encode('utf-8'))
    html_content = html()
    cl.send(html_content.encode('utf-8'))
    cl.close()
