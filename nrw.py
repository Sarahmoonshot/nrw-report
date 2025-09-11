from flask import Flask, jsonify, request
from datetime import datetime
from services.qty import get_billed_qty_by_project, get_billed_qty_by_year
from services.flowacc import run_flow_report, run_yearly_flow_report, DEVICE_CODES
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

######### YEARLY #########
@app.route("/nrw/yearly", methods=["GET"])
def get_yearly_nrw():
    year = request.args.get("year", type=int)
    device = request.args.get("device")

    if not year or not device:
        return jsonify({"error": "Missing 'year' or 'device' parameter"}), 400
    if device not in DEVICE_CODES.values():
        return jsonify({"message": f"Device {device} not recognized"}), 404

    results = {}

    for month in range(1, 13):
        month_str = f"{year}-{month:02d}"
        billing = get_billed_qty_by_project(year, month)
        flow = run_flow_report(device, year, month)
        flow_val = flow.get("total_flow", 0)

        entry = None

        for wtp, info in billing.items():
            if get_matched_device_code(wtp) == device:
                bill_val = sum(float(l.get("qty", 0)) for l in info["locations"])
                nrw_m3, nrw_pct = calculate_nrw(flow_val, bill_val)
                entry = {
                    wtp.upper(): {
                        "billed_completed": f"{info['percentage_complete']:.2f}%",
                        "total_flow": round(flow_val, 2),
                        "billed_qty": round(bill_val, 2),
                        "nrw_m3": round(nrw_m3, 2),
                        "nrw_percent": round(nrw_pct, 2),
                        "device_code": device,
                        "month": month_str
                    }
                }
                break

        # area
        if not entry:
            for wtp, info in billing.items():
                for loc in info["locations"]:
                    if get_matched_device_code(loc["location"]) == device:
                        bill_val = float(loc.get("qty") or 0)
                        nrw_m3, nrw_pct = calculate_nrw(flow_val, bill_val)
                        entry = {
                            loc["location"]: {
                                "billed_completed": f"{loc['loc_pctcomplete']:.2f}%",
                                "total_flow": round(flow_val, 2),
                                "billed_qty": round(bill_val, 2),
                                "nrw_m3": round(nrw_m3, 2),
                                "nrw_percent": round(nrw_pct, 2),
                                "device_code": device,
                                "month": month_str
                            }
                        }
                        break
                if entry: 
                    break

        results[month_str] = entry or {"message": f"No data found for {device} in {month_str}"}

    return jsonify(results)

######### MONTHLY #########
@app.route("/nrw/monthly", methods=["GET"]) 
def get_monthly_nrw():
    month_str = request.args.get("month")
    device = request.args.get("device")

    if not month_str or not device:
        return jsonify({"error": "Missing 'month' or 'device' parameter"}), 400

    try:
        year, month = map(int, month_str.split("-"))
    except ValueError:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM"}), 400

    if device not in DEVICE_CODES.values():
        return jsonify({"message": f"Device {device} not recognized"}), 404

    billing = get_billed_qty_by_project(year, month)
    flow = run_flow_report(device, year, month) 

    def build_response(name, flow_val, bill_val, billed_pct, device_code):
        nrw_m3, nrw_pct = calculate_nrw(flow_val, bill_val)
        if flow_val == 0 and bill_val == 0:
            return None
        return {
            name: {
                "billed_completed": f"{billed_pct:.2f}%",
                "total_flow": round(flow_val, 2),
                "billed_qty": round(bill_val, 2),
                "nrw_m3": round(nrw_m3, 2),
                "nrw_percent": round(nrw_pct, 2),
                "device_code": device_code
            }
        }

    # WTP 
    for wtp, info in billing.items():
        if get_matched_device_code(wtp) == device:
            wtp_key = wtp.replace(" WTP", "").lower()
            total_flow = flow.get("total_flow", 0)
            total_bill = sum(float(l.get("qty", 0)) for l in info.get("locations", []))
            result = build_response(
                wtp.upper(), total_flow, total_bill,
                info.get("percentage_complete", 0), device
            )
            return jsonify(result or {"message": f"No data found for device {device} in {month_str}"})

    # Area 
    for wtp, info in billing.items():
        for loc in info.get("locations", []):
            if get_matched_device_code(loc.get("location")) == device:
                name = loc.get("location", "Unknown")
                flow_val = flow.get("total_flow", 0)  
                bill_val = float(loc.get("qty", 0))
                result = build_response(
                    name, flow_val, bill_val,
                    loc.get("loc_pctcomplete", 0), device
                )
                return jsonify(result or {"message": f"No data found for device {device} in {month_str}"})

    return jsonify({"message": f"No data found for device {device} in {month_str}"})

######### DAILY  #########
@app.route("/nrw/daily", methods=["GET"])
def get_daily_nrw():
    date_str = request.args.get("month")
    device = request.args.get("device")

    if not date_str or not device:
        return jsonify({"error": "Missing 'date' or 'device' parameter"}), 400

    try:
        fmt = "%Y-%m" if len(date_str) == 7 else "%Y-%m-%d"
        req_date = datetime.strptime(date_str, fmt).date()
    except ValueError:
        return jsonify({"error": "Invalid 'date'. Use YYYY-MM or YYYY-MM-DD"}), 400

    year, month = req_date.year, req_date.month
    next_month = datetime(year + (month == 12), (month % 12) + 1, 1)
    days_in_month = (next_month - datetime(year, month, 1)).days

    flow = run_flow_report(device, year, month)  
    daily_flows = flow.get("last30days", [])

    billing = get_billed_qty_by_project(year, month)

    def build_rows(name, billed_total, daily_flows, billed_pct, device_code):
        billed_per_day = billed_total / days_in_month if days_in_month else 0
        rows = []
        for day in range(1, days_in_month + 1):
            flow_val = daily_flows[day - 1] if day - 1 < len(daily_flows) else 0
            flow_val = flow_val or 0.0
            nrw_m3, nrw_pct = calculate_nrw(flow_val, billed_per_day)
            rows.append({
                name: {
                    "date": f"{year}-{month:02d}-{day:02d}",
                    "daily_flow": round(flow_val, 2),
                    "billed_est": round(billed_per_day, 2),
                    "nrw_m3": round(nrw_m3, 2),
                    "nrw_percent": round(nrw_pct, 2),
                    "billed_completed": billed_pct,
                    "device_code": device_code
                }
            })
        return rows

    # --- Match billing side ---
    for wtp, info in billing.items():
        if get_matched_device_code(wtp) == device:
            billed_total = sum(float(l.get("qty", 0)) for l in info.get("locations", []))
            rows = build_rows(wtp.upper(), billed_total, daily_flows, info.get("percentage_complete", 0), device)
            return jsonify(rows)

        for loc in info.get("locations", []):
            if get_matched_device_code(loc.get("location")) == device:
                name = loc.get("location", "Unknown")
                billed_total = float(loc.get("qty") or 0)
                rows = build_rows(name, billed_total, daily_flows, loc.get("loc_pctcomplete", 0), device)
                return jsonify(rows)

    return jsonify({"message": f"No data found for device {device} in {date_str}"})

if __name__ == "__main__":
    app.run(debug=True)
