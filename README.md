# esp-temp

This is a micropython project for an ESP8266 which reads the temperature, then dumps it to an MQTT broker. It is designed to
run off batteries - in my case, direct to some 18650 Li-ion cells. It uses a DS18B20 temperature sensor, connected VCC->Pin 13, GND->Pin 14, Data->Pin 12 (this is easy to change).

I'll upload a schematic and photos soon.

Features include:
* Reads temperature, dumps to MQTT, then deep sleeps for a defined amount of time.
* Tries to connect to network for a little while, but shuts back down to deep sleep if can't connect.
* When battery voltage drops below a certain amount, attempts to send a message, then deep sleeps indefinitely to prevent draining battery too low
* Checks for a stop signal on MQTT. If received, goes into webrepl mode to allow for remote maintenance/updates

Usage:
* Flash micropython onto the device
* create secrets.py, and define ESSID and PASSWD in that file for your network configuration
* edit config.py to suit (particularly MQTT_SERVER)
* copy all files across using your method of choice (webrepl is one option)
* in a REPL, run `import set_adc_vcc; set_adc_vcc.set_adc_vcc()` - this configures the internal flash to use the ADC to measure
the VCC voltage rather than from the external pin.
* measure battery voltage using a voltmeter
* start the device - be ready to press Ctrl-C if connected by serial, or else push a retained MQTT message to your broker e.g. `mosquitto_pub -h localhost -r -t stop -m "esp-01"` then connect via webrepl
* determine correct VCC_CALIBRATION_OFFSET_MV, change this in the config.py file, and upload config.py again.