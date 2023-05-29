"""Functions for controlling bulbs."""
import logging

import dt_utils
import network


logger = logging.getLogger(__name__)


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
    logger.info(f"Setting temp and brightness: temp={temp}, brightness={brightness}")

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
    logger.info(f"Setting bulb state: {state}")

    params = {
        "state": state
    }
    payload = _construct_set_payload(params)

    network.send_payload_to_bulbs(payload)


def set_bulb_based_on_timeline() -> None:
    """Sets the lightbulbs based on the timeline config."""
    logger.info("Setting bulb based on light timeline config")

    current_light_config = dt_utils.get_current_light_config()

    if current_light_config:
        set_temp_and_brightness(**current_light_config)
