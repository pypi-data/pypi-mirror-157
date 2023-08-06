"""
TERMS AND CONDITIONS OF USE OF THE SOURCE CODE

The Source Code (the “SOURCE CODE”) is the sole property of SEQUANS Communications.

USER expressly undertakes to use this SOURCE CODE for the sole and only purposes of
TESTING and DEBUGGING. USER is perfectly aware that any other use is strictly prohibited
by SEQUANS Communications and notably the distribution/sale of such SOURCE CODE is
strictly prohibited by SEQUANS Communications. CONSIDERING THAT THE SOURCE CODE IS
PROVIDED BY COURTESY OF SEQUANS COMMUNICATIONS AND AT NO CHARGE, USER ACKNOWLEDGES
AND ACCEPTS THAT SUCH SOURCE CODE IS PROVIDED “AS IS” WITH NO ASSOCIATED DOCUMENTATION,
NO SUPPORT OR MAINTENANCE OF ANY KIND, NO WARRANTIES, EXPRESS OR IMPLIED, WHATSOEVER.
USER ACKNOWLEDGES THAT IN NO EVENT SHALL SEQUANS COMMUNICATIONS BE LIABLE FOR ANY CLAIM,
DAMAGES OR LOSS, DIRECT, INCIDENTAL, INDIRECT, SPECIAL OR CONSEQUENTIAL - ARISING FROM,
OUT OF OR IN CONNECTION WITH ANY USE OF THE SOURCE CODE. No Intellectual Property or
licensing rights shall be assigned to USER, under any form or for any purpose whatsoever,
with respect to the SOURCE CODE. Any modification, whatsoever, of the SOURCE CODE is
strictly prohibited WITHOUT PRIOR WRITTEN CONSENT OF SEQUANS Communications.

THE USE OF THE SOURCE CODE IS SUBJECT TO THE PRIOR ACCEPTANCE OF THESE TERMS AND CONDITIONS.
"""
from . import crc
import struct
import zlib

CRC32_FMT = "<I" # common format for CRC32 (fletcher) and ZCRC32 (zlib)
SIG_NONE = 0
SIG_CRC32 = 1
SIG_ECDSA_256 = 2
SIG_RSA_SHA256 = 3
SIG_ZCRC32 = 4

pubkey_type = {"ECDSA_256": 0, "RSA_2048": 1}
pubkey_name = {0: "ECDSA_256", 1: "RSA_2048"}
signature_type = {"NONE": 0, "CRC32": 1, "ECDSA_256": 2, "RSA_SHA256": 3, "ZCRC32": 4}
signature_name = {0: "NONE", 1:"CRC32", 2:"ECDSA_256", 3:"RSA_SHA256", 4: "ZCRC32"}
sigsize = {SIG_NONE: 0, SIG_CRC32: 4, SIG_RSA_SHA256: 256, SIG_ZCRC32: 4}

def sign_none(data, key, endian):
    return ""

def sign_zcrc32(data, key, endian):
    c = zlib.crc32(data) & 0xFFFFFFFF
    return struct.pack(CRC32_FMT, c)

def sign_crc32(data, key, endian):
    c = crc.fletcher32(data, endian)
    return struct.pack(CRC32_FMT, c)
"""
def sign_rsa_sha256(data, key, endian=None):
    # Here endianess is not needed by RSA lib, 
    # Parameter must be present to keep function prototype compatible with CRC 32
    data = ''.join(data)        # Convert array to bit-string
    rsa = __import__('rsa')
    if not key:
        raise Exception("Missing key to sign with RSA")
    key_data = open(key, 'rb').read()

    k = rsa.PrivateKey.load_pkcs1(key_data, format="DER")
    return rsa.sign(data, k, 'SHA-256')
"""
#sigfuns = {SIG_NONE: sign_none, SIG_CRC32: sign_crc32, SIG_RSA_SHA256: sign_rsa_sha256, SIG_ZCRC32: sign_zcrc32}
sigfuns = {SIG_NONE: sign_none, SIG_CRC32: sign_crc32, SIG_ZCRC32: sign_zcrc32}
def sign(sigtype, data, key=None, endian = None):
    if sigtype == SIG_ECDSA_256:
        raise Exception("Unsupported signature ECDSA_256")
    return sigfuns[sigtype](data, key, endian)

def verify_crc32(data, signature):
    crc = sign_crc32(data, None)
    return crc == signature

def verify_zcrc32(data, signature):
    crc = sign_zcrc32(data, None)
    return crc == signature
"""
def verify_rsa_sha256(data, signature, key):
    rsa = __import('rsa')
    if not key:
        raise Exception("Missing key to verify RSA signature")
    key_data = open(key, 'rb').read()

    k = rsa.PublicKey.load_pkcs1(key_data, format="DER")
    return rsa.verify(data, signature, k)
"""
def verify(data, signature, sigtype, key=None):
    if sigtype == SIG_ECDSA_256:
        raise Exception("Unsupported signature ECDSA_256")
    if sigtype == SIG_CRC32:
        return verify_crc32(data, signature)
    if sigtype == SIG_ZCRC32:
        return verify_zcrc32(data, signature)
    #if sigtype == SIG_RSA_SHA256:
    #    return verify_rsa_sha256(data, signature, key)
    return False
