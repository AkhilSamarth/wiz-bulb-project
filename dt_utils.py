"""Utility functions relating to datetime logic."""
import datetime as dt
from typing import List, Optional

import config


def _get_dst_normalized_sunset_times() -> List[dt.datetime]:
    """Returns sunset_times from config, but with all times in standard time instead of daylight time."""
    sunset_times = config.get_sunset_times()

    # add a time component of midnight for easy comparison
    dt_start_dt = dt.datetime.combine(config.get_dst_start_date(), dt.time(0, 0, 0))
    dt_end_dt = dt.datetime.combine(config.get_dst_end_date(), dt.time(0, 0, 0))

    for i, sunset_dt in enumerate(sunset_times):
        if sunset_dt >= dt_start_dt and sunset_dt < dt_end_dt:
            adjusted_hour = sunset_dt.hour - 1
            if adjusted_hour == -1:
                adjusted_hour = 23

            sunset_times[i] = sunset_dt.replace(hour=adjusted_hour)

    return sunset_times


def _get_sunset_time(date: dt.date) -> dt.time:
    """Returns the (approximate) sunset time for the given month and day (year is ignored)."""
    sunset_times = _get_dst_normalized_sunset_times()
    current_year = dt.datetime.now().year

    date = date.replace(year=current_year)

    # figure out which two dates from sunset_times the given date falls between (if equal, then start date == given date)
    for i, sunset_dt in enumerate(sunset_times):
        sunset_date = sunset_dt.date()

        if sunset_date > date:
            bucket_end_dt = sunset_dt
            bucket_start_dt = sunset_times[i - 1]
            break
    else:
        bucket_end_dt = sunset_times[0].replace(year=current_year+1)
        bucket_start_dt = sunset_times[-1]

    bucket_width_days = (bucket_end_dt.date() - bucket_start_dt.date()).days
    delta_days_to_start = (date - bucket_start_dt.date()).days

    # get times with date components equal to easily compare
    bucket_start_time = bucket_start_dt.replace(year=1900, month=1, day=1)
    bucket_end_time = bucket_end_dt.replace(year=1900, month=1, day=1)
    time_delta = bucket_end_time - bucket_start_time

    # sunset time is linearly interpolated from bucket start and end times
    sunset_time = (bucket_start_time + time_delta * (delta_days_to_start / bucket_width_days)).time()

    # correct for dst if needed
    dt_start_dt = dt.datetime.combine(config.get_dst_start_date(), dt.time(0, 0, 0))
    dt_end_dt = dt.datetime.combine(config.get_dst_end_date(), dt.time(0, 0, 0))
    date_with_time = dt.datetime.combine(date, dt.time(0, 0, 0))

    if date_with_time >= dt_start_dt and date_with_time < dt_end_dt:
        sunset_time = sunset_time.replace(hour=sunset_time.hour+1)

    return sunset_time


def _get_light_config_timeline() -> list:
    """Reads config and returns a list of dicts sorted by time.

    Each dict contains: {"time": dt.time, "temp": int, "brightness": int}"""
    light_config = config.get_light_config()

    # get today's sunset time
    today_date = dt.datetime.now().date()
    sunset_dt = dt.datetime.combine(date=today_date, time=_get_sunset_time(today_date))

    timeline = []
    for record in light_config:
        if "sunsetDelta" in record["time"].keys():
            sunset_delta = dt.timedelta(minutes=record["time"]["sunsetDelta"])

            timeline_record = {
                "time": (sunset_dt + sunset_delta).time(),
                "temp": record["light"]["temp"],
                "brightness": record["light"]["brightness"]
            }

            timeline.append(timeline_record)
        elif "exact" in record["time"].keys():
            exact_time = dt.datetime.strptime(record["time"]["exact"], "%H:%M").time()

            timeline_record = {
                "time": exact_time,
                "temp": record["light"]["temp"],
                "brightness": record["light"]["brightness"]
            }

            timeline.append(timeline_record)

    timeline.sort(key=lambda record: record["time"])

    return timeline


def get_current_light_config() -> Optional[dict]:
    """Returns the temp and brightness based on current time and the light config timeline.
    If no config is defined for the current time (i.e. current time < first config time or current time > last config time), returns None.

    Return format: {"temp": int, "brightness": int}
    """
    light_config_timeline = _get_light_config_timeline()

    current_time = dt.datetime.now().time()

    if current_time < light_config_timeline[0]["time"]:
        return None

    if current_time >= light_config_timeline[-1]["time"]:
        return None

    # get correct "bucket" from timeline
    for i, record in enumerate(light_config_timeline):
        if current_time < record["time"]:
            bucket_start = light_config_timeline[i - 1]
            bucket_end = record

            break

    # interpolate light data
    bucket_end_dt = dt.datetime.combine(date=dt.date(1900, 1, 1), time=bucket_end["time"])
    bucket_start_dt = dt.datetime.combine(date=dt.date(1900, 1, 1), time=bucket_start["time"])
    current_time_dt = dt.datetime.combine(date=dt.date(1900, 1, 1), time=current_time)

    bucket_size = bucket_end_dt - bucket_start_dt
    interp_factor = (current_time_dt - bucket_start_dt).seconds / bucket_size.seconds

    bucket_temp_delta = bucket_end["temp"] - bucket_start["temp"]
    bucket_brightness_delta = bucket_end["brightness"] - bucket_start["brightness"]

    return {
        "temp": int(bucket_temp_delta * interp_factor + bucket_start["temp"]),
        "brightness": int(bucket_brightness_delta * interp_factor + bucket_start["brightness"])
    }
