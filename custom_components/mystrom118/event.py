"""Integration for MyStrom Button Plus.

Take a look at the docs!
https://github.com/jkampich1411/hass-mystrom118-integration.
"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.event import (
    PLATFORM_SCHEMA,
    EventDeviceClass,
    EventEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CORE_DEVICE_MANUFACTURER,
    CORE_DEVICE_NAME,
    CORE_DEVICE_PRODUCT,
    DATA_CONF,
    DATA_COORDINATOR,
    DOMAIN,
)
from .coordinator import MyStromCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_MYSTROM_MAC = "mac_address"
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MYSTROM_MAC): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up."""
    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for btn_id in range(1, 5):
        entity = MyStromButtonEntity(
            hass.data[DATA_CONF][DATA_COORDINATOR], data["mac"], btn_id
        )
        entities.append(entity)

    for entity in entities:
        hass.data[DOMAIN][entity.unique_id] = entity

    async_add_entities(entities)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up."""
    mac = config[CONF_MYSTROM_MAC]

    entities = []
    for btn_id in range(1, 5):
        device = MyStromButtonEntity(
            hass.data[DATA_CONF][DATA_COORDINATOR], mac, btn_id
        )
        entities.append(device)

    for entity in entities:
        hass.data[DOMAIN][entity.unique_id] = entity

    async_add_entities(entities)


class MyStromButtonEntity(CoordinatorEntity, EventEntity):
    """MyStromButtonEntity."""

    event_types = ["SINGLE", "DOUBLE", "LONG"]

    def __init__(self, coordinator: MyStromCoordinator, macaddr, button_id):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=macaddr)

        self.coordinator = coordinator

        self.mac = macaddr
        self.button_id = button_id
        self.device_name = CORE_DEVICE_NAME.format(mac=macaddr)

        self._name = f"Button {button_id}"
        self._state = None
        self.attributes = {}

        self._attr_unique_id = f"mystrom_button_plus_{macaddr}_button{button_id}"
        self.unique_id = self._attr_unique_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data
        if data["mac"] != self.mac or data["component"] != f"BUTTON{self.button_id}":
            return

        self._state = data["action"]
        self._trigger_event(self._state, {})
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.mac)},
            name=self.device_name,
            manufacturer=CORE_DEVICE_MANUFACTURER,
            model=CORE_DEVICE_PRODUCT,
        )

    @property
    def name(self):
        """Return name."""
        return self._name

    @property
    def icon(self):
        """Return icon."""
        return "mdi:radiobox-marked"

    @property
    def device_class(self):
        """Return device_class."""
        return EventDeviceClass.BUTTON
