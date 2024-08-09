import network
import socket
import time
from machine import Pin, ADC
#import mdns  # Kontrollera att mdns-modulen är tillgänglig

# Ditt WiFi-nätverks namn (SSID) och lösenord
SSID = 'Tele2_24BB96'
PASSWORD = 'uei3rt7j'
HOSTNAME = 'PicoTemp'

# Statisk IP-konfiguration
STATIC_IP = '192.168.0.122'
SUBNET_MASK = '255.255.255.0'
GATEWAY = '192.168.0.1'
DNS_SERVER = '192.168.0.1'

# LED på pinne 25 (inbyggd LED på Raspberry Pi Pico W)
led = Pin("LED", Pin.OUT)

# ADC för att läsa in temperaturvärden
sensor_temp = ADC(4)
conversion_factor = 3.3 / (65535)

# Variabel för att lagra önskad temperatur
setTemp = 27.0  # Startvärde
maxTemp = 30.0  # Maxvärde
minTemp = 24.0  # Minvärde

# Funktion för att blinka LED:en
def blink_led(times, interval):
    for _ in range(times):
        led.on()
        time.sleep(interval)
        led.off()
        time.sleep(interval)

# Funktion för att konvertera RSSI till procent
def rssi_to_percentage(rssi):
    # Begränsa värdet till ett rimligt intervall
    if rssi <= -100:
        return 0
    elif rssi >= -50:
        return 100
    else:
        return 2 * (rssi + 100)

# Funktion för att läsa temperaturen från inbyggd sensor
def read_temperature():
    reading = sensor_temp.read_u16() * conversion_factor
    temperature_celsius = 27 - (reading - 0.706) / 0.001721
    return temperature_celsius

# Funktion för att ansluta till WiFi med statisk IP
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #wlan.config(dhcp_hostname=HOSTNAME)
    network.hostname(HOSTNAME) # gör ingen nytta?
    wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS_SERVER))
    wlan.connect(SSID, PASSWORD)
    retries = 0
    max_retries = 10
    while not wlan.isconnected() and retries < max_retries:
        retries += 1
        print(f'Försöker att ansluta... ({retries})')
        blink_led(1, 0.5)  # Blinkar LED:en en gång var 0.5 sekund
        time.sleep(1)
    if wlan.isconnected():
        print(f'Ansluten till WiFi som {HOSTNAME}!')
        print('IP-adress:', wlan.ifconfig()[0])
        led.on()  # Tänder LED:en med fast sken
        # Starta mDNS
        #mdns_instance = mdns.Server()
        #mdns_instance.start(HOSTNAME, "MicroPython")
        #mdns_instance.add_service('_http', '_tcp', 80, hostname=HOSTNAME, txt="PicoTemp Web Server")
        return wlan
    else:
        print('Misslyckades att ansluta till WiFi.')
        blink_led(3, 0.2)  # Blinkar LED:en snabbt 3 gånger för att indikera fel
        return None

# Skapar en webbsida
def web_page(temperature, rssi, rssi_percentage, set_temp):
    html = f"""
    <html>
    <head>
        <title>{HOSTNAME}</title>
    </head>
    <body>
        <h1>{HOSTNAME}</h1>
        <p>Temperatur: {temperature:.2f} °C</p>
        <p>WiFi RSSI: {rssi} dBm ({rssi_percentage:.0f}%)</p>
        <p>Inställd Temperatur: {set_temp:.2f} °C</p>
        <form action="/" method="post">
            <button name="action" value="upp" type="submit">Upp</button>
            <button name="action" value="ner" type="submit">Ner</button>
        </form>
    </body>
    </html>
    """
    return html

# Ansluter till WiFi vid start
wlan = connect_to_wifi()

# Skapar en socket och lyssnar på inkommande anslutningar
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

if wlan and wlan.isconnected():
    print(f'Lyssnar på http://{wlan.ifconfig()[0]}')

# Hanterar inkommande anslutningar och övervakar WiFi-anslutningen
while True:
    if not wlan.isconnected():
        print('WiFi-anslutningen tappad. Försöker återansluta...')
        led.off()  # Släcker LED:en vid förlorad anslutning
        wlan = connect_to_wifi()
        if wlan and wlan.isconnected():
            print(f'Återansluten till WiFi som {HOSTNAME}!')
            led.on()  # Tänder LED:en med fast sken

    if wlan and wlan.isconnected():
        cl, addr = s.accept()
        print('Klient ansluten från', addr)
        request = cl.recv(1024).decode()
        
        # Hanterar knapptryckningar
        if 'action=upp' in request:
            setTemp = min(setTemp + 0.5, maxTemp)  # Ökar men inte över maxTemp
        elif 'action=ner' in request:
            setTemp = max(setTemp - 0.5, minTemp)  # Minskar men inte under minTemp

        temperature = read_temperature()
        rssi = wlan.status('rssi')
        rssi_percentage = rssi_to_percentage(rssi)
        response = web_page(temperature, rssi, rssi_percentage, setTemp)
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    time.sleep(10)