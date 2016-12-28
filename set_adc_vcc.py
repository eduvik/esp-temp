'''
This will set the ADC mode of the ESP to be able to read the VCC
voltage instead of using the external pin. Useful to determine
battery status. This writes to the flash, so only needs to be run
once (or possibly once every time firmware is flashed).

Once set, battery voltage can read using machine.ADC(1).read()

From https://github.com/micropython/micropython/issues/2352#issuecomment-242315810
'''
import esp
from flashbdev import bdev
import machine

def set_adc_vcc():
    sector_size = bdev.SEC_SIZE
    flash_size = esp.flash_size()
    init_sector = int(flash_size / sector_size - 4)
    data = bytearray(esp.flash_read(init_sector * sector_size, sector_size))
    data[107] = 255
    esp.flash_erase(init_sector)
    esp.flash_write(init_sector * sector_size, data)
    machine.reset()
