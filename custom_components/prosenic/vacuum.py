"""Support for the Prosenic vacuum cleaner robot."""
import logging
from enum import Enum
from typing import Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.vacuum import (
    PLATFORM_SCHEMA,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    SUPPORT_BATTERY,
    SUPPORT_CLEAN_SPOT,
    SUPPORT_FAN_SPEED,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STOP,
    StateVacuumDevice,
    STATES,
    SUPPORT_PAUSE,
    STATE_RETURNING,
    ATTR_CLEANED_AREA,
    DOMAIN as VACUUM_DOMAIN
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_DEVICE_ID)
from pytuya import Device

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Prosenic Vacuum cleaner"
CONF_LOCAL_KEY = "local_key"
DATA_KEY = f"{VACUUM_DOMAIN}.{DOMAIN}"

ATTR_MOP_EQUIPT = "mob_equipt"
ATTR_CLEANING_TIME = "cleaning_time"
ATTR_ERROR = "error"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_LOCAL_KEY): vol.All(str, vol.Length(min=15, max=16)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)

SUPPORT_PROSENIC = (
        SUPPORT_STATE
        | SUPPORT_STOP
        | SUPPORT_RETURN_HOME
        | SUPPORT_FAN_SPEED
        | SUPPORT_BATTERY
        | SUPPORT_CLEAN_SPOT
        | SUPPORT_START
        | SUPPORT_PAUSE
)

STATE_CODE_TO_STATE = {
    0: STATE_IDLE,
    1: STATE_CLEANING,
    2: STATE_CLEANING,
    3: STATE_CLEANING,
    4: STATE_RETURNING,
    5: STATE_DOCKED,
    6: STATE_CLEANING,
    7: STATE_PAUSED,
    8: STATE_CLEANING
}


# rw=read/write, ro=read only
class Fields(Enum):
    POWER = 1  # rw
    FAULT = 11  # ro
    CLEANING_MODE = 25  # rw
    DIRECTION_CONTROL = 26  # rw
    FAN_SPEED = 27  # rw
    CURRENT_STATE = 38  # ro
    BATTERY = 39  # ro
    CLEAN_RECORD = 40  # ro
    CLEAN_AREA = 41  # ro
    CLEAN_TIME = 42  # ro
    SWEEP_OR_MOP = 49  # ro


class CleaningMode(Enum):
    SMART = "smart"
    WALL_FOLLOW = "wallfollow"
    MOP = "mop"
    CHARGE_GO = "chargego"
    SPRIAL = "sprial"
    #    IDLE="idle" #not settable
    SINGLE = "single"


class DirectionControl(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    TURN_LEFT = "turnleft"
    TURN_RIGHT = "turnright"
    STOP = "stop"


class FanSpeed(Enum):
    ECO = "ECO"
    NORMAL = "normal"
    STRONG = "strong"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Prosenic vacuum cleaner robot platform."""
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    host = config[CONF_HOST]
    device_id = config[CONF_DEVICE_ID]
    local_key = config[CONF_LOCAL_KEY]
    name = config[CONF_NAME]

    # Create handler
    _LOGGER.info("Initializing with host %s", host)

    device = Device(device_id, host, local_key, "device")
    device.version = 3.3

    robot = ProsenicVacuum(name, device)
    hass.data[DATA_KEY][host] = robot

    async_add_entities([robot], update_before_add=True)


class ProsenicVacuum(StateVacuumDevice):
    """Representation of a Prosenic Vacuum cleaner robot."""

    def __init__(self, name: str, device: Device):
        """Initialize the Prosenic vacuum cleaner robot."""
        self._name = name
        self._device = device

        self._state = dict()
        self._last_command: Optional[CleaningMode] = None
        self._available = False

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def state(self) -> STATES:
        """Return the status of the vacuum cleaner."""
        try:
            if self._get_field(Fields.FAULT) != 0:
                return STATE_ERROR

            return STATE_CODE_TO_STATE[int(self._get_field(Fields.CURRENT_STATE))]
        except (KeyError, ValueError):
            _LOGGER.error(
                "STATE not supported: %d",
                self._state,
            )
            return None

    @property
    def battery_level(self) -> Optional[int]:
        """Return the battery level of the vacuum cleaner."""
        try:
            return int(self._get_field(Fields.BATTERY))
        except ValueError:
            return None

    @property
    def fan_speed(self):
        """Return the fan speed of the vacuum cleaner."""
        return self._get_field(Fields.FAN_SPEED)

    @property
    def fan_speed_list(self):
        """Get the list of available fan speed steps of the vacuum cleaner."""
        f: FanSpeed
        return [f.value for f in FanSpeed]

    @property
    def should_poll(self):
        return True

    @property
    def device_state_attributes(self):
        """Return the specific state attributes of this vacuum cleaner."""
        attrs = {}
        if self._state:
            attrs.update(
                {
                    ATTR_MOP_EQUIPT: True
                    if self._get_field(Fields.SWEEP_OR_MOP) == "mop"
                    else False,

                    ATTR_CLEANED_AREA: int(self._get_field(Fields.CLEAN_AREA)),
                    ATTR_CLEANING_TIME: int(self._get_field(Fields.CLEAN_TIME)),
                }
            )

            error = self._get_field(Fields.FAULT)
            if error != 0:
                attrs[ATTR_ERROR] = error
        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def supported_features(self):
        """Flag vacuum cleaner robot features that are supported."""
        return SUPPORT_PROSENIC

    @property
    def direction_list(self):
        """Get the list of available direction controls of the vacuum cleaner."""
        return [d.name.lower() for d in DirectionControl]

    def start(self):
        """Start or resume the cleaning task."""
        if self._last_command is not None:
            self._execute_command(Fields.CLEANING_MODE, self._last_command)
        else:
            self._execute_command(Fields.CLEANING_MODE, CleaningMode.SMART)

    def pause(self):
        """Pause the cleaning task."""
        if self._last_command is not None:
            self._execute_command(Fields.CLEANING_MODE, self._last_command)

    def stop(self, **kwargs):
        """Stop the vacuum cleaner."""
        self._execute_command(Fields.DIRECTION_CONTROL, DirectionControl.STOP)

    def return_to_base(self, **kwargs):
        """Set the vacuum cleaner to return to the dock."""
        self._execute_command(Fields.CLEANING_MODE, CleaningMode.CHARGE_GO)

    def clean_spot(self, **kwargs):
        """Perform a spot clean-up."""
        self._execute_command(Fields.CLEANING_MODE, CleaningMode.SPRIAL)

    def set_fan_speed(self, fan_speed, **kwargs):
        """Set fan speed."""
        try:
            self._execute_command(Fields.FAN_SPEED, FanSpeed[fan_speed.upper()])
        except Exception:
            _LOGGER.error(
                "Fan speed not recognized (%s). Valid speeds are: %s",
                fan_speed,
                self.fan_speed_list,
            )

    def update(self):
        """Fetch state from the device."""
        try:
            self._state = self._device.status()["dps"]

            self._available = True
        except Exception as e:
            _LOGGER.error("Got exception while fetching the state: %s", e)
            self._available = False

    def remote_control(self, direction: str):
        """Move vacuum with remote control mode."""
        try:
            self._execute_command(Fields.DIRECTION_CONTROL, DirectionControl[direction.upper()])
        except KeyError:
            _LOGGER.error(
                "Direction not recognized (%s). Valid directions are: %s",
                direction,
                self.direction_list,
            )

    def _execute_command(self, field: Fields, value: Enum):
        """Send command to vacuum robot by setting the correct field"""
        try:
            if field == Fields.CLEANING_MODE:
                self._last_command = value
            else:
                self._last_command = None

            self._device.set_value(field.value, value.value)
        except Exception:
            _LOGGER.error(
                "Could not execute command &s with value %s",
                field,
                value
            )

    def _get_field(self, field: Fields):
        """Tries to retrieve the passed field from the current state"""
        field_str = str(field.value)
        try:
            return self._state[field_str]
        except KeyError:
            _LOGGER.error(
                "Could not find field %s in the current state. The current state is %s",
                field_str,
                self._state
            )
            return None
