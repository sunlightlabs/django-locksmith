import os, time, datetime, math, hashlib
import base64, uuid, struct, binascii

from django.conf import settings

THIRTY_DAYS = datetime.timedelta(days=30).total_seconds()

def get_client_key(master_key, hostname, user_agent, ts=None):
    print "getting", hostname
    ukey = uuid.UUID(master_key)
    if not ts:
        ts = int(time.time())

    to_sign = "%s%s%s" % (ukey.bytes, struct.pack("i", ts), struct.pack("i", binascii.crc32("%s/%s" % (hostname, user_agent))))
    signed = _encrypt(settings.SECRET_KEY, to_sign)
    return signed[10:].replace("+", "-").replace("/", "_")

def check_client_key(client_key, hostname, user_agent, ts=None):
    print "checking", hostname
    if not ts:
        ts = int(time.time())

    signed = "U2FsdGVkX1%s" % client_key.replace("-", "+").replace("_", "/")

    decrypted = _decrypt(settings.SECRET_KEY, signed)

    key = uuid.UUID(bytes=decrypted[:-8]).hex
    key_ts = struct.unpack("i", decrypted[-8:-4])[0]
    hostname_cs = struct.unpack("i", decrypted[-4:])[0]

    if hostname_cs != binascii.crc32("%s/%s" % (hostname, user_agent)):
        raise ValueError("Hostname or user agent for this key doesn't match.")

    if ts - key_ts > THIRTY_DAYS:
        raise ValueError("Key has expired.")

    return key

from locksmith.common import cache

get_cached_client_key = cache(seconds=900)(get_client_key)
check_cached_client_key = cache(seconds=900)(check_client_key)

def _simpleaes_encrypt(password, string):
    saes = SimpleAES(password)
    return saes.encrypt(string)

def _simpleaes_decrypt(password, string):
    saes = SimpleAES(password)
    return saes.decrypt(string)

def _slowaes_key(password, size=256, salt=None):
    rounds = math.ceil(size/128.0) + 1
    md5_hash = []
    if not salt:
        salt = os.urandom(8)
    
    ps = password + salt
    result = hashlib.md5(ps).digest()
    md5_hash = [result]
    
    for i in range(1, int(rounds) + 1):
        md5_hash.append(hashlib.md5(md5_hash[i - 1] + ps).digest())
        result = result + md5_hash[i]
    
    size8 = size / 8
    return {
        "key": result[0:size8],
        "iv": result[size8:size8+16],
        "salt": salt
    }

def _slowaes_encrypt(password, string):
    key = _slowaes_key(password, 256, salt=None)

    okey = map(ord, key['key'])
    data = aes.append_PKCS7_padding(string)

    moo = aes.AESModeOfOperation()
    (mode, length, ciph) = moo.encrypt(data, aes.AESModeOfOperation.modeOfOperation["CBC"], okey, len(okey), map(ord, key['iv']))
    raw_enc = ''.join(map(chr, ciph))

    return base64.b64encode("Salted__" + key['salt'] + raw_enc)

def _slowaes_decrypt(password, string):
    _string = base64.b64decode(string)

    key = _slowaes_key(password, 256, _string[8:16])

    okey = map(ord, key['key'])
    iv = map(ord, key['iv'])
    data = map(ord, _string[16:])
    moo = aes.AESModeOfOperation()
    decr = moo.decrypt(data, None, aes.AESModeOfOperation.modeOfOperation["CBC"], okey, len(okey), iv)

    return aes.strip_PKCS7_padding(decr)

if True:
    # use slowaes, which is fast enough, and works on pypy
    import aes
    _encrypt = _slowaes_encrypt
    _decrypt = _slowaes_decrypt
else:
    # use SimpleAES, which is fast
    from SimpleAES import SimpleAES
    _encrypt = _simpleaes_encrypt
    _decrypt = _simpleaes_decrypt
