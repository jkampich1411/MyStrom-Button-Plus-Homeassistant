"""Integration: MyStrom Button Plus; Contains class that listens for WebSocket events."""

import asyncio
import json
import logging

from aiohttp import ClientConnectorError, ClientSession, WSMsgType
import requests as r
import json

_LOGGER = logging.getLogger(__name__)


class MyStromListener:
    """Listens to MyStrom Translator WebSocket."""

    def __init__(self, url, session: ClientSession, loop: asyncio.AbstractEventLoop):
        """Initialize MyStromListener."""

        self.url = url
        self.session = session
        self.el = loop
        self.callbacks = []
        self.should_continue = True

    def kill(self):
        """Stop execution of Listener."""
        self.should_continue = False
        self.task.cancel()

    def create_loop_task(self, old_task=None):
        """Run Event Loop Task for Listening."""

        if not self.should_continue:
            return

        self.task = self.el.create_task(
            self._run_for_data(), name="MyStromDeviceListener"
        )
        self.task.add_done_callback(self.create_loop_task)

    async def _run_for_data(self):
        """Awaits WebSocket Data and posts to callback."""

        try:
            async with self.session.ws_connect(self.url) as ws:
                async for msg in ws:
                    if msg.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                        break

                    if msg.type in (WSMsgType.TEXT, WSMsgType.BINARY):
                        _LOGGER.debug("New Text Message; Distributing to callbacks")
                        # _LOGGER.debug(msg)
                        for cb in self.callbacks:
                            await cb(msg.data)
        except ClientConnectorError:
            _LOGGER.warning(
                "WebSocket connection failed, retrying in 10 seconds.", exc_info=True
            )

        if not self.should_continue:
            _LOGGER.debug(
                "Home Assistant is getting shut down, stopping WebSocket Listener."
            )
            return
        else:
            _LOGGER.error("WebSocket died, retrying connection in 10 seconds.")

        await asyncio.sleep(10)
        return


class MyStromAPI:
    """HTTP API for MyStrom Button Plus."""

    def __init__(self, deviceIp: str, session: ClientSession):
        """Initialize MyStromAPI."""
        self.session = session

        self.baseUrl = "http://\\device\\/api/v1".replace("\\device\\", deviceIp)

    async def req(
        self, method: str, url: str, raw="", json_data: dict = {}, headers: dict = {}
    ):
        """Request Function."""
        url = self.baseUrl + url

        if raw == "" and json_data != {}:
            async with self.session.request(
                method=method, url=url, json=json_data, headers=headers
            ) as response:
                data = await response.text()

        elif json_data == {} and raw != "":
            async with self.session.request(
                method=method, url=url, data=raw, headers=headers
            ) as response:
                data = await response.text()

        else:
            async with self.session.request(
                method=method, url=url, headers=headers
            ) as response:
                data = await response.text()

        return data

    async def is_online(self):
        """Check if device is online."""
        try:
            await asyncio.wait_for(self.req("GET", "/info"), timeout=5)
            return True
        except Exception:
            return False

    async def deviceInfo(self):
        """Get device information."""
        response = await self.req("GET", "/info")
        return json.loads(response)

    async def getSettings(self):
        """Get device settings."""
        response = await self.req("GET", "/settings")
        return json.loads(response)

    async def setSetting(self, setting):
        """Set device setting."""
        response = await self.req("POST", "/settings", json=setting)
        return json.loads(response)

    async def getAPsInRange(self):
        """Get access points in range."""
        res = await self.req("GET", "/scan")
        res = json.loads(res)

        parsed: list = [
            {"ssid": res[i], "strength": res[i + 1]}
            for i in range(0, len(res), 2)
            if res[i]
        ]

        return parsed

    def connectToAP(self, ssid, passwd, ifconfig: dict[str, str]):
        """Connect to an access point."""
        return self.req(
            "POST",
            "/connect",
            json={
                "ssid": ssid,
                "passwd": passwd,
                "ip": ifconfig["ip"],
                "mask": ifconfig["netmask"],
                "gw": ifconfig["gateway"],
                "dns": ifconfig["dns"],
            },
        )

    async def getSensorData(self):
        """Get sensor data."""
        response = await self.req("GET", "/sensors")
        return json.loads(response)

    async def getPastMeasurements(self):
        """Get past measurements."""
        response = await self.req("GET", "/meas")
        return json.loads(response)

    async def getAllActions(self):
        """Get all actions."""
        response = await self.req("GET", "/actions")
        return json.loads(response)

    async def getComponentActions(self, component: str):
        """Get actions for a specific component."""
        response = await self.req("GET", f"/actions/{component}")
        return json.loads(response)

    async def getSpecificAction(self, component: str, action: str):
        """Get a specific action for a component."""
        response = await self.req("GET", f"/action/{component}/{action}")
        return json.loads(response)

    def setSpecificAction(self, component: str, action: str, request: r.Request):
        """Set a specific action for a component."""
        url = str(request.url).replace("http://", "").replace("https://", "")

        customUrl = f"{str(request.method).lower()}://{url}"

        return self.req("POST", f"/action/{component}/{action}", raw=customUrl)
