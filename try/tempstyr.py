# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-w-micropython-ebook/

import machine, onewire, ds18x20, time

# Pin configuration for DS18B20 temperature sensor
ds_pin = machine.Pin(22)
led = machine.Pin(0, machine.Pin.OUT)
led.value(1)

# Create DS18X20 object using OneWire protocol with specified pin
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Scan for DS18B20 sensors and print their ROM addresses
roms = ds_sensor.scan()
print('Found DS devices: ', roms)
led.value(0)
while True:
    # Initiate temperature conversion for all sensors
    ds_sensor.convert_temp()
    time.sleep_ms(750)  # Wait for the conversion to complete (750 ms is recommended)
    
    for rom in roms:
        print(rom)
            
        # Read temperature in Celsius from the sensor
        temp_c = ds_sensor.read_temp(rom)
        if temp_c > 25:
            led.value(0)
        elif temp_c < 24:
            led.value(1)
        

        # Print the temperature readings
        print('temperature (ºC):', "{:.2f}".format(temp_c))

    time.sleep(1)  # Wait for 5 seconds before taking readings again

