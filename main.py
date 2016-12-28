import time
import socket
import machine
import onewire, ds18x20
import umqtt.simple

from config import *

sleep_when_finished = True  # Global var; if True, go to deep sleep when done


def wait_for_wlan():
    """Waits for WLAN to connect; will retry WLAN_RETRIES times, waiting
    WLAN_WAIT_SECS between each try"""
    for i in range(WLAN_RETRIES):
        if wlan.isconnected() and wlan.ifconfig()[0] != '0.0.0.0':
            break
        time.sleep(WLAN_WAIT_SECS)


def deep_sleep():
    """Puts the device to deep sleep after settings a wake-up alarm.
    Before doing this it waits for a user break"""
    # wait for user break
    print('about to deep sleep for %s minutes' % SLEEP_TIME_MINS)
    print('delaying %s seconds - press Ctrl-C to prevent deep sleep' % DELAY_TIME_SECS)
    time.sleep(DELAY_TIME_SECS)
    print('deep sleeping')
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, SLEEP_TIME_MINS*60*1000)
    machine.deepsleep()


def mqtt_callback(topic, msg):
    """Callback used by umqtt when checking for stop signal"""
    global sleep_when_finished
    print('Callback hit. Topic: %s; Message: %s' % (topic, msg))
    if topic.decode('utf-8') == MQTT_TOPIC_STOP and msg.decode('utf-8') == MQTT_CLIENT_ID:
        print('we should stop')
        sleep_when_finished = False

### Acquire data ###

# read battery voltage
vcc_voltage = machine.ADC(1).read()
print('Raw VCC voltage is %d' % vcc_voltage)
vcc_voltage = vcc_voltage + VCC_CALIBRATION_OFFSET_MV
print('Calibrated VCC voltage is %d' % vcc_voltage)
if vcc_voltage <= VCC_DANGER_LIMIT_MV:
    print('VCC below lower danger limit; deep sleeping indefinitely')
    machine.deepsleep()

# setup pins
ds_vcc = machine.Pin(13, machine.Pin.OUT)
ds_vcc.high()
ds_gnd = machine.Pin(14, machine.Pin.OUT)
ds_gnd.low()
ds_data = machine.Pin(12)
ds = ds18x20.DS18X20(onewire.OneWire(ds_data))

# read temp first so that wifi doesn't heat things up
roms = ds.scan()
ds.convert_temp()
time.sleep_ms(750)
temp = ds.read_temp(roms[0])
print('temperature is %d C' % temp)


### Set up network ###
import network
use_default = True  # try ESP's last working wifi connection

wlan = network.WLAN(network.STA_IF)

#try ESP's autoconnect with last credentials
print("trying wlan connection from ESP's last config")
if use_default:
    wait_for_wlan()

# If can't use default, use specified LAN
if not wlan.isconnected():
    print("trying wlan connection using credentials from config.py")
    wlan.active(True)
    wlan.connect(ESSID, PASSWD)
    wait_for_wlan()

print('network config:', wlan.ifconfig())



### Send data, check for messages, go to sleep ###
try:
    # send data
    print('sending data')
    mqtt_client = umqtt.simple.MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER)
    mqtt_client.set_callback(mqtt_callback)
    mqtt_client.connect(clean_session=False)
    mqtt_client.publish(MQTT_TOPIC_TEMP, str(temp))
    mqtt_client.publish(MQTT_TOPIC_VOLTAGE, str(vcc_voltage))
    if vcc_voltage <= VCC_LOWER_LIMIT_MV:  # battery voltage is low; send msg then deepsleep forever
        mqtt_client.publish(MQTT_TOPIC_LOW_VOLTAGE, MQTT_CLIENT_ID)
        print('VCC below lower limit; deep sleeping indefinitely')
        machine.deepsleep()

    print('checking for STOP signal')
    mqtt_client.subscribe('stop')
    time.sleep(1)  # allow mqtt broker a second to deliver retained msgs
    mqtt_client.check_msg()
except OSError:
    print('Caught OSError: deep sleeping')
    deep_sleep()

if sleep_when_finished:
    print('finished; deep sleeping')
    deep_sleep()
else:  # otherwise start webrepl
    print('stop signal detected: starting webrepl')
    import webrepl
    webrepl.start()
