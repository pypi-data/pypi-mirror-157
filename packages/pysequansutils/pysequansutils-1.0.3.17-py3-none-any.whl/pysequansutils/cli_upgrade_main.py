"""
Entry point for upgrade command of pysequans CLI
"""
from pykitcommander.kitprotocols import setup_kit
from pysequansutils.firmwareinterface import PermanentBridgeFirmwareInterface

from .upgrade import full_upgrade, get_firmware_version
from .status_codes import STATUS_SUCCESS
from .pysequans_errors import PysequansMinVersionError
from .atdriver import AtDriver
from .upgrade import BUNDLED_FW_VERSION

def upgrade_cli_handler(args):
    """
    Entry point for upgrade command of CLI
    """
    if args.action == "full":
        try:
            upgraded, active_version = full_upgrade(firmware=args.firmware,
                                                    force=args.force,
                                                    port=args.port,
                                                    serialnumber=args.serialnumber,
                                                    skip_programming=args.skip_program_provision_firmware,
                                                    skip_bridge=args.skip_enter_bridgemode)
            if upgraded:
                print(f"Successfully upgraded firmware to version '{active_version}'")
            else:
                print(f"Upgrade skipped. Current version is '{active_version}' (use -f to force downgrade)")
        except PysequansMinVersionError as min_version_err:
            print(f"ERROR - {min_version_err}")
            print("To force a full upgrade at your own risk use the --force flag")

        # Any errors will raise exceptions so if execution reached this statement the upgrade should have succeeded
        return STATUS_SUCCESS

    if args.action == "report":

        with PermanentBridgeFirmwareInterface(port=args.port,
                                              serialnumber=args.serialnumber,
                                              skip_programming=args.skip_program_provision_firmware) as fwinterface:
            atdriver = AtDriver(fwinterface=fwinterface, bridge_enabled=args.skip_enter_bridgemode)
            current_version = get_firmware_version(atdriver)
            print(f"Bundled Monarch 2 firmware: {BUNDLED_FW_VERSION}")
            print(f"Currently loaded Monarch 2 firmware: {current_version}")

        # Use the setup_kit function to leave the target in a clean state (i.e. leave the permanent bridge mode)
        # Since skip_programming is set no target programming will happen, only a target reset
        setup_kit('iotprovision', skip_programming=True, serialnumber=args.serialnumber)

        return STATUS_SUCCESS

    raise ValueError(f"Unknown action '{args.action}'")
