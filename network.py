"""File to interface with bulbs using sockets."""
import json
import socket

import config


def _get_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", config.get_socket_port()))

    return sock


def _close_socket(sock: socket.socket) -> None:
    sock.shutdown()
    sock.close()


def send_payload_to_bulbs(payload: dict) -> None:
    """Function to send a JSON payload to the bulbs.

    The string "{bulb_mac_addr}" will be substituted with the appropriate MAC.
    """
    sock = _get_socket()

    for bulb_record in config.get_bulb_info():
        payload_str = json.dumps(payload).format(bulb_mac_addr=bulb_record["mac"])

        sock.sendto(payload_str, (bulb_record["ip"], config.get_bulb_port()))

    _close_socket(sock)
