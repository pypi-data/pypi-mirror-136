"""Settings file exclusively for friendly -- not for friendly-traceback"""

import configparser
import os
import sys

from friendly_traceback import debug_helper
import appdirs


config_dir = appdirs.user_config_dir(
    appname="FriendlyTraceback", appauthor=False  # noqa
)
FILENAME = os.path.join(config_dir, "friendly.ini")

# I tried to install psutil to determine the kind of terminal (if any)
# that friendly was running in, but the installation failed.
# So I resort to a simpler way of determining the terminal if possible.
# For terminals, the assumption is that a single background color will
# be used for a given terminal type.

if "TERM_PROGRAM" in os.environ:  # used by VS Code
    terminal_type = os.environ["TERM_PROGRAM"]
elif "TERMINAL_EMULATOR" in os.environ:  # used by PyCharm
    terminal_type = os.environ["TERMINAL_EMULATOR"]
elif "TERM" in os.environ:  # Unix?
    terminal_type = os.environ["TERM"]
elif sys.platform == "win32":
    # The following might not be reliable.
    _ps = len(os.getenv("PSModulePath", "").split(os.pathsep))
    if _ps == 3:
        terminal_type = "powershell"
    elif _ps == 2:
        terminal_type = "cmd"
    else:
        terminal_type = ""
else:
    terminal_type = ""

ENVIRONMENT = None
# ENVIRONMENT is determined by the "flavour" of friendly.
# If a terminal type is identified, then the ENVIRONMENT variable
# would usually be a combination of the terminal_type and the flavour.

# Perhaps friendly will be used in environments where the user cannot
# create settings directories and files


def ensure_existence():
    """Ensures that a settings file exists"""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(FILENAME):
        config = configparser.ConfigParser()
        with open(FILENAME, "w") as config_file:
            config.write(config_file)


try:
    ensure_existence()
except Exception:  # noqa
    FILENAME = None


def read(*, option="unknown", environment=None):
    """Returns the value of a key in the current environment"""
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        section = "unknown"
        debug_helper.log("Unknown section")
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if section in config and option in config[section]:
        return config[section][option]
    return


def write(*, option="unknown", value="unknown", environment=None):
    """Updates the value of a key in the current environment.

    If the section does not already exist, it is created.
    """
    if not isinstance(option, str):
        debug_helper.log(f"option = {option} is not a string.")
        return
    if not isinstance(value, str):
        debug_helper.log(f"value = {value} is not a string.")
        return
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        section = "unknown"

    config = configparser.ConfigParser()
    config.read(FILENAME)
    if not config.has_section(section):
        config.add_section(section)
    config[section][option] = value
    with open(FILENAME, "w") as config_file:
        config.write(config_file)


def _remove_environment(environment=None):
    """Removes an environment (option) previously saved."""
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        print("No environment defined.")
        return
    config = configparser.ConfigParser()
    config.read(FILENAME)
    config.remove_section(section)
    with open(FILENAME, "w") as config_file:
        config.write(config_file)


def has_environment(environment=None):
    """Returns True if a section in the settings file has already been set
    for this environment.
    """
    if FILENAME is None:
        return False
    if environment is not None:
        section = environment
    else:
        section = ENVIRONMENT
    config = configparser.ConfigParser()
    config.read(FILENAME)
    return config.has_section(section)


def print_settings():
    """Prints the contents of the settings file"""
    config = configparser.ConfigParser()
    print("Current environment: ", ENVIRONMENT)
    config.read(FILENAME)
    config.write(sys.stdout)
