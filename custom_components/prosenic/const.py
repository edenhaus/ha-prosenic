"""Constants for the prosenic integration."""
from homeassistant.components.vacuum import (
    DOMAIN as VACUUM_DOMAIN,
    STATES as VACUUM_STATES
)

DOMAIN = "prosenic"
DEFAULT_NAME = "Prosenic Vacuum cleaner"
DATA_KEY = f"{VACUUM_DOMAIN}.{DOMAIN}"

CONF_LOCAL_KEY = "local_key"
CONF_REMEMBER_FAN_SPEED = "remember_fan_speed"

ATTR_MOP_EQUIPPED = "mob_equipped"
ATTR_CLEANING_TIME = "cleaning_time"
ATTR_ERROR = "error"

# in seconds
REMEMBER_FAN_SPEED_DELAY = 6

STATE_MOPPING = "mopping"

STATES = VACUUM_STATES.append(STATE_MOPPING)
