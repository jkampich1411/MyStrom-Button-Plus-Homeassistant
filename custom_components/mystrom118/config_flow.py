"""Config flow for MyStrom Button Plus."""

import logging

from requests import Request
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import CONF_HOOK, CORE_DEVICE_NAME, DATA_CONF, DOMAIN
from .discovery import discover
from .MyStromAPIs import MyStromAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, info=None):
        """User step."""
        if info is not None:
            if info["configure_type"] == "Discovery":
                return await self.async_step_discovery()
            else:
                return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("configure_type"): vol.In(["Discovery", "Manual"])}
            ),
        )

    async def async_step_discovery(self, info=None):
        """Automated Discovery step."""
        if info is not None:
            if "checkme" in info:
                if info["checkme"]:
                    task = self.hass.async_create_task(
                        discover(self.hass, 11), f"{DOMAIN}_discovery"
                    )

                    try:
                        devices = await task
                    except Exception:
                        return self.async_abort(reason="discovery_failed")
                    return await self.async_step_discovery(info=devices)
                else:
                    return await self.async_step_discovery()

            elif isinstance(info, list):
                usable_devices = [dev for dev in info if dev["device"] == 118]

                if len(usable_devices) == 0:
                    return self.async_show_form(
                        step_id="discovery",
                        data_schema=vol.Schema({}),
                        errors={
                            "base": "No MyStrom Button Plus devices found. Press submit to continue with manual discovery."
                        },
                    )

                session = async_create_clientsession(self.hass, False)
                for count, value in enumerate(usable_devices):
                    usable_devices[count]["api"] = MyStromAPI(value["ip"], session)

                return await self.async_step_configure(usable_devices)

            else:
                return await self.async_step_manual()

        return self.async_show_form(
            step_id="discovery",
            data_schema=vol.Schema({vol.Required("checkme"): bool}),
        )

    async def async_step_manual(self, info=None):
        """Manual Discovery."""
        if info is not None:
            if "ip_address" in info:
                # We got data!
                api = MyStromAPI(
                    info["ip_address"], async_create_clientsession(self.hass, False)
                )
                is_online = await api.is_online()
                if not is_online:
                    return self.async_abort(reason="no_devices_found")

                info = await api.deviceInfo()

                if info["type"] != 118:
                    return self.async_abort(reason="no_devices_found")

                datapackage = {
                    "mac": info["mac"],
                    "ip": info["ip"],
                    "api": api,
                }

                return await self.async_step_configure([datapackage])

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required("ip_address"): str,
                }
            ),
        )

    async def async_step_configure(self, info):
        """Configure MyStrom Button Plus entries."""
        if not isinstance(info, list) or len(info) == 0:
            return self.async_abort(reason="no_devices_found")

        # set unique id
        await self.async_set_unique_id(info[0]["mac"])
        self._abort_if_unique_id_configured()

        url = self.hass.data[DATA_CONF][CONF_HOOK]

        device = info[0]
        # for some reason theres no way to register multiple discovered devices so we're doing the first one that's discovered
        api = device["api"]
        await api.setSpecificAction(  # Change webhook via API (generic/generic is a catch all)
            "generic", "generic", Request(method="POST", url=url)
        )

        del device["api"]  # garbage collect the api since that's all we need to do

        return self.async_create_entry(
            title=CORE_DEVICE_NAME.format(mac=device["mac"]), data=device
        )
