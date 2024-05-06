import time
from datetime import datetime, timedelta
from typing import Optional

import pytz
from tzlocal import get_localzone

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from timezonefinder import TimezoneFinder

from prettytable import PrettyTable


INPUT_FINISH_CODE = "q"


def get_location_timezone(location_name: str) -> Optional[datetime.tzinfo]:
    geolocator = Nominatim(user_agent="timezone_difference")
    while True:
        try:
            location = geolocator.geocode(location_name)
            break
        except GeocoderTimedOut:
            time.sleep(5)
            pass
    if location is None:
        return None

    timezone = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
    return pytz.timezone(timezone)


def get_time_difference(reference_timezone: datetime.tzinfo, location_timezone: datetime.tzinfo) -> timedelta:
    reference_time = reference_timezone.utcoffset(datetime.now())
    location_time = location_timezone.utcoffset(datetime.now())
    return location_time - reference_time


def format_time_difference(difference: timedelta):
    zero_delta = timedelta(0)
    if difference == zero_delta:
        return "0"
    if difference < zero_delta:
        return "-" + str(abs(difference))
    return "+" + str(difference)


def main():
    reference_location = input("Location for reference time (Press Enter to use local time): ")
    reference_timezone = None
    while reference_location:
        reference_timezone = get_location_timezone(reference_location)
        if reference_timezone is not None:
            break
        reference_location = input("Invalid location. Enter again: ")
    reference_timezone = get_localzone() if reference_timezone is None else reference_timezone

    print("Enter locations line by line to compare timezone. Press \"q\" to finish.")
    locations = []
    while True:
        location = input()
        if location == INPUT_FINISH_CODE:
            break
        if location:
            locations.append(location)

    time_differences = []
    for location in locations:
        location_timezone = get_location_timezone(location)
        if location_timezone is None:
            time_difference = 'Invalid location'
        else:
            time_difference = get_time_difference(reference_timezone, location_timezone)
            time_difference = format_time_difference(time_difference)
        time_differences.append(time_difference)

    table = PrettyTable()
    table.add_column('Location', locations)
    table.add_column('Time Difference', time_differences)
    print(table)

if __name__ == "__main__":
    main()
