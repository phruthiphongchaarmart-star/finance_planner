#!/usr/bin/env python3
"""
Personal Finance Planner (CLI ภาษาไทย)
- แผนงบประมาณ (50/30/20 ปรับได้)
- เป้าหมายเงินสำรองฉุกเฉิน
- จำลองการชำระหนี้ (Avalanche / Snowball)
- สรุปคำแนะนำ พร้อมบันทึกไฟล์ txt
"""

from math import ceil

def input_float(prompt, default=None):
    while True:
        try:
            s = input(prompt).strip()
            if s == "" and default is not None:
                return default
            v = float(s)
            return v
        except:
            print(" โปรดใส่ตัวเลข เช่น 25000. หากต้องการข้าม ให้กด Enter")

def currency(x):
    return f"{x:,.2f}"

def collect_expenses():
    print("\n== ระบุรายการรายจ่ายประจำต่อเดือน (ใส่ 0 ถ้าไม่มี) ==")
    expenses = {}
    while True:
        name = input(" ชื่อหมวด (หรือ Enter เพื่อเสร็จสิ้น): ").strip()
        if name == "":
            break
        amt = input_float(f"  จำนวนต่อเดือนสำหรับ '{name}': ")
        expenses[name] = amt
    return expenses

def collect_debts():
    print("\n== ระบุหนี้สิน (ถ้ามี) ==")
    debts = []
    while True:
        name = input(" ชื่อหนี้ (หรือ Enter เพื่อเสร็จสิ้น): ").strip()
        if name == "":
            break
        balance = input_float("  ยอดคงเหลือ (balance): ")
        apr = input_float("  ดอกเบี้ยต่อปี (%) เช่น 18: ")
        min_pay = input_float("  ยอดชำระขั้นต่ำต่อเดือน: ")
        debts.append({
            "name": name,
            "balance": balance,
            "apr": apr,
            "min_pay": min_pay
        })
    return debts

# --- simulate_debt_payoff() ไม่ต้องแก้ (ใช้ข้อความเป็นกลางได้) ---

def generate_plan():
    print("=== วางแผนการเงินส่วนบุคคล ===")
    income = input_float(" รายได้สุทธิ (ต่อเดือน) เช่น 30000: ")
    print("\n-- เริ่มใส่รายการรายจ่ายประจำ --")
    expenses = collect_expenses()
    essential_names = input("\nชื่อหมวดที่คุณคิดว่าเป็น 'จำเป็น' (เช่น ค่าเช่า, อาหาร) คั่นด้วย , (หรือ Enter เพื่อข้าม): ").strip()
    essential_set = {n.strip() for n in essential_names.split(",")} if essential_names else set()

    debts = collect_debts()

    # เป้าหมาย
    emergency_months = input_float("\nต้องการกองทุนฉุกเฉินกี่เดือน (ค่าเริ่มต้น 3): ", default=3)
    saving_goal_amount = input_float("ถ้ามีเป้าหมายการออม (เช่น เงินดาวน์บ้าน) ใส่จำนวน (หรือ Enter เพื่อข้าม): ", default=0.0)
    months_for_goal = input_float("อยากบรรลุเป้าหมายภายในกี่เดือน (ถ้าไม่ระบุ ให้ Enter): ", default=0.0)

    # สูตรงบประมาณ
    print("\nสูตรแบ่งงบ (ค่าเริ่มต้น 50/30/20). ต้องการปรับหรือไม่? (y/n)")
    if input().strip().lower().startswith('y'):
        need_pct = input_float(" % สำหรับรายจ่ายจำเป็น: ")
        want_pct = input_float(" % สำหรับไลฟ์สไตล์/ความสุข: ")
        save_pct = 100.0 - need_pct - want_pct
        print(f" จะออม/ลงทุน: {save_pct:.1f}%")
    else:
        need_pct, want_pct, save_pct = 50.0, 30.0, 20.0

    # คำนวณ
    total_expenses = sum(expenses.values())
    essentials = sum(v for k,v in expenses.items() if (not essential_set) or k in essential_set)
    recommended_need = income * need_pct / 100.0
    recommended_want = income * want_pct / 100.0
    recommended_save = income * save_pct / 100.0
    emergency_target = essentials * emergency_months if essentials>0 else total_expenses * emergency_months

    # --- เตรียมข้อความสรุปเป็นภาษาไทย ---
    summary_lines = []
    summary_lines.append("=== สรุปแผนการเงินส่วนบุคคล ===")
    summary_lines.append(f"รายได้ต่อเดือน: {currency(income)} บาท")
    summary_lines.append(f"รายจ่ายรวม: {currency(total_expenses)} บาท")
    summary_lines.append("รายละเอียดรายจ่าย:")
    for k,v in expenses.items():
        summary_lines.append(f"  - {k}: {currency(v)} บาท")
    summary_lines.append(f"การแบ่งงบตามสูตร {int(need_pct)}/{int(want_pct)}/{int(save_pct)}:")
    summary_lines.append(f"  - รายจ่ายจำเป็น: {currency(recommended_need)} บาท")
    summary_lines.append(f"  - ไลฟ์สไตล์/ความสุข: {currency(recommended_want)} บาท")
    summary_lines.append(f"  - ออม/ลงทุน: {currency(recommended_save)} บาท")
    summary_lines.append(f"เป้าหมายกองทุนฉุกเฉิน {int(emergency_months)} เดือน: {currency(emergency_target)} บาท")
    if saving_goal_amount > 0:
        goal_monthly = saving_goal_amount / months_for_goal if months_for_goal>0 else 0
        summary_lines.append(f"เป้าหมายการออม: {currency(saving_goal_amount)} บาท ภายใน {int(months_for_goal)} เดือน → ต้องออม {currency(goal_monthly)} บาท/เดือน")

    if debts:
        summary_lines.append("\nสรุปหนี้สิน:")
        for d in debts:
            summary_lines.append(f"  - {d['name']}: คงเหลือ {currency(d['balance'])} บาท, ดอกเบี้ย {d['apr']}%, ขั้นต่ำ {currency(d['min_pay'])} บาท")
    else:
        summary_lines.append("\nไม่มีหนี้สินที่บันทึกไว้")

    summary_lines.append("\nข้อแนะนำ:")
    summary_lines.append(" - ให้ความสำคัญกับการชำระหนี้ดอกเบี้ยสูงก่อน")
    summary_lines.append(" - เก็บกองทุนฉุกเฉิน 3-6 เดือนก่อนลงทุน")
    summary_lines.append(" - ออมหรือลงทุนสม่ำเสมอ (DCA) ในกองทุนดัชนี/ETF")
    summary_lines.append(" - ทบทวนแผนการเงินทุกเดือนและปรับตามสถานการณ์")

    print("\n\n" + "\n".join(summary_lines))

    with open("สรุปแผนการเงิน.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
    print("\nบันทึกสรุปแล้วที่ไฟล์ 'สรุปแผนการเงิน.txt'")

if __name__ == "__main__":
    generate_plan()
