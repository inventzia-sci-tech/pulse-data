import datetime
import pytz
import calendar
import numpy as np
from datetime import date, timedelta, time, datetime
from typing import List


iso_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
standard_datetime_format = '%Y-%m-%d %H:%M:%S%z'

def parse_iso_datetime(s):
    return datetime.strptime(s, iso_datetime_format)


def parse_iso_date(s):
    return datetime.strptime(s, '%Y-%m-%d')


def format_to_isodatetime(dtm : datetime):
    return dtm.strftime(iso_datetime_format)


def generate_first_dates_of_months_in_period(start_date : date , end_date : date) -> List[date]:
    current_date = start_date.replace(day=1)  # Set the day to 1st to get the first day of the month
    end_date = end_date.replace(day=1)  # Ensure end_date is also the 1st to simplify comparison
    dates_list = []
    while current_date <= end_date:
        dates_list.append(current_date)
        # Move to the first day of the next month
        current_date += timedelta(days=32 - current_date.day)
        current_date = current_date.replace(day=1)
    return dates_list


def generate_dates(start_date : date, end_date : date, include_weekends : bool=False) -> List[date]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        if include_weekends or (current_date.weekday() < 5):  # 0-4 represent Monday to Friday
            dates.append(current_date)
        current_date += timedelta(days=1)
    return dates


def last_day_of_month(date):
    _, last_day = calendar.monthrange(date.year, date.month)
    return date.replace(day=last_day)


def last_business_day_of_month(date):
    last_d_month = last_day_of_month(date)
    # Check if the last day of the month is a weekend (Saturday or Sunday)
    if last_d_month.weekday() in [5, 6]:
        # If the last day is a weekend, find the previous Friday
        days_to_subtract = last_d_month.weekday() - 4  # 5 - 4 = 1 for Saturday, 6 - 4 = 2 for Sunday
        last_business_day = last_d_month - timedelta(days=days_to_subtract)
    else:
        # If the last day is a weekday, it is already the last business day
        last_business_day = last_d_month
    return last_business_day


def subtract_business_days(given_date : date, days_to_subtract : int) -> date:
    # Does not curate holidays...
    current_date = given_date
    while days_to_subtract > 0:
        current_date -= timedelta(days=1)
        # Check if the current day is a weekday (0-4 are Monday to Friday)
        if current_date.weekday() < 5:
            days_to_subtract -= 1
    return current_date


def get_years_list_between_dates(start_date : date, end_date : date):
    start_year = start_date.year
    end_year = end_date.year
    years_list = [year for year in range(start_year, end_year + 1)]
    return years_list


def from_unaware_datetime_to_locatized_datetime(dt : datetime, tzone : str):
    input_timezone = pytz.timezone(tzone)
    localized_datetime = input_timezone.localize(dt)
    return localized_datetime


def get_last_closing_datetime_in_chicago_to_utc(date_value : date):
    datetime_obj = datetime.combine(date_value, time(17, 0))
    chicago_tz = pytz.timezone('America/Chicago')
    return chicago_tz.localize(datetime_obj).astimezone(pytz.utc)


def from_date_time_tzone_to_localized_datetime(dt : date, tm : time, tzone : str):
    '''
        To obtain time you can do the following for example:
        input_time_str = "08:30"
        datetime.strptime(input_time_str, "%H:%M").time()
    '''
    # Combine the date and time
    combined_datetime = datetime.combine(dt, tm)
    return from_unaware_datetime_to_locatized_datetime(combined_datetime, tzone)
    
    
def nth_weekday_of_month(date : date,
                         weekday : int,
                         n : int) -> date:
    '''
     find the Nth occurrence of a specific weekday in the same month as the given date,
     weekday is an integer where 0 represents Monday, 1 represents Tuesday, and so on.
     n represents the Nth occurrence of the specified weekday.
     nth_weekday_of_month(given_date, weekday=2, n=3)  # <--- Gets you the third Wed of the month
    '''
    # Find the first day of the month
    first_day = date.replace(day=1)
    # Find the day of the week for the first day of the month (0 = Monday, ..., 6 = Sunday)
    first_day_weekday = first_day.weekday()
    # Calculate the number of days to add to reach the Nth occurrence of the specified weekday
    days_to_add = (weekday - first_day_weekday + 7) % 7 + (n - 1) * 7
    # Calculate the Nth occurrence of the specified weekday
    nth_weekday = first_day + timedelta(days=days_to_add)
    return nth_weekday


def convert_datetime64_array_to_utc_datetime(dt64array):
   unix_epoch = np.datetime64(0, 's')
   one_second = np.timedelta64(1, 's')
   seconds_since_epoch = (dt64array - unix_epoch) / one_second
   return [datetime.utcfromtimestamp(x) for x in seconds_since_epoch]


