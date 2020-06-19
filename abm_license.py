import struct
import hmac
import hashlib
from Crypto.Cipher import AES
from binascii import unhexlify

import config

def get_key_from_id(deviceid, usertoken, session, key_id):
    params = config._MEDIATOKEN_API_PARAMS
    auth_header = {"Authorization": "Bearer " + usertoken}
    res = session.get(config._MEDIATOKEN_API, params=params, headers=auth_header)
    jsonres = res.json()
    mediatoken = jsonres['token']

    res = session.post(config._LICENSE_API, params={"t": mediatoken}, json={"kv": "a", "lt": key_id})
    jsonres = res.json()
    cid = jsonres['cid']
    k = jsonres['k']

    res = sum([config.STRTABLE.find(k[i]) * (58 ** (len(k) - 1 - i))
              for i in range(len(k))])
    cipherkey = struct.pack('>QQ', res >> 64, res & 0xffffffffffffffff)

    h = hmac.new(unhexlify(config.HKEY),
                 (cid + deviceid).encode("utf-8"),
                 digestmod=hashlib.sha256)
    aeskey = h.digest()

    aes = AES.new(aeskey, AES.MODE_ECB)
    plainkey = aes.decrypt(cipherkey)

    return plainkey