import requests
from datetime import datetime

API_URL = "https://neptune.kyogojo.com/api/v4/statistics/get-flow-moving-average"
DEVICE_CODES = {
    "libona": "40961",
    "cotabato": "3993042952", 
    "dansolihon": "3993042948",
    "taguanao": "3993042954",
    "camarines_sur_1": "3993042950",
    "camarines_sur_2": "3993042951"
}

def fetch_device_data(device, year=None, month=None):
    """
    Fetch last30Days data for a given device code and month/year
    """
    year, month = year or datetime.today().year, month or datetime.today().month
    date_str = f"{month:02d}-01-{year}"

    url = f"{API_URL}?device={device}&date={date_str}"
    print(f"[LOG] Fetching: {url}")

    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json().get("payload", {}).get("last30Days", [])
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def calculate_total_flow(data):
    """Sum valid flows and count days"""
    valid = [x for x in data if x is not None]
    return sum(valid), len(valid)

def run_flow_report(device, year=None, month=None):
    """
    Show single device report
    """
    data = fetch_device_data(device, year, month)
    total, days = calculate_total_flow(data)
    print(f"\n📊 {device.upper()} | Total: {total:.2f} m³ | Valid: {days}")
    display_last30days(device, data)
    return {"device": device, "year": year, "month": month, "total_flow": total, "valid_days": days, "last30days": data}


def display_last30days(device, data):
    """
    Print last30Days array
    """
    formatted = [("null" if x is None else f"{x}") for x in data]
    print(f"Last30Days for {device.upper()}: [{','.join(formatted)}]")

def run_yearly_flow_report(device, year=None, verbose=True):
    """
    Collect flow report for all months in a given year for a specific device.
    """
    year = year or datetime.today().year
    yearly_total = 0.0
    yearly_valid_days = 0
    results = {}

    for month in range(1, 13):
        data = fetch_device_data(device, year, month)
        total, days = calculate_total_flow(data)

        if verbose:
            print(f"\n📊 {device.upper()} | {year}-{month:02d} | Total: {total:.2f} m³ | Valid: {days}")
            display_last30days(device, data)

        results[f"{year}-{month:02d}"] = {
            "total_flow": total,
            "valid_days": days,
            "last30days": data
        }

        yearly_total += total
        yearly_valid_days += days

    if verbose:
        print(f"\n📊 {device.upper()} | YEAR {year} | Total: {yearly_total:.2f} m³ | Valid: {yearly_valid_days}")

    return {
        "device": device,
        "year": year,
        "yearly_total": yearly_total,
        "yearly_valid_days": yearly_valid_days,
        "monthly_reports": results
    }

print ('congrats its running ')