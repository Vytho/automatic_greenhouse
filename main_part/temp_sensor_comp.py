import dht
import machine

# This is the simple code to test how to connect and work with dht11 sensor


d = dht.DHT11(machine.Pin(0))


d.measure()
temp = d.temperature()
print("temperature is: ", temp)