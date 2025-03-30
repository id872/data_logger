from smbus2 import SMBus, i2c_msg


class I2CDevice:
    _I2C_BUS_NO = 1

    def __init__(self, dev_addr: int, buf_size: int):
        self._i2c_addr = dev_addr
        self._buf = bytearray(buf_size)

    def i2c_write_data(self, data: bytearray):
        with SMBus(self._I2C_BUS_NO) as bus:
            msg = i2c_msg.write(self._i2c_addr, data)
            bus.i2c_rdwr(msg)

    def i2c_write_buf(self, buf_size: int):
        with SMBus(self._I2C_BUS_NO) as bus:
            msg = i2c_msg.write(self._i2c_addr, self._buf[0:buf_size])
            bus.i2c_rdwr(msg)

    def i2c_read_to_buf(self, buf_size: int):
        with SMBus(self._I2C_BUS_NO) as bus:
            self._buf = bus.read_i2c_block_data(self._i2c_addr, 0, buf_size)

    def i2c_read_register(self, reg: int, size: int):
        with SMBus(self._I2C_BUS_NO) as bus:
            return bus.read_i2c_block_data(self._i2c_addr, reg, size)

    def i2c_write_register(self, reg: int, data: bytearray):
        with SMBus(self._I2C_BUS_NO) as bus:
            return bus.write_i2c_block_data(self._i2c_addr, reg, data)

    @property
    def i2c_buffer(self):
        return self._buf
