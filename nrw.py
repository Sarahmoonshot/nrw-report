from flask import Flask, jsonify, request
from datetime import datetime
from services.qty import get_billed_qty_by_project, calculate_WTP_billing_completion
from services.flowacc import fetch_all_reports, DEVICE_CODES
app = Flask(__name__)

def calculate_nrw(total_flow, billed_qty):
    """Compute NRW volume and percentage.
    - If total_flow == 0 → NRW = 0
    - If billed_qty == 0 → NRW = 0
    - Otherwise, NRW = total_flow - billed_qty and % of total_flow
    """
    if not total_flow or not billed_qty:
        return 0, 0
    nrw_m3 = total_flow - billed_qty
    nrw_percent = (nrw_m3 / total_flow) * 100
    return nrw_m3, nrw_percent

def get_matched_device_code(name: str) -> str | None:
    """
    Match a WTP name or location string against DEVICE_CODES.
    - First, try exact key match (for WTP names).
    - Then, try substring match (for location names).
    """
    if not name:
        return None
    key = name.replace(" WTP", "").lower()
    if key in DEVICE_CODES:
        return DEVICE_CODES[key]

    for key_name, code in DEVICE_CODES.items():
        if key_name in key:
            return code
    return None

######### MONTHLY #########
@app.route("/nrw/monthly", methods=["GET"])
def get_monthly_nrw():
    month_str = request.args.get("month")
    if not month_str:
        return jsonify({"error": "Missing 'month' parameter (format: YYYY-MM)"}), 400
    try:
        year, month = map(int, month_str.split("-"))
    except ValueError:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM"}), 400

    billing = get_billed_qty_by_project(year, month)
    flow = fetch_all_reports(year, month)
    result = {}

    for wtp, info in billing.items():
        device = get_matched_device_code(wtp)
        wtp_key = wtp.replace(" WTP", "").lower()
        total_flow = flow.get(wtp_key, {}).get("total_flow", 0)
        total_bill = sum(float(loc.get("qty", 0)) for loc in info.get("locations", []))
        nrw_m3, nrw_pct = calculate_nrw(total_flow, total_bill)

        result[wtp.upper()] = {
            "billed_complete": f"{info.get('percentage_complete', 0):.2f}%",
            "total_flow": round(total_flow, 2),
            "total_bill_qty": round(total_bill, 2),
            "nrw_m3": round(nrw_m3, 2),
            "nrw_percent": round(nrw_pct, 2),
            "device_code": device,
            "areas": {}
        }

        for loc in info.get("locations", []):
            name = loc.get("location", "Unknown")
            bill = float(loc.get("qty", 0))
            area_device = get_matched_device_code(name) or device
            area_flow = flow.get(name.lower(), {}).get("total_flow", total_flow)
            area_nrw_m3, area_nrw_pct = calculate_nrw(area_flow, bill)

            result[wtp.upper()]["areas"][name] = {
                "billed_completed": f"{loc.get('loc_pctcomplete', 0):.2f}%",
                "billed_qty": round(bill, 2),
                "nrw_m3": round(area_nrw_m3, 2),
                "nrw_percent": round(area_nrw_pct, 2),
                "total_flow": round(area_flow, 2),
                "device_code": area_device
            }

    return jsonify(result)

######### DAILY  #########
@app.route("/nrw/daily", methods=["GET"])
def get_daily_nrw():
    """Return flattened daily NRW rows, filtered by WTP if given."""
    date_str = request.args.get("date")     
    wtp_filter = request.args.get("wtp")

    if not date_str:
        return jsonify({"error": "Missing 'date' parameter"}), 400

    try:
        fmt = "%Y-%m" if len(date_str) == 7 else "%Y-%m-%d"
        req_date = datetime.strptime(date_str, fmt).date()
    except ValueError:
        return jsonify({"error": "Invalid 'date'. Use YYYY-MM or YYYY-MM-DD"}), 400

    year, month = req_date.year, req_date.month
    next_month = datetime(year + (month == 12), (month % 12) + 1, 1)
    days_in_month = (next_month - datetime(year, month, 1)).days

    billing_data = get_billed_qty_by_project(year, month)
    flow_data = fetch_all_reports(year, month)

    device_flows = {}
    for wtp_key, fdata in flow_data.items():
        dev_code = DEVICE_CODES.get(wtp_key)
        if dev_code:
            device_flows[dev_code] = fdata.get("last30days", [])

    rows = []

    for wtp_name, bill_info in billing_data.items():
        device = get_matched_device_code(wtp_name)
        wtp_key = wtp_name.replace(" WTP", "").lower()
        daily_flows = flow_data.get(wtp_key, {}).get("last30days", [])

        if wtp_filter is not None:
            if wtp_filter == "" and device:   
                continue
            elif wtp_filter and wtp_filter.lower() != wtp_key:
                continue

        total_billed = sum(loc.get("qty", 0) for loc in bill_info.get("locations", []))
        billed_per_day = total_billed / days_in_month if days_in_month else 0

        # --- WTP rows (ALL) ---
        for day in range(1, days_in_month + 1):
            flow = daily_flows[day - 1] if day - 1 < len(daily_flows) else 0
            nrw_m3, nrw_pct = calculate_nrw(flow, billed_per_day)
            rows.append({
                "wtp": wtp_name.upper() if device else "",
                "area": "ALL",
                "date": f"{year}-{month:02d}-{day:02d}",
                "daily_flow": round(flow, 2),
                "billed_est": round(billed_per_day, 2),
                "nrw_m3": round(nrw_m3, 2),
                "nrw_percent": round(nrw_pct, 2),
                "billed_completed": bill_info.get("percentage_complete", 0),
                "device_code": device
            })

        # --- Per-location rows ---
        for loc in bill_info.get("locations", []):
            loc_name = loc.get("location", "Unknown")
            loc_billed = (loc.get("qty") or 0) / days_in_month if days_in_month else 0

            loc_device = get_matched_device_code(loc_name)

            if loc_device and loc_device in device_flows:
                loc_flows = device_flows[loc_device]
            else:
                loc_flows = daily_flows  

            for day in range(1, days_in_month + 1):
                flow = loc_flows[day - 1] if day - 1 < len(loc_flows) else 0
                flow = flow or 0.0
                nrw_m3, nrw_pct = calculate_nrw(flow, loc_billed)

                rows.append({
                    "wtp": wtp_name.upper() if device else "",
                    "area": loc_name,
                    "date": f"{year}-{month:02d}-{day:02d}",
                    "daily_flow": round(flow, 2),
                    "billed_est": round(loc_billed, 2),
                    "nrw_m3": round(nrw_m3, 2),
                    "nrw_percent": round(nrw_pct, 2),
                    "billed_completed": loc.get("loc_pctcomplete", 0),
                    "device_code": loc_device or device
                })

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
