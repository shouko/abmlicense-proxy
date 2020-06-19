import hashlib
import hmac
import logging
import re
import time
import uuid
import requests

from base64 import urlsafe_b64encode

import config
from abm_license import get_key_from_id

class AbmClient():

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.UA_CHROME})
        self.deviceid = str(uuid.uuid4())
        self.appkeysecret = self._generate_applicationkeysecret(self.deviceid)
        json_data = {"deviceId": self.deviceid,
                     "applicationKeySecret": self.appkeysecret}
        res = self.session.post(config._USER_API, json=json_data)
        jsonres = res.json()
        self.usertoken = jsonres['token']

    def _hmac_multi_pass(self, text, n):
        tmp = text

        for i in range(n):
            h = hmac.new(config.SECRETKEY, digestmod=hashlib.sha256)
            h.update(tmp)
            tmp = h.digest()

        return tmp

    def _generate_applicationkeysecret(self, deviceid):
        deviceid = deviceid.encode("utf-8")
        ts_1hour = (int(time.time()) + 60 * 60) // 3600 * 3600
        time_struct = time.gmtime(ts_1hour)
        ts_1hour_str = str(ts_1hour).encode("utf-8")

        tmp = self._hmac_multi_pass(config.SECRETKEY, 1)
        tmp = self._hmac_multi_pass(tmp, time_struct.tm_mon)
        tmp = self._hmac_multi_pass(urlsafe_b64encode(tmp).rstrip(b"=") + deviceid, 1)
        tmp = self._hmac_multi_pass(tmp, time_struct.tm_mday % 5)
        tmp = self._hmac_multi_pass(urlsafe_b64encode(tmp).rstrip(b"=") + ts_1hour_str, 1)
        tmp = self._hmac_multi_pass(tmp, time_struct.tm_hour % 5)

        return urlsafe_b64encode(tmp).rstrip(b"=").decode("utf-8")

    def _get_key_from_id(self, key_id):
        return get_key_from_id(self.deviceid, self.usertoken, self.session, key_id)