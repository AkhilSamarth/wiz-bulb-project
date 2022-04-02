import json


with open("config.json") as f:
    CONFIG = json.load(f)


def get_bulb_ips() -> list:
    return CONFIG["bulbIps"]
