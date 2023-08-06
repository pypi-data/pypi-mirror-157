"""
Firmware Serial-port-based communication interface

The class is instantiated with kit_info from pykitcommader.kitprotocols.setup_kit()
and uses the kit_info protocol_class to actually send FW commands to the kit.

"""
from logging import getLogger
from pyedbglib.serialport.serialcdc import SerialCDC
# This module uses pykitcommander:
# Functions in this module make use of the pykitcommander package to:
# - program application firmware on to the MCU based on the APPLICATION
# - handle protocol framing according to the firmware driver
from pykitcommander.kitprotocols import setup_kit
from pykitcommander.kitcommandererrors import KitCommunicationError

from .pysequans_errors import PysequansError

class PermanentBridgeFirmwareInterface():
    """
    Interface to provisioning firmware capable of permanent bridge mode

    Implementation of a subset of the provisioning firmware communication protocol.

    Actual firmware interaction is delegated to firmware driver supplied by pykitcommander:
    fwdriver.firmware_command(command, [<arg-list>][, blob])
    where args can be either integer, bytes, or str

    :param port: Serial port to connect to
    :type port: str, optional, defaults to the active kit
    :param serialnumber: USB serial number of kit/debugger to use.  Only needed if more than one kit is connected.
        Supports substring matching on end of serial number.
    :type serialnumber: str, optional, defaults to None
    :param skip_programming: Skip programming bridge firmware in target, i.e. just use whatever is already running
            on the target.  This option is useful if the user want to use a bridge firmware other
            than the one bundled with pykitcommander.
    :type skip_programming: bool, optional, defaults to False
    """
    DEFAULT_BAUD = 115200

    # ECC slots can only be written with complete words
    ECC_SLOT_WORD_SIZE_BYTES = 4

    def __init__(self, port=None, serialnumber=None, skip_programming=False):
        self.logger = getLogger(__name__)
        # FIXME: stopbits should come from kit_info
        self.stopbits = 1
        self.encoding = "UTF-8"
        self.fwdriver = None

        self.kit_info = setup_kit('iotprovision',
                                  skip_programming=skip_programming,
                                  serialnumber=serialnumber)
        self.led_defs = self.kit_info['kit_info']['leds']
        self.port = self.kit_info.get("port")
        if port:
            if self.port:
                self.logger.warning("Serial port '%s' auto-detected, ignoring request for port '%s'", self.port, port)
            else:
                # User provided port name only if not provided from pykitcommander
                self.port = port
        self.logger.debug("Using serial port '%s'", self.port)
        self.com = None
        self.bridge_mode = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_comport_handle(self):
        """
        Get serial port handle

        :returns: handle to serial port in use by this protocol
        """
        return self.com

    def get_firmware_driver(self):
        """
        Get firmware driver handle

        :returns: handle to firmware driver from pykitcommander
        """
        return self.fwdriver

    def open(self):
        """
        Open connection to target
        """
        self.com = SerialCDC(self.port, self.kit_info["protocol_baud"], timeout=10, stopbits=self.stopbits)
        # Instantiate protocol driver class if this firmware interface has one.
        protocol_class = self.kit_info.get("protocol_class")
        self.fwdriver = protocol_class(self.com) if protocol_class else None

    def close(self):
        """
        Close connection to target
        """
        # Note that if bridge mode is enabled LED access is not possible
        self.com.close()
        self.com = None
        self.fwdriver = None

    def synchronize(self):
        """
        Synchronize with firmware CLI
        """
        self.fwdriver.synchronize()

        # LED CONN (green) => provisioning firmware session active
        self.set_led_status(self.led_defs.CONNECTION_LED, "ON")

    def read_fw_version(self):
        """
        Reads the FW version of the provisioning FW

        :return: Firmware version
        :rtype: str
        """
        self.logger.debug("Target read FW version")
        response = self.fwdriver.firmware_command("MC+VERSION=FIRMWARE")
        self.logger.debug("FW version: %s", response)
        return response

    def enter_bridge_mode(self):
        """
        Enable bridge mode (permanent) in target

        In bridge mode target will just forward data from the host to the modem UART and forward data from the modem
        UART to the host.

        :returns: Empty string if OK
        :rtype: str
        :raises KitCommunicationError: If an unexpected response was received from target

        .. note:: Note that when in bridge mode no normal commands will work.  The only way to get out of bridge mode
            is to reset the target firmware (using the onboard debugger).
        """
        self.logger.debug("Entering Bridge Mode")

        if self.bridge_mode:
            self.logger.debug("Already in bridge mode")
            return ""

        # The blue LED used to indicate bridge mode (ie we're talking to the modem)
        self.set_led_status(self.led_defs.WIRELESS_LED, "ON")
        try:
            response = self.fwdriver.firmware_command("MC+BRIDGEMODE=PERMANENT")
        except KitCommunicationError as kitcommunicationerror:
            raise PysequansError("Could not connect to modem, do your kit have a Sequans Monarch 2 module?") from kitcommunicationerror
        if response == "":
            self.bridge_mode = True
        return response

    def exit_bridge_mode(self):
        """
        Exit bridge mode, not possible, kept for API compatibility

        Since this firmware interface implementation uses permanent bridge mode it is not possible to exit the bridge
        mode.  This function is just to ensure API compatibility with other firmware interface implementations that
        uses a temporary bridge mode that can be exited
        """
        self.logger.debug("Exit bridge mode not possible")

    def set_led_status(self, led, state):
        """
        Turn LED on or off

        .. note:: LEDs are not accessible while in bridge mode

        :param led: Name of led to manipulate as defined by pykitcommander.kitmanager.KitLeds classes.
            Use the led_defs instance variable of this class to get the correct name.
            Example: myfwinterface.led_defs.WIRELESS_LED
        :type led: str
        :param state: "ON" or "OFF" (case-insensitive)
        :type state: str
        """
        return self.fwdriver.firmware_command("MC+SETLED", [led, state])
