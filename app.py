#!/usr/bin/env python3
from flask import Flask, render_template, request, send_file # type: ignore
import pandas as pd # type: ignore
import io

app = Flask(__name__)

def currency(x):
    return f"{x:,.2f}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # รับข้อมูลจากฟอร์ม
        income = float(request.form.get("income", 0))
        emergency_months = float(request.form.get("emergency_months", 3))
        need_pct = float(request.form.get("need_pct", 50))
        want_pct = float(request.form.get("want_pct", 30))
        save_pct = 100 - need_pct - want_pct

        expenses_names = request.form.getlist("expense_name")
        expenses_values = request.form.getlist("expense_value")
        expenses = {n: float(v or 0) for n,v in zip(expenses_names, expenses_values) if n}

        # คำนวณ
        total_expenses = sum(expenses.values())
        recommended_need = income * need_pct / 100
        recommended_want = income * want_pct / 100
        recommended_save = income * save_pct / 100
        essentials = total_expenses
        emergency_target = essentials * emergency_months

        # สรุป
        summary = {
            "income": income,
            "total_expenses": total_expenses,
            "expenses": expenses,
            "need": recommended_need,
            "want": recommended_want,
            "save": recommended_save,
            "emergency_target": emergency_target,
            "ratio": (need_pct, want_pct, save_pct),
        }

        # เก็บใน session หรือ pass context
        return render_template("summary.html", summary=summary, currency=currency)

    return render_template("index.html")

@app.route("/download_txt", methods=["POST"])
def download_txt():
    data = request.form.to_dict(flat=False)
    buffer = io.StringIO()
    buffer.write("=== สรุปแผนการเงินส่วนบุคคล ===\n")
    buffer.write(f"รายได้ต่อเดือน: {currency(float(data['income'][0]))} บาท\n")
    buffer.write(f"รายจ่ายรวม: {currency(float(data['total_expenses'][0]))} บาท\n")
    return send_file(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        as_attachment=True,
        download_name="สรุปแผนการเงิน.txt",
        mimetype="text/plain"
    )

@app.route("/download_csv", methods=["POST"])
def download_csv():
    data = request.form.to_dict(flat=False)
    expenses = eval(data["expenses"][0])
    df = pd.DataFrame(list(expenses.items()), columns=["หมวดค่าใช้จ่าย", "จำนวนเงิน"])
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="expenses.csv", mimetype="text/csv")

@app.route("/download_excel", methods=["POST"])
def download_excel():
    data = request.form.to_dict(flat=False)
    expenses = eval(data["expenses"][0])
    df = pd.DataFrame(list(expenses.items()), columns=["หมวดค่าใช้จ่าย", "จำนวนเงิน"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Expenses")
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="expenses.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
