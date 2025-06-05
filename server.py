import network
import socket
import time
import sys
import dht
from machine import Pin
from puda import vlhkost_pudy
#dht
sensor=dht.DHT11(Pin(14))
#Nastavení Wi-Fi 
ssid = 'bbbb'
password = '12345678'
#relé
rele = Pin(15, Pin.OUT)
rele.value(1)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#Čekání na připojení
max_wait = 10
while max_wait > 0:
    if wlan.isconnected():
        break
    print('cekam na pripojeni', max_wait)
    max_wait -= 1
    time.sleep(1)

#Kontrola připojení
if not wlan.isconnected():
    raise RuntimeError('nefunguje/timeout')
else:
    ip = wlan.ifconfig()[0]
    print('Připojeno, IP =', ip)

#Nastavení HTTP serveru
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Server bezi na', ip, 'portu 80')

def load_html():
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except Exception as e:
        print('Chyba pri cteni index.html:', e)
        return '<h1>Chyba: nelze nacist index.html</h1>'

while True:
    cl, peer = s.accept()
    print('Připojení od', peer)
    cl_file = cl.makefile('rwb', 0)
    # Přečteme a ignorujeme HTTP hlavičky z requestu
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    #vypocty pro dht, vlhkost pudy a zapnuti rele
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    procento = vlhkost_pudy()
    time.sleep(5)
    rele.value(0)

    # Nacteni html a zobrazení hodnot
    with open("index.html") as f:
        html = f.read()
        html = html.replace("{{teplota}}", str('%3.1f °C' %temp))
        html = html.replace("{{vlhkost}}", str('%3.1f %%' %hum))
        html = html.replace("{{puda_procenta}}", str(procento) + " %")

    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html
    cl.send(response.encode())
    cl.close()
