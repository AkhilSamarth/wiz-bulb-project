"""File to interface with bulbs using sockets."""
import json
import socket
from typing import List, Tuple

import config


def _get_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", config.get_socket_port()))

    return sock


def send_payload_to_bulbs(payload: dict) -> List[Tuple[str, dict]]:
    """Function to send a JSON payload to the bulbs.

    Returns a list of responses from each bulb with the format:
    [
        (
            <bulb_ip: str>,
            <response: dict>
        )
    ]

    The string "%BULB_MAC_ADDR%" will be substituted with the appropriate MAC.
    """
    sock = _get_socket()

    responses = []

    for bulb_record in config.get_bulb_info():
        payload_str = json.dumps(payload).replace("%BULB_MAC_ADDR%", bulb_record["mac"])

        sock.sendto(payload_str.encode(), (bulb_record["ip"], config.get_bulb_port()))

        response = sock.recvfrom(8192)
        response_ip = response[1][0]
        response_json = json.loads(response[0].decode())

        responses.append((response_ip, response_json))

    sock.close()

    return responses


print(send_payload_to_bulbs({"method":"getPilot","params":{}}))
