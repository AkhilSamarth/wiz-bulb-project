import json


with open("config.json") as f:
    CONFIG = json.load(f)


def get_bulb_info() -> list:
    return CONFIG["bulbInfo"]


def get_socket_port() -> int:
    return CONFIG["socketPort"]