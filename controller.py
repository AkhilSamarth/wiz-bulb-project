"""Functions for controlling bulbs."""
import network


def _constrain_value(value, min, max) -> int:
    """Returns value if within bounds set by min/max (both inclusive), else returns min/max if value is too low/high respectively."""
    if value < min:
        return min
    elif value > max:
        return max

    return value


def _construct_set_payload(params: dict) -> dict:
    """Constructs a payload for setting the bulb using the given params."""
    payload = {
        "method": "setPilot",
        "env": "pro",
        "params": params
    }

    return payload


def set_temp_and_brightness(temp: int, brightness: int) -> None:
    temp = _constrain_value(temp, 2200, 6000)
    brightness = _constrain_value(brightness, 10, 100)

    params = {
        "state": True,
        "temp": temp,
        "dimming": brightness
    }
    payload = _construct_set_payload(params)

    network.send_payload_to_bulbs(payload)


def set_state(state: bool) -> None:
    params = {
        "state": state
    }
    payload = _construct_set_payload(params)

    network.send_payload_to_bulbs(payload)
