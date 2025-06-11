import network
import socket
import time
import dht
from machine import Pin
from puda import vlhkost_pudy

# DHT11 senzor
sensor = dht.DHT11(Pin(14))

# Relé na GPIO15
rele = Pin(15, Pin.OUT)

#minimalní vlhkost půdy
min_vlhkost = 30
# Wi-Fi připojení
ssid = 'bbbb'
password = '12345678'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.isconnected():
        break
    print('Čekám na připojení...', max_wait)
    max_wait -= 1
    time.sleep(1)

if not wlan.isconnected():
    raise RuntimeError('Wi-Fi nefunguje / timeout')
else:
    ip = wlan.ifconfig()[0]
    print('Připojeno, IP =', ip)

# HTTP server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Server běží na', ip, 'portu 80')

while True:
    cl, peer = s.accept()
    print('Připojení od', peer)
    request = cl.recv(1024).decode()

    # tlačítko na relé na webu
    if '/pump_on' in request:
        rele.value(1) 
        time.sleep(5)
        rele.value(0)
        response = 'HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n'
        cl.send(response.encode())
        cl.close()
        continue

    # Změření hodnot
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    procento = vlhkost_pudy()

    if procento < min_vlhkost: # automaticke zalevání
        rele.value(1) 
        time.sleep(5)
        rele.value(0) 
        
    # Vygenerování HTML
    try:
        with open("index.html", "r") as f:
            html = f.read()
        html = html.replace("{{teplota}}", str('%3.1f °C' % temp))
        html = html.replace("{{vlhkost}}", str('%3.1f %%' % hum))
        html = html.replace("{{puda_procenta}}", str(procento) + " %")
    except:
        html = "<h1>Chyba při načtení index.html</h1>"

    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html
    cl.send(response.encode())
    cl.close()
