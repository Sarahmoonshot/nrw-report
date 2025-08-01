import requests
from datetime import datetime, timezone, timedelta
from calendar import monthrange

API_BASE_URL = "https://neptune.kyogojo.com/api/statistics/get-multiple?stations=LBNA-001&days="

def to_unix_ms(dt_obj):
    return int(dt_obj.replace(tzinfo=timezone.utc).timestamp() * 1000)

def fetch_batched_flowacc(unix_days, batch_size=30):
    data = []
    for i in range(0, len(unix_days), batch_size):
        batch = unix_days[i:i + batch_size]
        days_str = ",".join(str(day) for day in batch)
        try:
            print(f"[LOG] Fetching: {API_BASE_URL}{days_str}")
            response = requests.get(f"{API_BASE_URL}{days_str}")
            response.raise_for_status()
            payload = response.json().get("payload", {}).get("data", [])
            if payload and "flowAcc" in payload[0]:
                data.extend(payload[0]["flowAcc"])
        except Exception as err:
            print(f"[ERROR] Batch failed: {err}")
    return data

def generate_daily_flows(flow_data, tz_offset=8):
    grouped = {}
    for item in flow_data:
        utc_date = datetime.fromtimestamp(item["time"] / 1000).strftime("%Y-%m-%d")
        grouped.setdefault(utc_date, []).append(item)

    final_vals = {
        date: max(entries, key=lambda x: x["time"])["value"]
        for date, entries in grouped.items()
    }

    dates = sorted(final_vals.keys())
    return [
        {
            "date": dates[i],
            "flow": final_vals[dates[i]] - final_vals[dates[i - 1]]
        }
        for i in range(1, len(dates))
        if isinstance(final_vals[dates[i]], (int, float)) and isinstance(final_vals[dates[i - 1]], (int, float))
    ]

def run_monthly_flow_report(month_str):
    try:
        year, month = map(int, month_str.split("-"))
        start_date = datetime(year, month, 1).date()
    except:
        print(" Invalid format. Use YYYY-MM.")
        return None

    last_day = monthrange(year, month)[1]
    fetch_dates = [start_date - timedelta(days=1) + timedelta(days=i) for i in range(last_day + 1)]
    unix_days = [to_unix_ms(datetime.combine(d, datetime.min.time())) for d in fetch_dates]

    flow_data = fetch_batched_flowacc(unix_days)
    daily_flows = generate_daily_flows(flow_data)

    total = sum(d["flow"] for d in daily_flows)
    avg = total / len(daily_flows) if daily_flows else 0

    print("\n📅 Monthly Flow Report")
    print(f"Month: {month_str}")
    print(f"Total: {round(total, 2)} m³")
    print(f" Avg Daily: {round(avg, 2)} m³")
    print("Date\t\tFlow (m³)")
    print("-" * 30)
    for d in daily_flows:
        print(f"{d['date']}\t{round(d['flow'], 2)}")

    return {
        "total_flow": total,
        "average_daily_flow": avg,
        "daily_flows": daily_flows
    }

def run_daily_and_hourly_report(date_str=None):
    tz_offset = 8
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            print(" Invalid format. Use YYYY-MM-DD.")
            return
    else:
        target_date = (datetime.now(timezone.utc) + timedelta(hours=tz_offset)).date()

    # Daily
    fetch_days = [target_date - timedelta(days=1), target_date]
    unix_days = [to_unix_ms(datetime.combine(d, datetime.min.time())) for d in fetch_days]
    flow_data = fetch_batched_flowacc(unix_days)
    daily = generate_daily_flows(flow_data)
    print("\n📅 Daily Flow Report")
    print(f"Date: {target_date}")
    if daily:
        print(f" FlowAcc: {daily[0]['flow']} m³")
    else:
        print(" Insufficient data.")

    # Hourly
    hourly_timestamps = [
        datetime(target_date.year, target_date.month, target_date.day, h)
        for h in range(24)
    ]
    unix_hours = [to_unix_ms(t) for t in hourly_timestamps]
    flow_hourly_data = fetch_batched_flowacc(unix_hours)

    hourly_vals = {}
    for row in flow_hourly_data:
        local_hour = datetime.fromtimestamp(row["time"] / 1000).strftime("%Y-%m-%d %H:00")
        hourly_vals.setdefault(local_hour, []).append(row)

    hourly_final = {
        hour: max(v, key=lambda x: x["time"])["value"]
        for hour, v in hourly_vals.items()
    }
    sorted_hours = sorted(hourly_final.keys())
    hourly_flows = [
        {
            "hour": sorted_hours[i],
            "flow": hourly_final[sorted_hours[i]] - hourly_final[sorted_hours[i - 1]]
        }
        for i in range(1, len(sorted_hours))
        if isinstance(hourly_final[sorted_hours[i]], (int, float)) and isinstance(hourly_final[sorted_hours[i - 1]], (int, float))
    ]

    total_hourly = sum(d["flow"] for d in hourly_flows)
    avg_hourly = total_hourly / len(hourly_flows) if hourly_flows else 0

    print("\n Hourly Flow Report")
    print(f"Avg Hourly: {round(avg_hourly, 2)} m³")
    print("Hour\t\tFlow (m³)")
    print("-" * 30)
    for d in hourly_flows:
        print(f"{d['hour']}\t{round(d['flow'], 2)}")

    return {
        "daily": {
            "date": str(target_date),
            "flow": daily[0]["flow"] if daily else 0
        },
        "hourly": {
            "hourly_flows": hourly_flows,
            "avg_hourly": avg_hourly,
            "total_hourly": total_hourly
        }
    }

def main():
    print("\n🌊 FLOW REPORT GENERATOR")
    print("Select one of the following:")
    print("1. Monthly Report")
    print("2. Daily & Hourly Report")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        month_input = input("📅 Enter month (YYYY-MM): ").strip()
        run_monthly_flow_report(month_input)
    elif choice == "2":
        date_input = input("📆 Enter date (YYYY-MM-DD): ").strip()
        run_daily_and_hourly_report(date_input)
    else:
        print(" Invalid selection. Please enter 1 or 2.")

if __name__ == "__main__":
    main()