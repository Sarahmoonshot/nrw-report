import time
import requests
from datetime import datetime

# -----------------------------
# token chaching
cached_token = None
token_expiry = 0

def get_cached_token():
    global cached_token, token_expiry
    now = time.time()

    if cached_token and now < token_expiry:
        return cached_token

    url = "https://p-673a9fc335d088609f177102-ocelotapigw.kyogojo.com/Identity/User/SignIn"
    headers = {"Content-Type": "application/json"}
    data = {
        "username": "admin.test@gmail.com",
        "password": "projectmoonshot"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()["data"]
        cached_token = result["access_token"]
        token_expiry = time.time() + result.get("expires_in", 3600)
        return cached_token
    except Exception as e:
        print(f"[ERROR] Token fetch failed: {e}")
        return None

# -----------------------------
# fetch data
def get_location_periods(year_month):
    token = get_cached_token()
    if not token:
        return []

    url = "https://p-673a9fc335d088609f177102-ocelotapigw.kyogojo.com/Billing/GetLocationPeriods"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "*/*"
    }
    params = {"yearMonth": year_month}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch location periods: {e}")
        return []

def get_billed_qty(year, month):
    year_month = f"{year}-{month:02d}"
    all_data = get_location_periods(year_month)
    filtered_data = [row for row in all_data if row.get("projectName") == "LIBONA WTP"]
    total_qty = sum(float(row.get("qtyM3", 0)) for row in filtered_data if row.get("qtyM3") is not None)
    return total_qty

def get_percentage_complete(year, month):
    year_month = f"{year}-{month:02d}"
    all_data = get_location_periods(year_month)
    filtered_data = [row for row in all_data if row.get("projectName") == "LIBONA WTP"]

    total_customers = sum(int(row.get("activeCustomers", 0)) for row in filtered_data)
    weighted_total = sum(
        int(row.get("activeCustomers", 0)) * float(row.get("percentageComplete", 0))
        for row in filtered_data
    )
    if total_customers == 0:
        return 0.0

    overall_percentage = weighted_total / total_customers
    return overall_percentage

# -----------------------------
def main():
    # auto compute prev month
    today = datetime.today()
    if today.month == 1:
        year = today.year - 1
        month = 12
    else:
        year = today.year
        month = today.month - 1

    year_month = f"{year}-{month:02d}"
    print(f"\n Displaying Libona WTP qtyM3 for: {year_month}")

    all_data = get_location_periods(year_month)
    filtered_data = [row for row in all_data if row.get("projectName") == "LIBONA WTP"]

    total_qty = sum(float(row.get("qtyM3", 0)) for row in filtered_data if row.get("qtyM3") is not None)

    print(f"\n📍 Project: LIBONA WTP")
    print(f"Product Total Flow (qtyM3): {total_qty:.2f}")
    print("\n Records:")
    for row in filtered_data:
        location = row.get("location", "Unknown")
        qty = row.get("qtyM3", "N/A")
        print(f"- Location: {location}, Qty: {qty} m³")

    overall_pct = get_percentage_complete(year, month)
    print(f"Overall Bill Complete (%): {overall_pct:.0f}%")

if __name__ == "__main__":
    main()