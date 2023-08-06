RAM_SIZE = {
    "nano": 0.5,
    "micro": 1,
    "small": 2,
    "medium": 4,
    "large": 8,
    "xlarge": 16,
    "2xlarge": 32,
}

HIBERNATION_SUPPORTED_VOLUME_TYPES = {"gp2", "gp3", "io1", "io2"}

SETTINGS_FILE = "instance_settings.json"

YES = False

from . import rollback, settings, util, relaunch, cli
