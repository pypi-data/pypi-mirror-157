"""
Utilities to upgrade firmware of Sequans Monarch 2 platform
"""
import os
import webbrowser
import datetime
from io import BytesIO
from sys import stdout
from logging import getLogger
from packaging import version
from pykitcommander.kitprotocols import setup_kit

from .pysequans_errors import PysequansError, PysequansMinVersionError
from .atdriver import AtDriver
from .firmwareinterface import PermanentBridgeFirmwareInterface
from . import stp

BUNDLED_FW = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fw", "GM02RB6Q_LR8.0.5.10-55042.dup")
# This is the UE version
BUNDLED_FW_VERSION = "8.0.5.10"
# Current firmware version must be at least this version to be guaranteed to work
FULL_UPGRADE_MIN_VERSION = "8.0.4.0"

# URL of the license agreement
SEQUANS_SPLA_URL = "https://www.sequans.com/legal/spla"

STP_DATATYPE_ELF = 2
STP_DATATYPE_CABA = 4

def _is_boot_mode_recovery(atdriver):
    """
    Helper to check that modem is in recovery boot mode

    :param atdriver: AtDriver instance, connection should be open when calling this function.
    :type atdriver: :class:`Atdriver` instance
    :returns: True if modem is in recovery boot mode
    :rtype: bool
    """
    logger = getLogger(__name__)
    logger.debug("Checking if modem is in recovery boot mode")
    response = atdriver.command_response('AT+SMOD?')
    if '4' in response:
        logger.debug("Modem is in recovery boot mode")
        return True

    logger.debug("Modem not in recovery boot mode")
    return False

def _is_boot_mode_fff(atdriver):
    """
    Helper to check that modem is in FFF boot mode

    :param atdriver: AtDriver instance, connection should be open when calling this function.
    :type atdriver: :class:`Atdriver` instance
    :returns: True if modem is in FFF boot mode
    :rtype: bool
    """
    logger = getLogger(__name__)
    logger.debug("Checking if modem is in FFF boot mode")
    response = atdriver.command_response('AT+SMOD?')
    if '2' in response:
        logger.debug("Modem is in FFF boot mode")
        return True

    logger.debug("Modem not in FFF boot mode")
    return False

def _get_data_type(data):
    """
    Identify data type

    The data type is used as input to the stp module
    :param data: Raw data
    :type data: bytes
    :returns: Data type
    :rytpe: int
    """
    if data[1] == 'E' and data[2] == 'L' and data[3] == 'F':
        return STP_DATATYPE_ELF

    # !ELF means CABA
    return STP_DATATYPE_CABA

def get_firmware_version(atdriver):
    """
    Get the (UE) firmware version from the Monarch 2 modem

    :param atdriver: AtDriver instance, connection should be open when calling this function.
    :type atdriver: :class:`Atdriver` instance
    :returns: Version string of Sequans LTE User Equipment (UE) firmware
    :rtype: str
    """
    logger = getLogger(__name__)
    if not _is_boot_mode_fff(atdriver):
        logger.debug("Booting to normal (FFF) mode to read firmware version")
        atdriver.command_no_response('AT+SMSWBOOT=1,1')
        # Wait for reboot to complete
        atdriver.read_until(b'+SYSSTART', retries=5)

    current_version = atdriver.command_response("ATI1")[0].strip('UE')
    logger.debug("Currently loaded Monarch 2 firmware: %s", current_version)

    return current_version

def full_upgrade(firmware=None, force=False, port=None, serialnumber=None, skip_programming=False, skip_bridge=False):
    """
    Perform full upgrade of Sequans Monarch 2 platform

    Either use bundled firmware or firmware provided as argument to this function.
    If using the bundled firmware the current version will be checked and upgrade skipped if already up to date unless
    the force argument is used.

    :param firmware: Path to firmware for Sequans Monarch 2 platform.
        If set to None the bundled firmware will be used for the upgrade.
    :type firmware: optional, str, defaults to None
    :param force: Force downgrade (i.e. disregard version check)
    :type force: optional, bool, defaults to False
    :param port: Serial port to use for communication, optional and only used if the kit does
            not support auto detection of virtual serial port
    :type port: optional, str, defaults to None
    :param serialnumber: USB serial number of kit/debugger to use.  Only needed if more than one kit is connected.
        Supports substring matching on end of serial number.
    :type serialnumber: optional, str, defaults to None
    :param skip_programming: Skip programming provisioning firmware in target.  Target must be programmed upfront
        either with provisioning firmware or a permanent bridge firmware (in which case the skip_bridge argument
        should also be set to True)
    :type skip_programming: optional, bool, defaults to False
    :param skip_bridge: Skip entering bridge mode.  Target must be programmed upfront with a permanent bridge firmware.
    :type skip_bridge: optional, bool, defaults to False
    :returns: Upgrade status and current firmware version after upgrade
    :rtype: bool, str
    :raises PysequansError: If any AT commands report failure
    """
    logger = getLogger(__name__)
    if firmware:
        logger.info("Performing full firmware upgrade of Sequans Monarch 2 platform using %s", firmware)
    else:
        logger.info("Performing full firmware upgrade of Sequans Monarch 2 platform to version %s", BUNDLED_FW_VERSION)

    with PermanentBridgeFirmwareInterface(port=port,
                                          serialnumber=serialnumber,
                                          skip_programming=skip_programming) as fwinterface:
        atdriver = AtDriver(fwinterface=fwinterface, bridge_enabled=skip_bridge)
        current_version = get_firmware_version(atdriver)
        logger.info("Currently loaded Monarch 2 firmware: %s", current_version)
        if not force and version.parse(current_version) < version.parse(FULL_UPGRADE_MIN_VERSION):
            # Use the setup_kit function to leave the target in a clean state (i.e. leave the permanent bridge mode)
            # Since skip_programming is set no target programming will happen, only a target reset
            setup_kit('iotprovision', skip_programming=True, serialnumber=serialnumber)
            raise PysequansMinVersionError(f"Current version is below {FULL_UPGRADE_MIN_VERSION},"
                                           " raster upgrade required")

        if not firmware:
            # Using bundled firmware
            firmware = BUNDLED_FW
            if not force and version.parse(BUNDLED_FW_VERSION) <= version.parse(current_version):
                logger.info("Firmware already up to date - skipping upgrade")
                # Use the setup_kit function to leave the target in a clean state (i.e. leave the permanent bridge mode)
                # Since skip_programming is set no target programming will happen, only a target reset
                setup_kit('iotprovision', skip_programming=True, serialnumber=serialnumber)
                return False, current_version
        else:
            firmware = os.path.normpath(firmware)

        # Assuming FFF boot mode since reading firmware version will require FFF boot mode
        # Note without reset (i.e. AT+CFUN=5,1 fails)
        response = atdriver.command_response('AT+CFUN=5')
        logger.debug("Entering recovery boot mode")
        # Even though this command will do a modem reset there will be no +SYSSTART URC afterwards
        atdriver.command_no_response('AT+SMSWBOOT=3,1')
        # The modem reset might take some time and there will be no response until the reset is completed so a few
        # retries might be needed
        retries = 5
        while retries:
            try:
                if _is_boot_mode_recovery(atdriver):
                    break
            except PysequansError:
                retries -= 1
                logger.debug("Waiting for modem to finish resetting, retrying...")

        if not retries:
            raise PysequansError("Unable to enter recovery boot mode")

        with open(firmware, "rb") as fwfile:
            data = fwfile.read()

        datatype = _get_data_type(data)
        dataio = BytesIO(data)

        atdriver.flush()
        atdriver.disable_echo()

        atdriver.command_response("AT+SMSTPU=\"ON_THE_FLY\"")

        # Save the port for later use
        port_used = fwinterface.port

    # Note that the following code assumes the target is in permanent bridge mode, i.e. that the AtDriver will not go
    # out of bridge mode when exiting the context manager
    logger.info("Downloading firmware...")
    logger.warning("This WILL take a few minutes. Do NOT disconnect your kit!")
    stp.start(device=port_used, dev_type="serial", elf=dataio, baud=115200, AT=False, zip=True, datatype=datatype)
    logger.info("Download done")

    # Note always skipping target programming as the bridge firmware should be in place already from the previous
    # interactions.
    # Note also that the original port argument is used to avoid a warning about auto detection of port overriding
    # user setting in the case that port was set to None. If the port_used variable was used instead a warning about
    # auto-detection overriding user specified port would always be printed.
    with PermanentBridgeFirmwareInterface(port=port,
                                          serialnumber=serialnumber,
                                          skip_programming=True) as fwinterface:
        atdriver = AtDriver(fwinterface=fwinterface, bridge_enabled=skip_bridge)
        logger.debug("Checking upgrade status...")
        response = atdriver.command_response('AT+SMUPGRADE?')
        if "success" in response[0]:
            logger.info("Upgrade succeeded")
        else:
            logger.debug("'AT+SMUPGRADE?': %s", response)
            raise PysequansError("Upgrade failed")

        logger.info("Booting back to normal (FFF) mode")
        atdriver.command_no_response('AT+SMSWBOOT=1,1')
        response = atdriver.read_response()
        if "+SYSSTART" not in response:
            logger.error("Unexpected response after reboot: %s", response)

        atdriver.flush()

        # Check new current version since it is unknown if the user brought his own firmware
        new_current_version = get_firmware_version(atdriver)

    # Use the setup_kit function to leave the target in a clean state (i.e. leave the permanent bridge mode)
    # Since skip_programming is set no target programming will happen, only a target reset
    setup_kit('iotprovision', skip_programming=True, serialnumber=serialnumber)

    return True, new_current_version

def prompt_for_license_agreement_acceptance():
    """
    Shows the user the license agreement for using the firmware by opening it in a web browser.
    Users are required to accept this agreement once per package revision.

    :returns: True if accepted, False otherwise
    :rtype: boolean
    """

    # Bypass this stage when running unit tests (stdout is mocked with a _pytest.capture.EncodedFile object)
    # isinstance() cannot be used here because in production builds the pytest dependency is not present
    # TODO: add proper unit tests for this stage
    if "pytest" in str(type(stdout)):
        return True

    license_dir = os.path.join(os.path.expanduser("~"), ".microchip-iot", "sequans")
    license_file = f"spla_acceptance_{BUNDLED_FW_VERSION}.txt"
    license_path = os.path.join(license_dir, license_file)
    print("Notice: the Monarch 2 firmware is provided by SEQUANS Communications and is subject to a license agreement.")
    if os.path.isfile(license_path):
        print(f"You have previously accepted the license agreement for using this firmware ({SEQUANS_SPLA_URL}).")
        return True
    print("In order to use this firmware package you must accept the license agreement.")
    if webbrowser.open(SEQUANS_SPLA_URL):
        print(f"The terms and conditions of use has been opened in your web browser ({SEQUANS_SPLA_URL}).")
    else:
        print(f"Download and review the terms and conditions of use here: {SEQUANS_SPLA_URL}.")
    prompt = "If you agree to the terms and conditions shown in the " \
             "SOFTWARE PACKAGE LICENSE AGREEMENT enter 'yes' at the prompt: "
    license_acceptance = input(prompt)
    if not license_acceptance.lower() == 'yes':
        print("You have declined the license agreement, and cannot use the firmware package.")
        return False
    # Leave breadcrumbs to not ask again for this package for this user
    now = datetime.datetime.now()
    os.makedirs(license_dir, exist_ok=True)
    with open(license_path, "w") as f:
        f.write(f"The license agreement for using Monarch 2 firmware package '{BUNDLED_FW_VERSION}' ")
        f.write(f"provided by SEQUANS Communications has been accepted on {now.strftime('%Y-%m-%d %H:%M:%S')}")
    return True
