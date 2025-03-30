from time import sleep

from devices.i2c.i2c_device import I2CDevice

_TIME_FIVE_U_SEC = 0.005
_TIME_TWENTY_U_SEC = 0.02

_AHT_I2CADDR_DEFAULT = 0x38  # Default I2C address
_AHT_STATUS_BUSY = 0x80  # Status bit for busy
_AHT_STATUS_CALIBRATED = 0x08  # Status bit for calibrated

_AHT_RESET_CMD = bytearray([0xBA])
_AHT_INIT_CMD = bytearray([0xBE, 0x08, 0x00])
_AHT_TRIGGER_MEA_CMD = bytearray([0xAC, 0x33, 0x00])


class AHT21:
    def __init__(self, aht_addr=_AHT_I2CADDR_DEFAULT):
        self.i2c_dev = I2CDevice(aht_addr, buf_size=6)
        self._aht_reset()
        if not self._aht_init():
            raise Exception("init error")

    def _aht_reset(self):
        self.i2c_dev.i2c_write_data(_AHT_RESET_CMD)
        sleep(_TIME_TWENTY_U_SEC)

    def _aht_init(self):
        self.i2c_dev.i2c_write_data(_AHT_INIT_CMD)
        self._wait_for_idle()
        if not self._get_dev_status() & _AHT_STATUS_CALIBRATED:
            return False
        return True

    def _wait_for_idle(self):
        while self._get_dev_status() & _AHT_STATUS_BUSY:
            sleep(_TIME_FIVE_U_SEC)

    def _trigger_measurement(self):
        self.i2c_dev.i2c_write_data(_AHT_TRIGGER_MEA_CMD)

    def _perform_measurement(self):
        self._trigger_measurement()
        self._wait_for_idle()
        self.i2c_dev.i2c_read_to_buf(6)

    def _get_dev_status(self):
        self.i2c_dev.i2c_read_to_buf(1)
        return self.i2c_dev.i2c_buffer[0]

    def get_humidity(self):
        self._perform_measurement()
        buf = self.i2c_dev.i2c_buffer
        temp = (buf[1] << 12) | (buf[2] << 4) | (buf[3] >> 4)
        return (temp * 100) / 0x100000

    def get_temperature(self):
        self._perform_measurement()
        buf = self.i2c_dev.i2c_buffer
        temp = ((buf[3] & 0xF) << 16) | (buf[4] << 8) | buf[5]
        return ((temp * 200.0) / 0x100000) - 50

    def print_all_data(self):
        print(f"Temperature: {self.get_temperature():.2f}")
        print(f"Humidity: {self.get_humidity():.2f}")
