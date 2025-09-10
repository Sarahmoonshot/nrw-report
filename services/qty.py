import time
import requests
from datetime import datetime
from collections import defaultdict

# -----------------------------
# token caching
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
    total_qty = sum(float(row.get("qtyM3", 0)) for row in all_data if row.get("qtyM3") is not None)
    return total_qty

def get_billed_qty_by_project(year, month):
    """Get billed quantities grouped by project/area"""
    year_month = f"{year}-{month:02d}"
    all_data = get_location_periods(year_month)
    
    project_data = defaultdict(lambda: {
        "total_qty": 0.0,
        "active_customers": 0,
        "percentage_complete": 0.0,
        "locations": []
    })
    
    for row in all_data:
        project = row.get("projectName", "Unknown Project")
        qty = float(row.get("qtyM3", 0) or 0)
        customers = int(row.get("activeCustomers", 0) or 0)
        loc_pctcomplete = float(row.get("percentageComplete", 0) or 0)
        location = row.get("location", "Unknown")
        
        project_data[project]["total_qty"] += qty
        project_data[project]["active_customers"] += customers
        project_data[project]["locations"].append({
            "location": location,
            "qty": qty,
            "customers": customers,
            "loc_pctcomplete": loc_pctcomplete
        })
    
    # Calculate weighted percentage complete for each project
    for project, data in project_data.items():
        if data["active_customers"] > 0:
            weighted_pct = sum(
                loc["customers"] * loc["loc_pctcomplete"] 
                for loc in data["locations"]
            ) / data["active_customers"]
            data["percentage_complete"] = weighted_pct
    
    return dict(project_data)

def get_overallpercentage_complete(year, month):
    data = get_location_periods(f"{year}-{month:02d}")
    total = sum(int(d.get("activeCustomers", 0)) for d in data)
    return round(sum(int(d.get("activeCustomers", 0)) * float(d.get("percentageComplete", 0)) for d in data) / total, 2) if total else 0.0

def calculate_WTP_billing_completion(records):
    total = sum(int(r.get("activeCustomers", 0)) for r in records)
    return sum(int(r.get("activeCustomers", 0)) * float(r.get("percentageComplete", 0)) for r in records) / total if total else 0.0

# -----------------------------
"""
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
    print(f"\n📊 Displaying ALL PROJECTS qtyM3 for: {year_month}\n")

    all_data = get_location_periods(year_month)

    # group totals by project
    project_totals = defaultdict(float)
    project_records = defaultdict(list)

    for row in all_data:
        project = row.get("projectName", "Unknown Project")
        qty = float(row.get("qtyM3", 0) or 0)
        project_totals[project] += qty
        project_records[project].append(row)

    # display per project totals with completion percentage
    for project, total in project_totals.items():
        # Calculate project completion percentage
        project_completion = calculate_WTP_billing_completion(project_records[project])
        
        print(f"📍 Project: {project}")
        print(f"   Product Total Flow (qtyM3): {total:.2f}")
        print(f"   Billed Completed (%): {project_completion:.2f}%")
        print("   Records:")
        
        for row in project_records[project]:
            location = row.get("location", "Unknown")
            qty = row.get("qtyM3", "N/A")
            location_pct = float(row.get("percentageComplete", 0) or 0)
            print(f"   - Location: {location}, Qty: {qty} m³, Billed Complete %: {location_pct:.1f}%")
        
        print("-" * 50)
        
    overall_pct = get_overallpercentage_complete(year, month)
    print(f"Overall Bill Complete (%): {overall_pct:.1f}%")
"""
if __name__ == "__main__":
    main()