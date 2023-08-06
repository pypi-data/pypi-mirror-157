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
import argparse
from . import stp
from io import StringIO, BytesIO
from . import signing

class args:
    pass

# /* CABA Header */
# typedef struct caba_v1 {
# 	char magic[4];		/* Identifier of data */
# 	u16 version;		/* Version of header. Must be 1 */
# 	u16 flags;		/* Flags of component */
# 	u32 size;		/* Size of data without header */
# 	u32 crc;		/* CRC32 of data */
# 	u32 hcrc;		/* CRC32 of header computed while hcrc32 == 0 */
# 	u8 data[0];		/* Data */
# } caba_v1_t;

# typedef struct caba_v2 {
#	char magic[4];		/* Identifier of data */
#	u16 version;		/* Version of header. Must be 2 */
#	u16 flags;		/* Flags of component */
#	u32 size;		/* Size of data without header */
#	u16 sig_type;		/* Signature type (see caba_sig_type) */
#	u16 sig_size;		/* Signature size in bytes */
#	u8 data[0];		/* Data */
# } caba_v2_t;

# typedef struct caba_v3 {
# 	char magic[4];		/* Identifier of data */
# 	u16 version;		/* Version of header. Must be 3*/
# 	u16 flags;		/* Flags of component */
# 	u32 size;		/* Size of data without header */
# 	u16 sig_type;		/* Signature type (see caba_sig_type) */
# 	u16 sig_size;		/* Signature size in bytes */
# 	u16 descr_size;		/* Size of description string (including null byte) */
# 	char description[0];	/* Null terminated description string */
# 	u8 data[0];		/* Data */
# } __attribute__((packed)) caba_v3_t;


CABA_V1_FMT = "<4sHHIII"
CABA_V2_FMT = "<4sHHIHH"
CABA_V3_FMT = "<4sHHIHHH"

def pack_v1(magic, data):
    dcrc = crc.fletcher32(data)
    caba = struct.pack(CABA_V1_FMT, magic.encode(), 1, 0, len(data),
                       dcrc, 0)
    hcrc = crc.fletcher32(caba)
    caba = struct.pack(CABA_V1_FMT, magic.encode(), 1, 0, len(data),
                       dcrc, hcrc)
    return caba + data

def pack_v2(magic, data):
    caba = struct.pack(CABA_V2_FMT, magic.encode(), 2, 0, len(data),
                       signing.SIG_CRC32, 4)
    return caba + data + signing.sign(signing.SIG_CRC32, caba + data)

def pack_v3(magic, data, descr, key, sig):
    descr += "\x00"
    caba = struct.pack(CABA_V3_FMT, magic.encode(), 3, 0, len(data),
                       sig, signing.sigsize[sig], len(descr))
    unsigned = caba + descr + data

    return unsigned + signing.sign(sig, unsigned, key, endian=">")

def get_version(data):
    _, version = struct.unpack_from("<4sH", data)
    return version

def pack(magic, data, version=1, descr=None, key=None, sig=signing.SIG_ZCRC32):
    if version == 1:
        return pack_v1(magic, data)

    if version == 2:
        return pack_v2(magic, data)

    if version == 3:
        if descr == None:
            print("Caba version 3 requires a description")
            return None
        return pack_v3(magic, data, descr, key, sig)

    print(f"Unsupported CABA version {version}")
    return None

def identify(data):
    index = 0
    while index < len(data):
        caba, version = struct.unpack_from(">4sH", data[index:])

        if version == 1:
            _, _, _, size, _, _= struct.unpack_from(CABA_V1_FMT, data[index:])
            print(f"Obsolete caba {caba}")
            index += struct.calcsize(CABA_V1_FMT) + size
            continue

        if version == 2:
            _, _, _, size, _, sig_size= struct.unpack_from(CABA_V2_FMT, data[index:])
            print("Obsolete caba {caba}")

            index += struct.calcsize(CABA_V2_FMT) + size + sig_size
            continue

        if version == 3:
            _, _, _, size, _, sig_size, descr_size = struct.unpack_from(CABA_V3_FMT, data[index:])
            hsize = struct.calcsize(CABA_V3_FMT)
            print(f"{data[index + hsize : index + hsize + descr_size - 1]}")
            index += hsize + sig_size + descr_size + size
            continue

        print("identify: Unknown caba version {version}")
        return

def split(data):
    index = 0
    cabas = []
    while index < len(data):
        caba, version = struct.unpack_from("<4sH", data[index:])
        if version == 1:
            _, _, _, size, _, _= struct.unpack_from(CABA_V1_FMT, data[index:])
            length = struct.calcsize(CABA_V1_FMT) + size
        elif version == 2:
            _, _, _, size, _, sig_size= struct.unpack_from(CABA_V2_FMT, data[index:])
            length = struct.calcsize(CABA_V2_FMT) + size + sig_size
        elif version == 3:
            _, _, _, size, _, sig_size, descr_size = struct.unpack_from(CABA_V3_FMT, data[index:])
            hsize = struct.calcsize(CABA_V3_FMT)
            length = hsize + sig_size + descr_size + size
        else:
            print("split: Unknown caba version {version}")
            return None

        cabas.append(data[index:index + length])
        index += length
    return cabas

def get_magic(data):
    return struct.unpack_from("<4s", data)[0]

def get_description(data):
    vers = get_version(data)
    if vers < 3:
        raise Exception("Caba version %d has no description field"%vers)

    _, _, _, _, _, _, descr_size = struct.unpack_from(CABA_V3_FMT, data)
    header_size = struct.calcsize(CABA_V3_FMT)
    return data[header_size : header_size + descr_size]

def get_sigtype(data):
    vers = get_version(data)
    if vers < 3:
        raise Exception("Caba version %d has no signature field"%vers)

    _, _, _, _, sigtype, _, _ = struct.unpack_from(CABA_V3_FMT, data)
    return sigtype

def get_total_size(data):
    vers = get_version(data)

    if vers < 3:
        raise Exception("Caba version %d not supported"%vers)

    _, _, _, data_size, _, sig_size, descr_size= struct.unpack_from(CABA_V3_FMT, data)
    return struct.calcsize(CABA_V3_FMT) + descr_size + data_size + sig_size

def get_data(data):
    v = get_version(data)

    if v == 1 or v == 2:
        _, _, _, data_size, _, _= struct.unpack_from(CABA_V1_FMT, data)
        size = struct.calcsize(CABA_V1_FMT)
    elif v == 3:
        _, _, _, data_size, _, _, descr_size= struct.unpack_from(CABA_V3_FMT, data)
        size = descr_size + struct.calcsize(CABA_V3_FMT)
    else:
        print("get_data: Unknown caba version {version}")
        return None

    return data[size:size + data_size]

def resign(data, sigtype, sigkey):
    vers = get_version(data)

    if vers != 3:
        raise Exception("Caba version %d can't be resigned"%vers)

    magic = get_magic(data)
    descr = get_description(data)
    data = get_data(data)

    return pack(magic, data, 3, descr, sigkey, sigtype)


def verify(data):
    vers = get_version(data)
    if vers != 3:
        raise Exception("Caba version %d can't be verified"%vers)

    _, _, _, data_size, sig_type, sig_size, descr_size= struct.unpack_from(CABA_V3_FMT, data)
    signed_data_size = struct.calcsize(CABA_V3_FMT) + descr_size + data_size
    signed_data = data[:signed_data_size]
    signature = data[signed_data_size:]
    return signing.verify(signed_data, signature, sig_type, None)

def main():
    parser = argparse.ArgumentParser(description='elf2sfff arguments parser')
    parser.add_argument('-s', '--serial', help='Flash generated file using serial device', nargs=1, required=True)
    parser.add_argument('-b', '--baudrate', help='Set serial baudrate (default is 921600)',
                        type=int, default=921600)
    parser.add_argument('-v', '--version', help='Caba version to use', type=int, default=1)
    parser.parse_args(namespace=args)

    c1 = pack("TEST", "FOOBAR\0".encode(), version=args.version)
    c2 = pack("TEST", "BARFOO\0".encode(), version=args.version)
    out = c1 + c2

    io = BytesIO(out)

    import serial
    s = serial.Serial(args.serial[0], args.baudrate, rtscts=True, timeout=1)
    s.timeout = 0.1
    s.read(256)
    s.timeout = 1

    s.write("AT+SMSTPU\r\n".encode())
    response = s.read(4)
    rsp = response.decode(encoding="ascii")
    if rsp != "OK\r\n" and rsp != "\r\nOK" and rsp != "\nOK":
        print(f"Remote answered '{rsp}' to AT command\n")
        exit(1)
    s.flush()
    s.close()
    stp.start(args.serial[0], "serial", io, args.baudrate, AT=False)

if __name__ == "__main__":
    main()
