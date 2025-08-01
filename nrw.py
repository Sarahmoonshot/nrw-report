from flask import Flask, render_template, request, jsonify, g
from datetime import datetime, timedelta
from calendar import monthrange
from services.flowacc import run_monthly_flow_report, run_daily_and_hourly_report  
from services.qty import get_billed_qty, get_percentage_complete
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

######### app & db Setup #########
app = Flask(__name__)

DB_HOST = '209.38.56.184'
DB_PORT = 5432
DB_NAME = 'kyogojo'
DB_USER = 'admin'
DB_PASSWORD = 'password'

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

#  ORM model for NRW report
class NRWReport(Base):
    __tablename__ = 'monthly_nrw'

    id = Column(Integer, primary_key=True)
    month = Column(String, unique=True)
    total_flow = Column(Float)
    billed_qty = Column(Float)
    nrw_m3 = Column(Float)
    nrw_percent = Column(Float)
    overall_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now, onupdate=func.now())

Base.metadata.create_all(engine)

@app.before_request
def create_session():
    g.db = SessionLocal()

@app.teardown_request
def remove_session(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

######### util #########
def normalize_month_string(db_month):
    try:
        return datetime.strptime(db_month, "%B %Y").strftime("%Y-%m")
    except Exception as e:
        print(f"[DEBUG] Failed to parse DB month format: {db_month} → {e}")
        return None

######### NRW volume [%] monthly  #########
@app.route('/nrw/volume-data')
def volume_data():
    session = g.db
    records = session.query(NRWReport).order_by(NRWReport.created_at.desc()).all()

    response_data = {}

    for r in records:
        response_data[r.month] = {
            "nrw_volume": r.nrw_m3,
            "nrw_percent": r.nrw_percent,
            "billed_qty": r.billed_qty,
            "total_flows": r.total_flow
        }

    return response_data

######################
@app.route("/api/daily-flow", methods=["GET"])
def daily_flow_report():
    month_str = request.args.get("month")  # format: YYYY-MM
    if not month_str:
        return jsonify({"error": "Missing 'month' parameter (format: YYYY-MM)"}), 400

    try:
        year, month = map(int, month_str.split("-"))
        target_date = datetime(year, month, 1)
    except ValueError:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM"}), 400

    session = g.db
    flow_report = run_monthly_flow_report(month_str)
    billed_qty = get_billed_qty(year, month)
    overall_pct = get_percentage_complete(year, month)

    if not flow_report or billed_qty is None:
        return jsonify({"error": "No data available to compute NRW for this month"}), 404

    total_flow = flow_report.get("total_flow", 0)
    nrw_m3 = total_flow - billed_qty if total_flow and billed_qty else 0
    nrw_percent = (nrw_m3 / total_flow * 100) if total_flow else 0
    rounded = lambda x: round(x, 2) if isinstance(x, (float, int)) else 0

    existing = session.query(NRWReport).filter_by(month=month_str).first()

    if existing:
        # check if any field has changed
        updated = False
        if (
            existing.total_flow != rounded(total_flow) or
            existing.billed_qty != rounded(billed_qty) or
            existing.nrw_m3 != rounded(nrw_m3) or
            existing.nrw_percent != rounded(nrw_percent) or
            existing.overall_pct != round(overall_pct or 0)
        ):
            existing.total_flow = rounded(total_flow)
            existing.billed_qty = rounded(billed_qty)
            existing.nrw_m3 = rounded(nrw_m3)
            existing.nrw_percent = rounded(nrw_percent)
            existing.overall_pct = round(overall_pct or 0)
            existing.last_updated = datetime.now()
            session.commit()
            updated = True
            print(f"[DB] 🔁 Updated NRWReport for {month_str}")
        else:
            print(f"[DB] ✅ Existing record is up-to-date for {month_str}")
    else:
        # insert new record
        new_record = NRWReport(
            month=month_str,
            total_flow=rounded(total_flow),
            billed_qty=rounded(billed_qty),
            nrw_m3=rounded(nrw_m3),
            nrw_percent=rounded(nrw_percent),
            overall_pct=round(overall_pct or 0),
        )
        session.add(new_record)
        session.commit()
        existing = new_record
        print(f"[DB] ✅ Inserted new NRWReport for {month_str}")

    report = run_monthly_flow_report(month_str)
    daily_flows = report.get("daily_flows", [])
    average_daily_flow = report.get("average_daily_flow", 0)

    # daily NRW breakdown
    daily_nrws = []
    for day in daily_flows:
        day_flow = day["flow"]
        pct_of_total = day_flow / total_flow if total_flow else 0
        est_billed = billed_qty * pct_of_total
        est_nrw = day_flow - est_billed
        daily_nrws.append({
            "date": day["date"],
            "flowacc": rounded(day_flow),
            "est_billed": rounded(est_billed),
            "est_nrw": rounded(est_nrw),
            "nrw_percent": round((est_nrw / day_flow) * 100, 2) if day_flow > 0 else None
        })

    return jsonify({
        "month": month_str,
        "billed_month": month_str,
        "total_flow": rounded(total_flow),
        "average_daily_flow": rounded(average_daily_flow),
        "billed_qty": rounded(billed_qty),
        "nrw_volume": rounded(nrw_m3),
        "nrw_percent": rounded(nrw_percent),
        "is_estimate": False,
        "daily_nrws": daily_nrws
    }), 200

#########################
@app.route('/hourly')
def hourly_nrw():
    date_str = request.args.get("date")  # format: YYYY-MM-DD
    if not date_str:
        return jsonify({"error": "Missing 'date' parameter (format: YYYY-MM-DD)"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid 'date' format. Use YYYY-MM-DD"}), 400

    # gGet flowAcc data (hourly + daily) from target date
    flow_data = run_daily_and_hourly_report(date_str=date_str)
    daily_flow = flow_data.get("daily", {}).get("flow", 0)
    hourly_deltas = flow_data.get("hourly", {}).get("hourly_flows", [])

    current_month_str = target_date.strftime("%Y-%m")

    session = g.db
    billed_qty = None
    billed_month_str = None
    is_estimate = False

    # try current month first
    row = session.query(NRWReport).filter_by(month=current_month_str).first()
    if row and row.billed_qty and row.billed_qty > 0:
        billed_qty = row.billed_qty
        billed_month_str = row.month
        print(f"[DEBUG] Found billed_qty for {billed_month_str}: {billed_qty}")
    else:
        # back to previous month
        last_month = target_date.replace(day=1) - timedelta(days=1)
        fallback_month_str = last_month.strftime("%Y-%m")
        row = session.query(NRWReport).filter_by(month=fallback_month_str).first()
        if row and row.billed_qty and row.billed_qty > 0:
            billed_qty = row.billed_qty
            billed_month_str = row.month
            is_estimate = True
            print(f"[DEBUG] Using fallback billed_qty from {billed_month_str}: {billed_qty}")

    # if billing data available
    if billed_qty is None or billed_qty == 0.0:
        return jsonify({"error": "No billing data available for current or previous month"}), 404

    # estimate billed per day/hour
    num_days_in_month = monthrange(target_date.year, target_date.month)[1]
    billed_per_day = billed_qty / num_days_in_month
    billed_per_hour = billed_per_day / 24

    # daily estimates
    nrw_volume = daily_flow - billed_per_day
    nrw_percent = (nrw_volume / daily_flow * 100) if daily_flow else 0

    # hourly estimates
    hourly_estimates = []
    for entry in hourly_deltas:
        flow = entry["flow"]
        nrw = flow - billed_per_hour
        percent = (nrw / flow * 100) if flow else 0
        hourly_estimates.append({
            "hour": entry["hour"],
            "flow": round(flow, 2),
            "billed_est": round(billed_per_hour, 2),
            "nrw_percent": round(percent, 2)
        })

    return jsonify({
        "status": "ok",
        "source": f"flowAcc - billed_qty from {billed_month_str}",
        "is_estimate": is_estimate,
        "billed_month": billed_month_str,
        "billed_qty": round(billed_qty, 2),
        "daily": {
            "flowAcc": round(daily_flow, 2),
            "billed_est": round(billed_per_day, 2),
            "nrw_volume": round(nrw_volume, 2),
            "nrw_percent": round(nrw_percent, 2)
        },
        "hourly": hourly_estimates
    })

if __name__ == "__main__":
    app.run(debug=True)