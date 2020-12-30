# -*- coding: utf-8 -*-
from minimalmodbus import MODE_RTU


class ModbusConfig:
    DEV_ID_NAME = {
        1: 'Santerno1',
        2: 'Santerno2'
    }

    PORT_DEV_NAME = '/dev/ttyUSB'
    PORT_DEV_NUM = 0
    PORT_DEV = '{}{}'.format(PORT_DEV_NAME, PORT_DEV_NUM)

    RS_485_BAUDRATE = 9600
    RS_485_STOP_BITS = 2
    RS_485_MODBUS_MODE = MODE_RTU
    RS_485_MODBUS_TIMEOUT = 0.08
    RS_485_CLOSE_PORT_AFTER_CALL = True
