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
import sys, os
import argparse
import socket
import struct
import random
import time
import string
import zlib
import signal
from functools import partial

# CRC-16(CCIT)
def crc16(s, crcerr=False):
    crc = 0x0000
    table = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
        0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
        0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
        0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
        0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
        0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
        0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
        0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
        0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
        0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
        0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
        0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
        0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
        0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
        0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
        0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
        0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
        0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]
    for ch in s:
        crc = ((crc<<8)&0xff00) ^ table[((crc>>8)&0xff)^ch]
    if crcerr is True:
        crc += 1
        crc &= 0xFFFF
    return crc

def usleep(x):
    time.sleep(x/1000000.0)

def hexdump(src, length=32):
    if len(src) == 0:
        return
    src = src[:length]
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in range(0, len(src), length):
        chars = src[c:c+length]
    hex = ' '.join(["%02x" % ord(x) for x in chars])
    printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
    lines.append("%04x %-*s %s\n" % (c, length*3, hex, printable))
    print(''.join(lines))


def usage(app):
    print(f"Usage: {app} [options] -fifo <path>")
    print(f"Usage: {app} [options] -unix <path>")
    print(f"Usage: {app} [options] -serial <path> <elf>")
    print(f"Usage: {app} [options] -usb <VID:PID> <elf>")
    print(f"Options:")
    print(f"\t-b baudrate")
    print(f"\t-retry")
    print(f"\t-debug")
    sys.exit(1)


class MException(BaseException):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s


class FifoDev(object):
    def __init__(self, path, to, err):
        self.to = to
        self.path = path
        self.fifoIn = None
        self.fifoOut = None
        self.err = err

        self.rnd = random.Random()
        self.rnd.seed()

        self.mean = 100/2
        d = pow(self.mean - err, 2) + pow(self.mean, 2) + pow(self.mean + err, 2)
        self.sd = pow(d/3,0.5)


    def read(self, n):
        while not self.fifoOut:
            self.fifoOut = os.open(self.path + ".out", os.O_RDONLY|os.O_NONBLOCK)

        s = []
        start = time.time()
        while len(s) != n:
            try:
                s += os.read(self.fifoOut, n-len(s))
            except OSError:
                pass
            if self.to and time.time() > start + self.to:
                break
        end = time.time()
        return s


    def write(self, s):
        while not self.fifoIn:
            self.fifoIn = os.open(self.path + ".in", os.O_WRONLY|os.O_NONBLOCK)

        r = self.rnd.normalvariate(self.mean, self.sd)
        if abs(r-self.mean) < self.err:
            if self.rnd.random() > 0.5:
                print("Corrupting the OUT data")
                s = ''.join(self.rnd.sample(s, len(s)))
            else:
                print("Loosing a byte from the OUT data")
                s = s[1:]

        os.write(self.fifoIn, s)


    def devastate(self):
        while not self.fifoOut:
            self.fifoOut = os.open(self.path + ".out", os.O_RDONLY|os.O_NONBLOCK)
        while True:
            try:
                c = os.read(self.fifoOut, 1)
                if len(c) == 0: break
            except OSError:
                break

class UnixDev(object):
    def __init__(self, path, to, err):
        self.to = to
        self.remote = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.remote.connect(path)
        self.err = err

        self.rnd = random.Random()
        self.rnd.seed()

        self.mean = 100/2
        d = pow(self.mean - err, 2) + pow(self.mean, 2) + pow(self.mean + err, 2)
        self.sd = pow(d/3,0.5)


    def read(self, n):
        s = []
        start = time.time()
        while len(s) != n:
            try:
                s += self.remote.recv(n-len(s), socket.MSG_DONTWAIT)
            except socket.error:
                pass
            if self.to and time.time() > start + self.to:
                break
        end = time.time()
        return s


    def write(self, s):
        r = self.rnd.normalvariate(self.mean, self.sd)
        if abs(r-self.mean) < self.err:
            if self.rnd.random() > 0.5:
                print("Corrupting the OUT data")
                s = ''.join(self.rnd.sample(s, len(s)))
            else:
                print("Loosing a byte from the OUT data")
                s = s[1:]

        try:
            self.remote.sendall(s, socket.MSG_DONTWAIT)
        except:
            pass


    def devastate(self):
        while True:
            try:
                self.remote.recv(1, socket.MSG_DONTWAIT)
            except:
                break

class SerialDev(object):
    def __init__(self, path, to, baud):
        import serial
        self.serial = serial.serial_for_url(path, do_not_open = False)
        self.serial.baudrate = baud
        self.serial.timeout = to
        self.serial.rtscts = True

    def read(self, n):
        return self.serial.read(n)

    def write(self, s):
        self.serial.write(s)

    def devastate(self):
        # self.serial.write(chr(0xff) * 2048)
        # self.serial.flush()
        self.serial.flushInput()

    def close(self):
        self.serial.close()

    def set_timeout(self, timeout):
        self.serial.timeout = timeout

class UsbDev(object):
    def __init__(self, vid, pid, to):
        self.ep = 1
        self.interface = 0
        self.configuration = 1
        self.to = to*1000
        self.maxin = 16*1024*1024
        self.inb = []

        print(f"Waiting for STP client to settle at 0x{vid:04x}:0x{pid:04x}")

        import usb
        while True:
            dev = None
            busses = usb.busses()
            for bus in busses:
                devices = bus.devices
                for d in devices:
                    if d.idVendor == vid and d.idProduct == pid:
                        # print "Device:", d.filename
                        # print "  idVendor: %d (0x%04x)" % (d.idVendor, d.idVendor)
                        # print "  idProduct: %d (0x%04x)" % (d.idProduct, d.idProduct)
                        # print "  Manufacturer:", d.iManufacturer
                        # print "  Serial:", d.iSerialNumber
                        # print "  Product:", d.iProduct
                        # print "  Configurations:", map(lambda x: x.iConfiguration, d.configurations)
                        # for c in d.configurations:
                        #     print "  Interfaces:", map(lambda x: x[0].iInterface, c.interfaces)
                        #     for i in c.interfaces:
                        #         print "  Endpoints:", map(lambda x: x.address, i[0].endpoints)
                        dev = d.open()
                        break
            if dev:
                break
            time.sleep(1)

        assert dev is not None
        print("Connecting to STP client")
        try:
            dev.detachKernelDriver(self.interface)
        except:
            pass
        dev.setConfiguration(self.configuration)
        dev.claimInterface(self.interface)
        print("Successfully connected to STP client")
        self.dev = dev

    def __read(self, n):
        if n > len(self.inb): n = len(self.inb)
        r = self.inb[:n]
        self.inb = self.inb[n:]
        return r

    def read(self, n):
        if len(self.inb) >= n:
            return self.__read(n)
        try:
            s = self.dev.bulkRead(0x80|self.ep, self.maxin, self.to)
            self.inb += ''.join(map(lambda x: chr(x), s))
        except:
            pass
        return self.__read(n)


    def write(self, s):
        self.dev.bulkWrite(self.ep, s, self.to)
        #usleep(5000)


    def devastate(self):
        try:
            while len(self.dev.bulkRead(0x80|self.ep, self.maxin, 1000)) > 0:
                pass
        except:
            pass
        try:
            for i in range(0, 18*1024):
                self.dev.bulkWrite(self.ep, '\xff', 1000)
        except:
            pass


class Master:
    RESET               = 0
    SESSION_OPEN        = 1
    TRANSFER_BLOCK_CMD  = 2
    TRANSFER_BLOCK      = 3
    TRANSFER_DATA_TYPE  = 4
    UNKNOWN             = 63

    MREQH = ">IBBHIHH"
    SRSPH = ">IBBHIHH"
    SRSP_SESSION_OPEN = ">BBH"
    SRSP_TRANSFER_BLOCK = ">H"

    MREQH_SIZE = struct.calcsize(MREQH)
    SRSPH_SIZE = struct.calcsize(SRSPH)
    SRSP_SESSION_OPEN_SIZE = struct.calcsize(SRSP_SESSION_OPEN)
    SRSP_TRANSFER_BLOCK_SIZE = struct.calcsize(SRSP_TRANSFER_BLOCK)

    MREQ_SIGNATURE = 0x66617374
    SRSP_SIGNATURE = 0x74736166

    def __init__(self, dev, at=False, debug=False, crcerr=999999, zipped=False, datatype=2):
        self.sid = 0
        self.tid = 0
        self.dev = dev
        self.at = at
        self.debug = debug
        self.crcerr = crcerr
        self.crcerrnb = 1
        self.mreq = []
        self.srsp = []
        self.version = 2
        self.max_transfer = 16
        self.sigerr = False
        self.zipped = zipped
        self.datatype = datatype


    @staticmethod
    def mreq_ack(op):
        return op | 0x80


    @staticmethod
    def mreq_nack(op):
        return op | 0x40


    def close(self):
        self.dev.close()

    def wipe(self):
        self.dev.devastate()


    def read(self, n):
        r = self.dev.read(n)
        if self.debug:
            print("IN")
            hexdump(r)
        return r


    def write(self, s):
        self.dev.write(s)
        if self.debug:
            print("OUT")
            hexdump(s)

    def stp_over_at(self, device, baud):
        ok_msg = "OK\r\n"
        time.sleep(1)

        print("Starting AT negociation")
        self.dev.devastate()
        self.dev.write("AT\n")
        data = self.dev.read(len(ok_msg))
        if data != ok_msg:
            print("Remote didn't answered to AT command")
            print(f"Received: '{data}' ({len(data)} bytes)")
            exit(1)

        print(f"Setting baudrate {baud}")
        self.dev.write("AT+IPR=%d\n"%baud)
        data = self.dev.read(len(ok_msg))
        if data != ok_msg:
            print("Remote failed to set baudrate")
            print(f"Received: '{data}' ({len(data)} bytes)")
            exit(1)
        self.dev.close()
        self.dev = SerialDev(device, 60, baud)

        time.sleep(0.1)
        print("Starting STP")
        retry = 3
        self.dev.serial.timeout = 1
        while retry !=0:
            self.dev.write("AT+STP\n")
            data = self.dev.read(len(ok_msg))
            if data == ok_msg:
                break
            retry = retry - 1
            print("Remote failed to start STP")
            self.dev.serial.timeout = 0.1
            data += self.dev.read(256)
            self.dev.serial.timeout = 1
            print(f"Received: '{data}' ({len(data)} bytes)")
            if retry <= 0:
                exit(1)
        self.dev.serial.timeout = 3
        print("STP started")


    def make_mreq(self, op, pld):
        assert self.MREQH_SIZE + len(pld) <= self.max_transfer

        self.crcerrnb += 1
        if self.crcerrnb % self.crcerr == 0: crcerr = True
        else: crcerr = False

        if len(pld) != 0:
            pcrc = crc16(pld, crcerr)
        else:
            pcrc = 0

        hcrc = crc16(struct.pack(self.MREQH,
                           self.MREQ_SIGNATURE,
                           op, self.sid, len(pld),
                           self.tid,
                           0, pcrc), crcerr)
        return struct.pack(self.MREQH,
                           self.MREQ_SIGNATURE,
                           op, self.sid, len(pld),
                           self.tid,
                           hcrc, pcrc)


    def decode_srsp(self, p):
        if len(p) < self.SRSPH_SIZE:
            raise MException("SRSP header too small: %d" % len(p))

        (magic, op, sid, plen, tid, hcrc, pcrc) = struct.unpack(self.SRSPH, p[:self.SRSPH_SIZE])

        if magic != self.SRSP_SIGNATURE:
            raise MException("Wrong SRSP signature: 0x%08X" % magic)

        if hcrc != 0:
            chcrc = crc16(struct.pack(self.SRSP, self.SRSP_SIGNATURE, op, sid, plen, tid, 0, pcrc))
            if hcrc != chcrc:
                raise MException("Wrong header CRC: 0x%04X" % hcrc)

        return dict(op=op, sid=sid, tid=tid, plen=plen, pcrc=pcrc)


    def verify_srsp_data(self, p, plen, pcrc):
        if len(p) != plen:
            raise MException("Wrong payload size: %d" % plen)
        if plen != 0 and pcrc != 0 and pcrc != crc16(p):
            raise MException("Wrong payload CRC: 0x%04X" % pcrc)


    def verify_session(self, i, op):
        if i['op'] != Master.mreq_ack(op):
            raise MException("Invalid op: 0x%02x" % i['op'])
        if i['sid'] != self.sid:
            raise MException("Invalid sid: %d" % i['sid'])
        if i['tid'] != self.tid:
            raise MException("Invalid sid: %d" % i['tid'])


    def decode_open_session(self, p):
        if len(p) < self.SRSP_SESSION_OPEN_SIZE:
            raise MException("OpenSession data too small: %d" % len(p))
        (ok, ver, mts) = struct.unpack(self.SRSP_SESSION_OPEN, p[:self.SRSP_SESSION_OPEN_SIZE])
        if not ok:
            raise MException("OpenSession: failed to open")

        self.version = ver
        self.max_transfer = mts
        print(f"Session opened: version {ver}, max transfer {mts} bytes")

        if ver >= 2:
            if self.zipped:
                self.datatype += 1
            self.send_data_type()


    def reset(self, closing=False):
        while True:
            self.write(self.make_mreq(self.RESET, []))
            r = self.read(self.SRSPH_SIZE)
            if closing:
                self.close()
                break
            i = self.decode_srsp(r)
            if i['op'] == Master.mreq_nack(self.UNKNOWN):
                continue
            if i['op'] != Master.mreq_ack(self.RESET):
                raise MException("Reset: invalid op: 0x%02x" % i['op'])
            break

        self.sid = 0
        self.tid = 0


    def noex_reset(self, closing=False):
        try:
            self.reset(closing)
        except MException:
            pass


    def send_data_type(self):
        self.tid += 1
        while True:
            pld = struct.pack(">L", self.datatype)
            self.write(self.make_mreq(self.TRANSFER_DATA_TYPE, pld))
            self.write(pld)
            r = self.read(self.SRSPH_SIZE)
            i = self.decode_srsp(r)
            if i['op'] == Master.mreq_nack(self.UNKNOWN):
                continue
            if i['op'] != Master.mreq_ack(self.TRANSFER_DATA_TYPE):
                raise MException("data_type: invalid op: 0x%02x" % i['op'])
            break


    def open_session(self):
        self.sid = 1
        self.tid = 1

        while True:
            self.write(self.make_mreq(self.SESSION_OPEN, []))
            r = self.read(self.SRSPH_SIZE)
            i = self.decode_srsp(r)
            if i['op'] == Master.mreq_nack(self.UNKNOWN):
                continue
            break

        self.verify_session(i, self.SESSION_OPEN)
        r = self.read(self.SRSP_SESSION_OPEN_SIZE)
        self.verify_srsp_data(r, i['plen'], i['pcrc'])
        self.decode_open_session(r)
        self.tid += 1


    def send_data(self, data, trials=4):
        size = len(data)
        total = size

        while size:
            l = min(size, self.max_transfer-self.MREQH_SIZE)
            l = min(l, 2048-32) # 31x0 mii limitation

            # send transfer block command
            while True:
                pld = struct.pack(">H", l)
                self.write(self.make_mreq(self.TRANSFER_BLOCK_CMD, pld))
                self.write(pld)
                self.tid += 1
                try:
                    r = self.read(self.SRSPH_SIZE)
                    i = self.decode_srsp(r)
                    if i['op'] == Master.mreq_nack(self.TRANSFER_BLOCK_CMD):
                        continue
                    if i['op'] == Master.mreq_nack(self.UNKNOWN):
                        self.tid -= 1
                        continue
                except MException:
                    raise
                break

            # send transfer block data
            while True:
                pld = data[:l]
                self.write(self.make_mreq(self.TRANSFER_BLOCK, pld))
                self.write(pld)
                self.tid += 1
                try:
                    r = self.read(self.SRSPH_SIZE)
                    i = self.decode_srsp(r)
                    if i['op'] == Master.mreq_nack(self.TRANSFER_BLOCK):
                        time.sleep(0.1)
                        continue
                    if i['op'] == Master.mreq_nack(self.UNKNOWN):
                        time.sleep(0.1)
                        self.tid -= 1
                        continue
                except MException:
                    raise
                r = self.read(self.SRSP_TRANSFER_BLOCK_SIZE)
                break

            (residue, ) = struct.unpack(">H", r)
            if residue > 0:
                print(f"Slave didn't consume {residue} bytes")
                l -= residue

            data = data[l:]
            size -= l
            self.progress("Sending %d bytes" % total, total - size, total)
        self.progressComplete()

        return True


    def progress(self, what, downloaded, total, barLen=40):
        percent = float(downloaded)/total
        hashes = '#' * int(round(percent*barLen))
        spaces = ' ' * (barLen - len(hashes))
        print(f'{what}: [{hashes}{spaces}] {int(round(percent*100)):3d} %', end='\r')
        sys.stdout.flush()


    def progressComplete(self):
        print("")


def mock(m):
    m.send_data("Hello, cruel world!")
    m.send_data("Prepare for a huge transaction.")
    m.send_data("There could be random data corruption ...")
    m.send_data("I know that togather we can stand it.")
    m.send_data("So let's begin!")
    m.send_data("Nhah! " * 4096)


class args(object):
    pass


def signal_handler(m, signum, frame):
    if m.sigerr == False:
        sys.stderr.write("\nQuiting...")
        m.sigerr = True
        if m.tid > 1:
            m.noex_reset(True)
            sys.stderr.write("done\n")
            sys.exit(1)
    sys.stderr.write("\rQuiting...forced\n")
    sys.exit(2)


def start(device, dev_type, elf=None, baud=3686400, retry=None, debug=None, crcerr=999999, AT=True, zip=False, datatype=2):
    dev = None
    if AT == True:
        init_baud = 115200
    else:
        init_baud = baud

    try:
        # The base-two logarithm of the window size, which therefore ranges between 512 and 32768
        # 12 is 4096K
        wbits = 12
        if dev_type == "fifo":
            dev = FifoDev(device, 2, 2)
            push = mock
        if dev_type == "unix":
            dev = UnixDev(device, 2, 2)
            push = mock
        if dev_type == "serial":
            dev = SerialDev(device, 60, init_baud)
            data = elf.read()
            if zip:
                compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, wbits)
                data = compress.compress(data)
                data += compress.flush()
            b = bytearray(data)
            push = lambda m: m.send_data(b)
        if dev_type == "usb":
            (vid, pid) = map(lambda x: string.atoi(x, 16), device.split(':'))
            dev = UsbDev(vid, pid, 1)
            data = elf.read()
            if zip:
                compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, wbits)
                data = compress.compress(data)
                data += compress.flush()
            b = bytearray(data)
            push = lambda m: m.send_data(data)
    except:
        raise

    m = Master(dev, at=AT, debug=debug, crcerr=crcerr, zipped=zip, datatype=datatype)

    signal.signal(signal.SIGINT, partial(signal_handler, m))

    tries = 3
    while True:
        try:
            m.wipe()
            if AT == True:
                m.stp_over_at(device, baud)
            m.reset()
            m.open_session()
            push(m)
            dev.set_timeout(1)
            m.reset(True)
        except MException as ex:
            print(f"\nException: {str(ex)}")
            m.noex_reset()
            if retry:
                if tries > 0:
                    print(f"Retrying from scratch ({tries})...")
                    tries -= 1
                    if dev_type == "serial":
                        # sleep to drop '+SYSTART'
                        time.sleep(1)
                        m.dev.close()
                        m.dev = SerialDev(device, 60, init_baud)
                    continue
            else:
                print("Retry on error not enabled, giving up...")
                exit(-1)
        break

def main():
    parser = argparse.ArgumentParser(description='STP arguments parser')
    parser.add_argument('-fifo', help='Use unix fifo as device', nargs=1, required=False)
    parser.add_argument('-unix', help='Use unix socket as device', nargs=1, required=False)
    parser.add_argument('-serial', help='Use serial as device', nargs=1, required=False)
    parser.add_argument('-usb', help='Use usb as device', nargs=1, required=False)
    parser.add_argument('elf_file', help='Elf file to transfer', nargs=1)

    parser.add_argument('-b', '--baudrate', help='Set serial baudrate (default is 3686400)',
                        type=int, default=3686400)
    parser.add_argument('--noAT', help='Bypass AT commands to start STP', action="store_true",
                        default=False)
    parser.add_argument('-z', '--zip', help='Compress data before sending it using zlib',
                        action="store_true", default=False)
    parser.add_argument('-retry', help='Retry on error', action="store_true")
    parser.add_argument('-debug', help='Enable debugging messages', action="store_true")
    parser.add_argument('-crcerr', help='Add CRC errors each N transfer', type=int, default=999999)

    parser.parse_args(namespace=args)

    app = sys.argv[0]

    devices = 0
    if args.fifo:
        devices += 1
    if args.unix:
        devices += 1
    if args.serial:
        devices += 1
    if args.usb:
        devices += 1
    if devices != 1:
        usage(app)

    baud = None
    elf = None
    try:
        if args.fifo:
            dev = args.fifo[0]
            dev_type = "fifo"
        if args.unix:
            dev = args.unix[0]
            dev_type = "unix"
        if args.serial:
            dev = args.serial[0]
            dev_type = "serial"
            elf = open(args.elf_file[0], "rb")
            baud = args.baudrate
        if args.usb:
            dev = args.usb[0]
            dev_type = "usb"
            elf = open(args.elf_file[0], "rb")
    except:
        raise
        usage(app)

    retry = args.retry
    debug = args.debug
    crcerr = args.crcerr

    start(dev, dev_type, elf=elf, baud=baud, retry=retry, debug=debug, crcerr=crcerr, AT=not args.noAT, zip=args.zip, datatype=2)

if __name__ == "__main__":
    main()


