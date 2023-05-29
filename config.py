import datetime as dt
import json
import logging
import sys
from typing import List


logger = logging.getLogger(__name__)


with open("config.json") as f:
    CONFIG = json.load(f)


def _get_current_year_dst_record() -> dict:
    current_year = dt.datetime.now().year

    dst_records = CONFIG["daylightSavingTime"]

    for record in dst_records:
        if record["year"] == current_year:
            return record

    logger.error(f"Missing DST config for current year={current_year}, stopping")

    sys.exit(1)


def get_bulb_ips() -> List[str]:
    return CONFIG["bulbIps"]


def get_bulb_port() -> int:
    return CONFIG["bulbPort"]


def get_socket_port() -> int:
    return CONFIG["socketPort"]


def get_sunset_times() -> List[dt.datetime]:
    raw_data = CONFIG["sunsetTimes"]
    current_year = dt.datetime.now().year

    sunset_times = []
    for record in raw_data:
        combined_datetime = f"{record['date']}-{record['time']}"

        sunset_times.append(dt.datetime.strptime(combined_datetime, "%m/%d-%H:%M").replace(year=current_year))
    
    return sorted(sunset_times)


def get_dst_start_date() -> dt.date:
    dst_record = _get_current_year_dst_record()

    return dt.datetime.strptime(dst_record["start"], "%m/%d").date().replace(year=dst_record["year"])


def get_dst_end_date() -> dt.date:
    dst_record = _get_current_year_dst_record()

    return dt.datetime.strptime(dst_record["end"], "%m/%d").date().replace(year=dst_record["year"])


def get_light_config() -> list:
    return CONFIG["lightConfig"]
