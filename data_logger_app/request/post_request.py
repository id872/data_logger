# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from configs.data_config import PostRequestConfig
from request.aes_helper import AesHelper, OutputFmt

_LOGGER = logging.getLogger('DevDataLogger')


class PostRequest:
    def __init__(self, post_payload):
        self.post_payload = post_payload

    def encrypt_and_send(self, aes_key: str) -> str:
        def get_post_payload_data_encrypted():
            AesHelper.enc_out_fmt = OutputFmt.PLAIN_COMPRESSED_BASE64_CIPHER
            return AesHelper(aes_key).encrypt_json(self.post_payload['data'])

        def get_post_payload():
            json_to_send = dict(self.post_payload)
            json_to_send['data'] = get_post_payload_data_encrypted()
            return json_to_send

        try:
            request = Request(PostRequestConfig.REQUEST_URL,
                              urlencode(get_post_payload()).encode(),
                              headers={'User-Agent': PostRequestConfig.USER_AGENT})
            return urlopen(request, timeout=PostRequestConfig.REQUEST_TIMEOUT).read().decode()
        # catch expected & unexpected exceptions from urllib
        # pylint: disable=W0703
        except Exception as ex:
            _LOGGER.debug('URL/HTTP/other error:\n%s', ex)
        return ''
