"""
pysequansutils CLI: "pysequans"
"""
import sys
import logging
import argparse
import os
import textwrap

from logging import getLogger
from logging.config import dictConfig
from appdirs import user_log_dir
import yaml
from yaml.scanner import ScannerError
from pykitcommander.kitcommandererrors import KitConnectionError

from .status_codes import STATUS_SUCCESS, STATUS_FAILURE
from .cli_upgrade_main import upgrade_cli_handler
from .upgrade import BUNDLED_FW_VERSION
from .upgrade import prompt_for_license_agreement_acceptance

try:
    #pylint: disable=no-name-in-module
    from .version import VERSION, BUILD_DATE, COMMIT_ID
except ImportError:
    print("Version info not found!")
    VERSION = "0.0.0"
    COMMIT_ID = "N/A"
    BUILD_DATE = "N/A"

def print_kit_status(error):
    """
    Print details from KitConnectionError exception due to none or too many kits
    matching serial number specification (if any)

    :param error: KitConnectionError exception object
    :type error: :class `pykitcommander.kitcommandererrors.KitConnectionError` object
    """
    # There must be exactly one tool connected, or user must disambiguate with (partial)
    # serial number
    logger = getLogger(__name__)
    if not error.value:
        logger.error("No suitable kits found")
    elif len(error.value) > 1:
        logger.error("Multiple kits found.")
        logger.error("Please specify serial number ending digits for the one you want")
        for tool in error.value:
            logger.error("Tool: %s Serial: %s Device: %s",
                         tool["product"][:16],
                         tool["serial"][:20],
                         tool["device_name"])
    else:
        # If exactly one was found, something is wrong with it, expect reason in msg
        tool = error.value[0]
        logger.error("Tool: %s Serial: %s Device: %s: %s",
                     tool["product"][:16],
                     tool["serial"][:20],
                     tool["device_name"],
                     error.msg)

def setup_logging(user_requested_level=logging.WARNING, default_path='logging.yaml',
                  env_key='MICROCHIP_PYTHONTOOLS_CONFIG'):
    """
    Setup logging configuration for this CLI

    :param user_requested_level: Logging level requested
    :type user_requested_level: int log level as defined by logging module
    :param default_path: Default path to logging configuration YAML file.  This one will be used unless a different
        path is specified through the environment variable given by env_key.
    :type default_path: str
    :param env_key: Name of environment variable that can be used to override the default logging configuration YAML
        file path
    :type env_key: str
    """
    # Logging config YAML file can be specified via environment variable
    value = os.getenv(env_key, None)
    if value:
        path = value
    else:
        # Otherwise use the one shipped with this application
        path = os.path.join(os.path.dirname(__file__), default_path)
    # Load the YAML if possible
    if os.path.exists(path):
        try:
            with open(path, 'rt', encoding="UTF-8") as file:
                # Load logging configfile from yaml
                configfile = yaml.safe_load(file)
                # File logging goes to user log directory under Microchip/modulename
                logdir = user_log_dir(__name__, "Microchip")
                # Look through all handlers, and prepend log directory to redirect all file loggers
                num_file_handlers = 0
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        configfile['handlers'][handler]['filename'] = os.path.join(
                            logdir, configfile['handlers'][handler]['filename'])
                        num_file_handlers += 1
                if num_file_handlers > 0:
                    # Create it if it does not exist
                    os.makedirs(logdir, exist_ok=True)

                if user_requested_level <= logging.DEBUG:
                    # Using a different handler for DEBUG level logging to be able to have a more detailed formatter
                    configfile['root']['handlers'].append('console_detailed')
                    # Remove the original console handlers
                    try:
                        configfile['root']['handlers'].remove('console_only_info')
                    except ValueError:
                        # The yaml file might have been customized and the console_only_info handler might
                        # already have been removed
                        pass
                    try:
                        configfile['root']['handlers'].remove('console_not_info')
                    except ValueError:
                        # The yaml file might have been customized and the console_only_info handler might
                        # already have been removed
                        pass
                else:
                    # Console logging takes granularity argument from CLI user
                    configfile['handlers']['console_only_info']['level'] = user_requested_level
                    configfile['handlers']['console_not_info']['level'] = user_requested_level

                # Root logger must be the most verbose of the ALL YAML configurations and the CLI user argument
                most_verbose_logging = min(user_requested_level, getattr(logging, configfile['root']['level']))
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        level = getattr(logging, configfile['handlers'][handler]['level'])
                        most_verbose_logging = min(most_verbose_logging, level)
                configfile['root']['level'] = most_verbose_logging
            dictConfig(configfile)
            return
        except ScannerError:
            # Error while parsing YAML
            print(f"Error parsing logging config file '{path}'")
        except KeyError as keyerror:
            # Error looking for custom fields in YAML
            print(f"Key {keyerror} not found in logging config file")
    else:
        # Config specified by environment variable not found
        print(f"Unable to open logging config file '{path}'")

    # If all else fails, revert to basic logging at specified level for this application
    print("Reverting to basic logging.")
    logging.basicConfig(level=user_requested_level)

def main():
    """
    Entrypoint for installable CLI

    Configures the top-level CLI and parses the arguments
    """
    # Shared switches.  These are inherited by subcommands (and root) using parents=[]
    common_argument_parser = argparse.ArgumentParser(add_help=False)
    common_argument_parser.add_argument("-v", "--verbose",
                                        default="info",
                                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                                        help="Logging verbosity/severity level")

    parser = argparse.ArgumentParser(
        parents=[common_argument_parser],
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''\
    pysequans: a command line interface for Microchip pysequansutils

    basic usage:
        - pysequans <command> <action> [-switches]
            '''),
        epilog=textwrap.dedent(f'''usage examples:
        Do a full upgrade of Sequans Monarch 2 platform to version {BUNDLED_FW_VERSION}
        The upgrade will be skipped if the Monarch 2 platform firmware already is up to date,
        i.e.  version number of currently running firmware >= {BUNDLED_FW_VERSION}
        - pysequans upgrade full

        Do a forced full upgrade/downgrade of Sequans Monarch 2 platform, disregarding the version check
        - pysequans upgrade full --force

        Do a full upgrade, but using dedicated bridge firmware already programmed in target
        - pysequans upgrade full --sprov --sbridge

        Do a full upgrade, but use a specified dup file instead of the bundled firmware file
        Note that this option will not do any version checking
        The Sequans Monarch 2 platform will always be programmed with the provided firmware
        - pysequans upgrade full --firmware my_firmware.dup
        '''))

    # Global switches that are all "do X and exit"
    parser.add_argument("-V", "--version", action="store_true",
                        help="Print pysequans version number and exit")
    parser.add_argument("-R", "--release-info", action="store_true",
                        help="Print pysequans release details and exit")

    # Global switches that are common to all commands
    parser.add_argument("-s", "--serialnumber",
                        type=str,
                        help="USB serial number of the kit to use\n"
                        "This is optional if only one kit is connected\n"
                        "Substring matching on end of serial number is supported")
    parser.add_argument("-P", "--port",
                        type=str, default=None,
                        help="Serial port name for communication with kit\n"
                        "This option is only used when port name is not successfully auto-detected")

    # First 'argument' is the command, which is a sub-parser
    subparsers = parser.add_subparsers(title='commands',
                                       dest='command',
                                       description="use one and only one of these commands",
                                       help="for additional help use pysequans <command> --help")
    # Make the command required but not for -V or -R arguments
    subparsers.required = not any(arg in ["-V", "--version", "-R", "--release-info"] for arg in sys.argv)

    # Upgrade command
    upgrade_command = subparsers.add_parser(name='upgrade',
                                            formatter_class=lambda prog: argparse.RawTextHelpFormatter(
                                            prog, max_help_position=0, width=80),
                                            help='functions related to Sequans Monarch 2 platform firmware upgrade',
                                            parents=[common_argument_parser])
    upgrade_command.add_argument('action',
                                 help=(f'''\
\nupgrade actions:
- full: does a full firmware upgrade of Monarch 2 platform
    Default is to upgrade to version {BUNDLED_FW_VERSION} using bundled firmware
- report: read and report Monarch 2 platform firmware version
'''),
                                 choices=['full', 'report'])

    upgrade_command.add_argument("-f", "--force", action="store_true",
        help="Force upgrade/downgrade, i.e. disregard version of currently loaded firmware\n"
        "This option is ignored when a specific firmware file is configured using the --firmware argument")

    upgrade_command.add_argument("--sprov", "--skip-program-provision-firmware",
        action="store_true", dest="skip_program_provision_firmware",
        help="Skip programming provisioning firmware.\n"
             "Setting this option indicates that the target already is programmed with provisioning firmware or\n"
             "a permanent bridge, in which case the --skip-enter-bridge switch should also be enabled.\n"
             "NOTE: This is an advanced option and may break the process")

    upgrade_command.add_argument("--sbridge", "--skip-enter-bridgemode",
        action="store_true", dest="skip_enter_bridgemode",
        help="Skip command to enable bridge mode in target firmware.\n"
             "Setting this option indicates that the target is programmed with permanent bridge firmware\n"
             "NOTE: This is an advanced option and may break the process")

    upgrade_command.add_argument("--fw", "--firmware", type=str,
        help="Sequans Monarch 2 platform firmware (dup file)\n"
        f"Optional, if not specified the bundled firmware (version {BUNDLED_FW_VERSION}) will be used\n"
        "When this argument is used no version check is performed,\n"
        "i.e. the Monarch 2 platform will always be programmed with the specified firmware file",
        dest="firmware")

    upgrade_command.add_argument("-r", "--report", action="store_true",
                                 help="Just read and report Sequans Monarch 2 platform firmware version\n"
                                 "No upgrade will be done")


    # Parse
    args = parser.parse_args()

    # Setup logging
    setup_logging(user_requested_level=getattr(logging, args.verbose.upper()))
    logger = logging.getLogger(__name__)

    # Dispatch
    if args.version or args.release_info:
        print(f"pysequansutils version {VERSION}")
        if args.release_info:
            print(f"Build date:  {BUILD_DATE}")
            print(f"Commit ID:   {COMMIT_ID}")
            print(f"Installed in {os.path.abspath(os.path.dirname(__file__))}")
        return STATUS_SUCCESS

    if args.skip_enter_bridgemode and not args.skip_program_provision_firmware:
        print("ERROR - Argument mismatch: Provisioning firmware requires bridge mode command so\n"
              "if using --skip-enter-bridge then --skip-program-provision-firmware must also be used.\n"
              "In other words the target must be programmed with permanent bridge upfront")
        return STATUS_FAILURE

    try:
        if args.command == "upgrade":
            # Upgrading to new firmware requires acceptance of the license agreement
            if not prompt_for_license_agreement_acceptance():
                return STATUS_FAILURE
            return upgrade_cli_handler(args)
    except KitConnectionError as connection_error:
        print_kit_status(connection_error)
        return STATUS_FAILURE
    except Exception as exc:
        logger.error("Operation failed with %s: %s", type(exc).__name__, exc)
        logger.debug(exc, exc_info=True)    # get traceback if debug loglevel

    return STATUS_FAILURE

if __name__ == "__main__":
    sys.exit(main())
