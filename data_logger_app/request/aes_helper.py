# -*- coding: utf-8 -*-
import base64
import zlib
from enum import Enum
from hashlib import sha256
from json import dumps

from Crypto.Cipher import AES


class OutputFmt(Enum):
    RAW_CIPHER = 0
    BASE64_CIPHER = 1
    PLAIN_COMPRESSED_BASE64_CIPHER = 2


def output_decorator(func_decorated):
    def func_wrapper(*args, **kwargs):
        if AesHelper.enc_out_fmt == OutputFmt.RAW_CIPHER:
            return func_decorated(*args, **kwargs)
        return base64.b64encode(func_decorated(*args, **kwargs)).decode()

    return func_wrapper


class AesHelper:
    enc_out_fmt = OutputFmt.BASE64_CIPHER

    def __init__(self, key_str: str):
        self.aes_mode = AES.MODE_CFB
        self.key = self.hash_key(key_str)
        self.init_vector = None

    @classmethod
    def get_output_fmt(cls):
        return cls.enc_out_fmt

    @staticmethod
    def hash_key(aes_key: str) -> bytes:
        return sha256(aes_key.encode()).digest()

    @output_decorator
    def encrypt_str(self, plain_str: str, iv_concat=True) -> bytes or str:
        if not plain_str:
            raise ValueError('String is empty')

        cipher = AES.new(self.key, self.aes_mode)

        self.init_vector = cipher.iv

        if self.get_output_fmt() != OutputFmt.PLAIN_COMPRESSED_BASE64_CIPHER:
            data_bytes = plain_str.encode()
        else:
            data_bytes = zlib.compress(plain_str.encode())

        if iv_concat:
            return b''.join([self.init_vector, cipher.encrypt(data_bytes)])
        return cipher.encrypt(data_bytes)

    def encrypt_json(self, json_data: dict, iv_concat=True) -> bytes or str:
        if not json_data:
            raise ValueError('Dictionary is empty')

        return self.encrypt_str(dumps(json_data), iv_concat)
