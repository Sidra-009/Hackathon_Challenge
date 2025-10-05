# utils/helpers.py
from datetime import datetime

def doy_to_date(year, doy):
    return datetime.strptime(f"{year}{doy}", "%Y%j")

def format_date_for_api(date_obj):
    return date_obj.strftime("%Y%m%d")
