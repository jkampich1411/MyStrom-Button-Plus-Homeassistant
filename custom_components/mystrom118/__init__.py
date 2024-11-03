"""Integration of MyStrom Button Plus."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import EVENT_HOMEASSISTANT_STOP, HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_HOOK,
    CONF_HOST,
    DATA_CONF,
    DATA_COORDINATOR,
    DATA_WSLISTENER,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import MyStromCoordinator
from .MyStromAPIs import MyStromListener

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(CONF_HOST): cv.string,
            vol.Required(CONF_HOOK): cv.string
        })
    }, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up MyStrom Button Plus Integration."""
    conf = config[DOMAIN]
    hass.data.setdefault(DOMAIN, {})
    hass.data.setdefault(DATA_CONF, conf)

    websocket_listener = MyStromListener(
        conf[CONF_HOST],
        async_create_clientsession(hass, auto_cleanup=True),
        hass.loop,
    )
    websocket_listener.create_loop_task()
    hass.data[DATA_CONF][DATA_WSLISTENER] = websocket_listener

    data_coordinator = MyStromCoordinator(hass, websocket_listener)
    hass.data[DATA_CONF][DATA_COORDINATOR] = data_coordinator

    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STOP, lambda _: cleanup(hass, config)
    )

    return True


def cleanup(hass: HomeAssistant, config: ConfigType):
    """Cleanup on Home Assistant shutdown."""
    websocket_listener = hass.data[DATA_CONF][DATA_WSLISTENER]
    websocket_listener.kill()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up MyStrom Button Plus Entities."""
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload MyStrom Button Plus Entities."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
