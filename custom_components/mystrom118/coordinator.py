"""MyStrom Button Plus Data Coordinator."""

from __future__ import annotations

from json import loads
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import ACTION_LOOKUP, COMPONENT_LOOKUP
from .MyStromAPIs import MyStromListener

_LOGGER = logging.getLogger(__name__)


class MyStromCoordinator(DataUpdateCoordinator):
    """MyStrom Websocket API Coordinator."""

    def __init__(self, hass: HomeAssistant, ws_listener: MyStromListener):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="MyStrom Data Coordinator",
        )
        ws_listener.callbacks.append(self._async_update_data)

    async def _async_update_data(self, data: bytes | str):
        """Function's called once WebSocket Data received."""
        # yes this is the only way I managed to make it not shout at me

        if isinstance(data, bytes):
            data = data.decode()

        data = loads(data)

        component = COMPONENT_LOOKUP[data["index"]]
        action = ACTION_LOOKUP[data["action"]]

        data = {
            "mac": data["mac"],
            "component": component,
            "action": action,
            "battery": data["bat"],
            "temperature": data["temp"],
            "humidity": data["rh"],
        }

        self.async_set_updated_data(data)
