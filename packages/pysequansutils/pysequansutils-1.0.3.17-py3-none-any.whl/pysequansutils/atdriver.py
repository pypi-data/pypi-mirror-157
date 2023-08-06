"""
Simple driver for Monarch 2 AT modem control commands
"""
from logging import getLogger

from .pysequans_errors import PysequansError
class AtDriver():
    """
    Low-level AT modem command driver.
    """

    def __init__(self, fwinterface, bridge_enabled=False):
        """
        Connstructor. Will enter bridge mode. Protocol port must be opened by caller.

        :param fwinterface: Firmware interface object
        :type fwinterface: instance of a firmwareinterface class
        :param bridge_enabled: Bridge mode already enabled in target firmware.  This option is
            useful if the user brings their own permanent bridge firmware.  Note if skip_programming is True and
            bridge_enabled is False it means that the target firmware will not be programmed, but the firmware is
            assumed to not be in bridge mode, i.e. the atdriver will use MC+BRIDGEMODE command to enter bridge mode.
        :type bridge_enabled: optional, bool, defaults to False
        """
        self.logger = getLogger(__name__)
        self.fwinterface = fwinterface
        self.fwinterface.bridge_mode = bridge_enabled
        self.com = self.fwinterface.get_comport_handle()
        if not self.fwinterface.bridge_mode:
            self.fwinterface.synchronize()
            self.enter_bridge_mode()

    def __del__(self):
        self.exit_bridge_mode()

    def __enter__(self):
        self.enter_bridge_mode()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit_bridge_mode()

    def enter_bridge_mode(self):
        """
        Enter bridge mode
        """
        response = self.fwinterface.enter_bridge_mode()

        if response == "":
            # Wait for modem being ready after reset
            self.read_until(b"+SYSSTART", retries=2, timeout=1)
            # Flush any garbage the modem might still have in store
            garbage = self.com.read(self.com.in_waiting)
            if garbage:
                self.logger.debug("Garbage from modem: %s", garbage)
            self.ping()                         # Sanity check - this should not fail
        else:
            self.fwinterface.set_led_status(self.fwinterface.led_defs.ERROR_LED, "ON")
            raise PysequansError(f"Enter bridge mode failed, response: {response}")

    def exit_bridge_mode(self):
        """
        Exit bridge mode
        """
        self.fwinterface.exit_bridge_mode()

    def ping(self):
        """
        Send 'AT' command to modem and check response

        :returns: True if modem responds "OK"
        :rtype: bool
        """
        if self.fwinterface.bridge_mode:
            try:
                self.command_response("AT")
                return True
            except PysequansError as error:
                raise PysequansError(f"Modem ping failed: {error}")
        raise PysequansError("Modem ping attempted when not in bridge mode")

    def read_response(self):
        """
        Read response from modem.

        Response can be multiple lines either ended with "OK\\r\\n", "ERROR\\r\\n", or '>' so a simple read_until
        won't do. Returns list of response lines, blank lines and CR-LF stripped.
        """
        lines = []
        while True:
            line = self.com.read_until(b'\r\n')
            if not line:
                lines.append("ERROR: Timeout")
                return lines
            if line != b'\r\n':
                lines.append(line[0:-2].decode("utf-8", "ignore"))
                if line[0:2] == b"OK" or b"ERROR" in line:
                    return lines

    def read_until(self, string, expect=b'\r\n', retries=1, timeout=None):
        """
        Read complete lines until a line containing string is read.

        This function can be used to wait for expected URCs after a given command.

        :param string: String to wait for
        :type string: :class `collections.abc.ByteString` object
        :param expect: Optional character to read until if not whole line read
        :type expect: :class `collections.abc.ByteString` object
        :param retries: Number of times to retry after timeout waiting for string before giving up
        :type retries: optional, int, defaults to 1
        :param timeout: override timeout value for serial port read
        :type timeout: optional, float
        :returns: List of response lines.
        :rtype: list of str
        """
        # TODO: extend to do regular expression matching.
        lines = []
        original_timeout = self.com.timeout
        if timeout:
            self.com.timeout = timeout
        while True:
            line = self.com.read_until(expect)
            if not line:
                # For situations where the comm timeout is not enough.
                retries -= 1
                if retries > 0:
                    self.logger.debug("Timeout, retrying...")
                    continue
                lines.append("ERROR: Timeout")
                self.com.timeout = original_timeout
                return lines
            if line != b'\r\n':   # Strip blank lines
                if line.endswith(b'\r\n'):
                    lines.append(line[0:-2].decode("utf-8", "ignore"))
                else:
                    lines.append(line.decode("utf-8", "ignore"))
                if string in line:
                    self.com.timeout = original_timeout
                    return lines

    def disable_echo(self):
        """
        Disable modem echo on serial interface
        """
        self.command_no_response("ATE0")
        response = self.com.read(10)
        while self.com.inWaiting():
            pass
        response += self.com.read(1)
        # Don't check response, ATE0 is not necessarily supported

    def command_no_response(self, cmd, payload=None):
        """
        Send simple AT command, expect no response.

        .. note:: This function will just send the command and not wait for anything back from the modem,
            not even an "OK"

        :param cmd: Pre-formatted command.
        :type cmd: str
        :param payload: Optional payload sent in separate line. Payload length is appended
            as argument to cmd. Payload == "" will append payload length argument while None will not.
            (used for erase in AT+SQNSNVW command)
        :type payload: bytes
        """
        if payload is None:
            self.logger.debug(cmd)
            self.com.write((cmd + '\r').encode())
        else:
            self.logger.debug("%s,%d", cmd, len(payload))
            self.com.write((cmd + f",{len(payload)}\r").encode())
            if len(payload) > 0:
                self.com.read_until(b'>')
                self.com.write(payload)

    def command_response(self, cmd, payload=None):
        """
        Send simple AT command and expect a response

        This function should be used for every command that expects a response, even if it is just an "OK" response

        :param cmd: Pre-formatted command.
        :type cmd: string
        :param payload: Optional payload sent in separate line. Payload length is appended
            as argument to cmd. Payload == "" will append payload length argument while None will not.
            (used for erase in AT+SQNSNVW command)
        :type payload: bytes
        :returns: sanitized response (list of lines) Last line will be "OK" or "ERROR"
        :rtype: list of str
        """
        self.command_no_response(cmd, payload)
        response = self.read_response()
        if response[-1] != "OK":
            raise PysequansError(f"'{cmd}' failed: {response}")
        self.logger.debug(response)
        return response

    def write_nvm(self, datatype, slot, data=None, cmd="AT+SQNSNVW"):
        """
        Write data to NVM.

        Some special handling is required because the Sequans modem requires that certificate PEM files use '\\n'
        line endings, including the last line.

        :param datatype: "certificate" or "privatekey"
        :type datatype: str
        :param slot: Slot to write to, in the range 0-19
        :type slot: int
        :param data: data to write.  Passing in None will erase the slot.
        :type data: optional, bytes, defaults to None (erase)
        :param cmd:  AT command to use for write
        :type cmd: optional, str, defaults to "AT+SQNSNVW"
        """
        if not datatype in ["certificate", "privatekey"]:
            raise ValueError(f"Invalid data type for NVM write: {datatype}")

        if data:
            # Strip CR-LF line endings if present
            data = data.replace(b'\r\n', b'\n')
            # Sequans modem requires PEM input ends with newline
            if not data.endswith(b'\n'):
                self.logger.warning("Missing newline at end of data, appending")
                data += b'\n'
        else:
            data = b''

        self.command_response(cmd + f'="{datatype}",{slot}', data)

    def reset(self):
        """
        Software-reset modem, wait for startup to complete
        """
        self.command_response("AT^RESET")
        self.read_until(b'+SYSSTART')

    def flush(self):
        """
        Flush any remaining data in the serial interface pipe
        """
        # This code is taken directly from elf2sfff.py which was received from Sequans. Not sure what the purpose is,
        # but looks like some kind of flushing
        original_timeout = self.com.timeout
        # Short timeout since the purpose is to just flush what is already in the pipe
        self.com.timeout = 0.1
        self.com.read(256)
        self.com.timeout = original_timeout
