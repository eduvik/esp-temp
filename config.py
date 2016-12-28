from secrets import *  # ESSID and PASSWD come from here; don't add to VCS

DELAY_TIME_SECS=5
SLEEP_TIME_MINS=30
WLAN_WAIT_SECS = 1
WLAN_RETRIES = 10
MQTT_SERVER = '192.168.1.11'
MQTT_CLIENT_ID = 'esp-01'
MQTT_TOPIC_TEMP = 'sensors/' + MQTT_CLIENT_ID + '/temp'
MQTT_TOPIC_VOLTAGE = 'sensors/' + MQTT_CLIENT_ID + '/voltage'
MQTT_TOPIC_LOW_VOLTAGE = 'sensors/' + MQTT_CLIENT_ID + '/low_voltage'
MQTT_TOPIC_STOP = 'stop'
VCC_CALIBRATION_OFFSET_MV = -187  # this will be added to the raw ADC reading
VCC_LOWER_LIMIT_MV = 3300  # device will try to deliver message, then deep sleep when VCC below this
VCC_DANGER_LIMIT_MV = 3100  # device will deep sleep immediately when VCC below this

