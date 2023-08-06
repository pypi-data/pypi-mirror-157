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
import struct, array

LITTLE_ENDIAN = "<"
NATIVE_ENDIAN = "="
BIG_ENDIAN = ">"

# -------------------------------------------------// Utility /__________________________________
class encode:

    endian = BIG_ENDIAN

    @staticmethod
    def setEndianness (e):
            encode.endian = e

    @staticmethod
    def getEndianness ():
            return encode.endian

    @staticmethod
    def u32 (value, endianness = None):
        e = encode.endian if endianness is None else endianness
        return array.array("c", struct.pack(e + "I", value))

    @staticmethod
    def s32 (value, endianness = None):
        if value < 0:
            value = 0x100000000 + value
        return encode.u32(value, endianness)

    @staticmethod
    def u16 (value, endianness = None):
        e = encode.endian if endianness is None else endianness
        return array.array("c", struct.pack(e + "H", value))

    @staticmethod
    def u8 (value, endian = None):
        return array.array("c", chr(value))

    @staticmethod
    def string (value, endian = None):
        return array.array("c", value + "\x00")

class decode:

    endian = BIG_ENDIAN

    @staticmethod
    def setEndianness (e):
            decode.endian = e

    @staticmethod
    def getEndianness ():
            return decode.endian

    @staticmethod
    def u32 (value, endianness = None):
        e = decode.endian if endianness is None else endianness
        return struct.unpack(e + "I", value)[0]

    @staticmethod
    def s32 (value, endianness = None):
        v = decode.u32(value, endianness)
        if v & (1 << 31):
            return v - 0x100000000
        return v

    @staticmethod
    def u16 (value, endianness = None):
        e = decode.endian if endianness is None else endianness
        return struct.unpack(e + "H", value)[0]

    @staticmethod
    def u8 (value, endian = None):
        return ord(value)

    @staticmethod
    def string (value, endian = None):
        offset = 0
        str = ""
        c = value[offset]
        while c != '\x00':
            offset += 1
            str += c
            c = value[offset]

        return str

