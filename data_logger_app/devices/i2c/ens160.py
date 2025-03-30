from struct import pack, unpack
from time import sleep

from devices.i2c.i2c_device import I2CDevice

_ENS160_I2CADDR_DEFAULT = 0x53  # ENS160 dev I2C address

_ENS160_REG_OP_MODE = 0x10
_ENS160_REG_STATUS = 0x20

_ENS160_SET_HUM_CAL_REG = 0x15
_ENS160_SET_TEMP_CAL_REG = 0x13

_ENS_OP_MODE_SLEEP = 0x00
_ENS_OP_MODE_IDLE = 0x01
_ENS_OP_MODE_STANDARD = 0x02
_ENS_OP_MODE_RESET = 0xF0

NORMAL_OP = 0x00
WARM_UP = 0x01
START_UP = 0x02
INVALID_OUT = 0x03

OP_MODE_MAP = {
    _ENS_OP_MODE_SLEEP: "SLEEP",
    _ENS_OP_MODE_IDLE: "IDLE",
    _ENS_OP_MODE_STANDARD: "STANDARD",
    _ENS_OP_MODE_RESET: "RESET",
}

STATUS_MAP = {NORMAL_OP: "NORMAL OPERATION", WARM_UP: "WARMING OPERATION", START_UP: "STARTUP", INVALID_OUT: "INVALID"}


class ENS160:
    def __init__(self, aht_addr=_ENS160_I2CADDR_DEFAULT):
        self.i2c_dev = I2CDevice(aht_addr, buf_size=1)
        self._dev_init()
        self.temperature = 25
        self.humidity = 50

    def _dev_init(self):
        self.set_op_mode(_ENS_OP_MODE_RESET)
        self.set_op_mode(_ENS_OP_MODE_IDLE)
        self.set_op_mode(_ENS_OP_MODE_STANDARD)

    def print_all_data(self):
        print(f"AQI: {self.get_aqi()}")
        print(f"ECO2: {self.get_eco2()}")
        print(f"VOC: {self.get_voc()}")
        print(f"OP mode: {self.get_op_mode()}")
        print(f"Status: {self.get_status()}\n")

    @staticmethod
    def _unpack_raw(fmt: str, raw: list):
        return unpack(fmt, bytearray(raw))[0] if raw else None

    def set_op_mode(self, mode: int):
        self.i2c_dev.i2c_write_register(_ENS160_REG_OP_MODE, bytearray(pack("<B", mode)))
        if mode == _ENS_OP_MODE_RESET:
            sleep(0.01)

    def calibrate_temp(self, temperature: float):
        if self.temperature != temperature:
            temp = int((temperature + 273.15) * 64.0 + 0.5)
            self.i2c_dev.i2c_write_register(_ENS160_SET_TEMP_CAL_REG, bytearray(pack("<H", temp)))
            self.temperature = temperature

    def calibrate_humidity(self, humidity: int):
        if self.humidity != humidity:
            hum = int(humidity * 512 + 0.5)
            self.i2c_dev.i2c_write_register(_ENS160_SET_HUM_CAL_REG, bytearray(pack("<H", hum)))
            self.humidity = humidity

    def get_aqi(self):
        return self._unpack_raw("<B", self.i2c_dev.i2c_read_register(0x21, 1))

    def get_voc(self):
        return self._unpack_raw("<H", self.i2c_dev.i2c_read_register(0x22, 2))

    def get_eco2(self):
        return self._unpack_raw("<H", self.i2c_dev.i2c_read_register(0x24, 2))

    def get_op_mode(self):
        op_mode = self._unpack_raw("<B", self.i2c_dev.i2c_read_register(_ENS160_REG_OP_MODE, 1))
        return OP_MODE_MAP[op_mode]

    def get_status(self):
        status = self._unpack_raw("<B", self.i2c_dev.i2c_read_register(_ENS160_REG_STATUS, 1))
        return STATUS_MAP[(status >> 2) & 0x03] if status else "No status"

    def is_normal_op_status(self):
        return self.get_status() == STATUS_MAP[NORMAL_OP] and self.get_aqi() > 0
