"""Constants for MyStrom Button Plus Integration."""
DOMAIN = "mystrom118"
PLATFORMS: list[str] = ["event", "sensor"]

CORE_DEVICE_NAME = "MyStron Button Plus {mac}"
CORE_DEVICE_MANUFACTURER = "myStrom AG"
CORE_DEVICE_PRODUCT = "MyStrom Button Plus"

CONF_HOST = "websocket_url"
CONF_HOOK = "webhook_url"
CONF_MAC = "mac_address"

DATA_CONF = "mystrom118_conf"
DATA_WSLISTENER = "WS"
DATA_COORDINATOR = "COORDINATOR"

COMPONENT_LOOKUP = {
    "0": "GENERIC",
    "1": "BUTTON1",
    "2": "BUTTON2",
    "3": "BUTTON3",
    "4": "BUTTON4",
    "5": "TEMPERATURE",
    "6": "HUMIDITY",
}

ACTION_LOOKUP = {
    "1": "SINGLE",
    "2": "DOUBLE",
    "3": "LONG",
    "6": "BATTERY",
    "13": "GENERIC",
    "28": "OVER_VALUE",
    "29": "UNDER_VALUE",
}
