# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-w-micropython-ebook/

import network
import time
# udp server
import socket
import select

# Wi-Fi credentials
ssid = 'Tele2_24BB96'
password = 'uei3rt7j'

temp_c = -273.2

# Static IP configuration
static_ip = '192.168.0.100'  # Replace with your desired static IP
subnet_mask = '255.255.255.0'
gateway_ip = '192.168.0.1'
dns_server = '8.8.8.8'



# Init Wi-Fi Interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to your network
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)
    
# Set static IP address
wlan.ifconfig((static_ip, subnet_mask, gateway_ip, dns_server))

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection') # Lista över sockets som vi ska övervaka

else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])
    
# Definiera serverns IP-adress och port
SERVER_IP = ""
SERVER_PORT = 12345
BUFFER_SIZE = 1024  # Storleken på bufferten för att ta emot meddelanden

# Skapa en UDP-socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind socketen till IP-adressen och porten
sock.bind((SERVER_IP, SERVER_PORT))

print(f"UDP-server kör på {SERVER_IP}:{SERVER_PORT}")

# Lista över sockets som vi ska övervaka
inputs = [sock]
outputs = []
loopar = 0

while True:
    
    if loopar > 1000:
        print("Loopar vidare och väntar på inkommande........")
        loopar = 0
    print("HEJ")   
    # Använd select för att vänta på att sockets ska bli redo för I/O
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    for s in readable:
        if s is sock:
            data, client_address = s.recvfrom(BUFFER_SIZE)
            print(f"Mottog meddelande från {client_address}: {data.decode('utf-8')}")
            
            # Förbered svaret
            response = "Meddelande mottaget!"
            s.sendto(response.encode('utf-8'), client_address)


    # Ta emot data och klientens adress
    data, client_address = sock.recvfrom(BUFFER_SIZE)
    
    print(f"Mottog meddelande från {client_address}: {data.decode('utf-8')}")
    
    # Skicka ett svar tillbaka till klienten
    response = f"Temp: {temp_c}"
    sock.sendto(response.encode('utf-8'), client_address)
    loopar +=1
    print(f"Loopar = {loopar}")
