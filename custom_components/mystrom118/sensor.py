"""Integration for MyStrom Button Plus.

Take a look at the docs!
https://github.com/jkampich1411/hass-mystrom118-integration.
"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature
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

    entities = [
        MyStromTemperatureEntity(hass.data[DATA_CONF][DATA_COORDINATOR], data["mac"]),
        MyStromHumidityEntity(hass.data[DATA_CONF][DATA_COORDINATOR], data["mac"]),
        MyStromBatteryVoltageEntity(
            hass.data[DATA_CONF][DATA_COORDINATOR], data["mac"]
        ),
    ]

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

    entities = [
        MyStromTemperatureEntity(hass.data[DATA_CONF][DATA_COORDINATOR], mac),
        MyStromHumidityEntity(hass.data[DATA_CONF][DATA_COORDINATOR], mac),
        MyStromBatteryVoltageEntity(hass.data[DATA_CONF][DATA_COORDINATOR], mac),
    ]

    for entity in entities:
        hass.data[DOMAIN][entity.unique_id] = entity

    async_add_entities(entities)


class MyStromTemperatureEntity(CoordinatorEntity, SensorEntity):
    """Representation of a MyStrom Button Temperature sensor."""

    def __init__(self, coordinator: MyStromCoordinator, macaddr) -> None:
        """Set up."""
        super().__init__(coordinator, context=macaddr)

        self.coordinator = coordinator
        self.mac = macaddr
        self.device_name = CORE_DEVICE_NAME.format(mac=macaddr)

        self._name = "Temperature"
        self._state = None
        self.attributes = {}

        self._attr_unique_id = f"mystrom_button_plus_{macaddr}_temperature"
        self.unique_id = self._attr_unique_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

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
    def device_class(self):
        """Return device_class."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        """Return state_class."""
        return SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data
        if data["mac"] != self.mac or "temperature" not in data:
            return

        self._state = data["temperature"]
        self.async_write_ha_state()


class MyStromHumidityEntity(CoordinatorEntity, SensorEntity):
    """Representation of a MyStrom Button Humidity sensor."""

    def __init__(self, coordinator: MyStromCoordinator, macaddr) -> None:
        """Set up."""
        super().__init__(coordinator, context=macaddr)

        self.coordinator = coordinator
        self.mac = macaddr
        self.device_name = CORE_DEVICE_NAME.format(mac=macaddr)

        self._name = "Humidity"
        self._state = None
        self.attributes = {}

        self._attr_unique_id = f"mystrom_button_plus_{macaddr}_humidity"
        self.unique_id = self._attr_unique_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return PERCENTAGE

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
    def device_class(self):
        """Return device_class."""
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self):
        """Return state_class."""
        return SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data
        if data["mac"] != self.mac or "humidity" not in data:
            return

        self._state = data["humidity"]
        self.async_write_ha_state()


class MyStromBatteryVoltageEntity(CoordinatorEntity, SensorEntity):
    """Representation of a MyStrom Button Battery Voltage sensor."""

    def __init__(self, coordinator: MyStromCoordinator, macaddr) -> None:
        """Set up."""
        super().__init__(coordinator, context=macaddr)

        self.coordinator = coordinator
        self.mac = macaddr
        self.device_name = CORE_DEVICE_NAME.format(mac=macaddr)

        self._name = "Battery Voltage"
        self._state = None
        self.attributes = {}

        self._attr_unique_id = f"mystrom_button_plus_{macaddr}_battery_voltage"
        self.unique_id = self._attr_unique_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfElectricPotential.VOLT

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
    def device_class(self):
        """Return device_class."""
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        """Return state_class."""
        return SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data
        if data["mac"] != self.mac or "battery" not in data:
            return

        self._state = data["battery"]
        self.async_write_ha_state()
