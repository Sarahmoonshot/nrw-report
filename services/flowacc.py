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
    """Fetch last30Days data for a given device and month/year"""
    year, month = year or datetime.today().year, month or datetime.today().month
    date_str = f"{month:02d}-01-{year}"
    url = f"{API_URL}?device={DEVICE_CODES[device]}&date={date_str}"
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
    """Show single device report"""
    data = fetch_device_data(device, year, month)
    total, days = calculate_total_flow(data)
    print(f"\n📊 {device.upper()} | Total: {total:.2f} m³ | Valid: {days}")
    display_last30days(device, data)
    return {"device": device, "year": year, "month": month, "total_flow": total, "valid_days": days, "last30days": data}

def fetch_all_reports(year=None, month=None):
    """Show reports for all devices"""
    reports = {}
    for device in DEVICE_CODES:
        reports[device] = run_flow_report(device, year, month)
    return reports

def display_last30days(device, data):
    """Print last30Days array"""
    formatted = [("null" if x is None else f"{x}") for x in data]
    print(f"Last30Days for {device.upper()}: [{','.join(formatted)}]")

"""
def main():
    print("\n🌊 FLOW REPORT GENERATOR")
    print("Select one of the following:")
    print("1. Single Device Report")
    print("2. All Devices Summary")

    choice = input("Enter choice (1 or 2): ").strip()

    # Ask user for year/month
    year = input("Enter year (e.g., 2025): ").strip()
    month = input("Enter month (1-12): ").strip()
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        print("[ERROR] Invalid year/month, defaulting to current month")
        from datetime import datetime
        today = datetime.today()
        year, month = today.year, today.month

    if choice == "1":
        device_input = input(f"🔧 Enter device ({', '.join(DEVICE_CODES.keys())}): ").strip().lower()
        if not device_input:
            device_input = "libona"
        run_flow_report(device_input, year, month)

    elif choice == "2":
        print(f"\n📊 Fetching data for all devices ({month:02d}-{year})...")
        all_data = fetch_all_reports(year, month)
        print("\n" + "=" * 50)
        print(f"📊 ALL DEVICES SUMMARY ({month:02d}-{year})")
        print("=" * 50)
        for device_name, stats in all_data.items():
            print(f"{device_name.upper():15} | Total: {stats['total_flow']:8.2f} m³ | Valid: {stats['valid_days']}")
            display_last30days(device_name, stats['last30days'])
            print("-" * 50)

    else:
        print("Invalid selection. Please enter 1 or 2.")
"""

if __name__ == "__main__":
    main()
