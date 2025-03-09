from urllib.parse import urlencode
from urllib.request import Request, urlopen

from configs.data_config import PostRequestConfig
from loggers.app_logger import app_logging
from request.aes_helper import AesHelper, OutputFmt


class PostRequest:
    def __init__(self, post_payload):
        self.post_payload = post_payload

    def encrypt_and_send(self, aes_key: str) -> str:
        def get_post_payload_data_encrypted():
            AesHelper.enc_out_fmt = OutputFmt.PLAIN_COMPRESSED_BASE64_CIPHER
            return AesHelper(aes_key).encrypt_json(self.post_payload["data"])

        def get_post_payload():
            json_to_send = dict(self.post_payload)
            json_to_send["data"] = get_post_payload_data_encrypted()
            return json_to_send

        try:
            request = Request(
                PostRequestConfig.REQUEST_URL,
                urlencode(get_post_payload()).encode(),
                headers={"User-Agent": PostRequestConfig.USER_AGENT},
            )
            return str(urlopen(request, timeout=PostRequestConfig.REQUEST_TIMEOUT).read().decode()).strip()
        # catch expected & unexpected exceptions from urllib
        # pylint: disable=W0703
        except Exception as ex:
            app_logging.debug("URL/HTTP/other error:\n%s", ex)
        return ""
