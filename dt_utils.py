"""Utility functions relating to datetime logic."""
import datetime as dt

import config


def _get_sunset_time(date: dt.date) -> dt.time:
    """Returns the (approximate) sunset time for the given month and day (year is ignored)."""
    sunset_times = config.get_sunset_times()
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

    return (bucket_start_time + time_delta * (delta_days_to_start / bucket_width_days)).time()
