import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
# ===== LOGIN WINDOW =====
login = tk.Tk()
login.title("Login")
login.geometry("300x200")
tk.Label(login, text="Username").pack(pady=5)
user_entry = tk.Entry(login)
user_entry.pack()
tk.Label(login, text="Password").pack(pady=5)
pass_entry = tk.Entry(login, show="*")
pass_entry.pack()
def check_login():
    if user_entry.get() == "admin" and pass_entry.get() == "1234":
        login.destroy()
    else:
        messagebox.showerror("Error", "Invalid Username or Password")
tk.Button(login, text="Login", command=check_login).pack(pady=10)
login.mainloop()
# ===== DATABASE =====
conn = sqlite3.connect("payroll.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll (
emp_no TEXT,
name TEXT,
gender TEXT,
position TEXT,
rate REAL,
days REAL,
sss REAL,
philhealth REAL,
cash REAL,
gross REAL,
deductions REAL,
net REAL
)
""")
try:
    cursor.execute("ALTER TABLE payroll ADD COLUMN sss REAL")
except:
    pass
try:
    cursor.execute("ALTER TABLE payroll ADD COLUMN philhealth REAL")
except:
    pass
try:
    cursor.execute("ALTER TABLE payroll ADD COLUMN cash REAL")
except:
    pass
conn.commit()
# ===== FUNCTIONS =====
def compute_pay():
    try:
        rate = float(rate_entry.get())
        days = float(days_entry.get())
        sss = float(sss_entry.get())
        philhealth = float(philhealth_entry.get())
        cash_adv = float(cash_entry.get())
        gross_pay = rate * days
        total_deductions = sss + philhealth + cash_adv
        net_pay = gross_pay - total_deductions
        gross_var.set(f"{gross_pay:.2f}")
        deduct_var.set(f"{total_deductions:.2f}")
        net_var.set(f"{net_pay:.2f}")
        save_to_db(gross_pay, total_deductions, net_pay)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers!")
def save_to_db(gross, deductions, net):
    cursor.execute("""
INSERT INTO payroll (
emp_no, name, gender, position,
rate, days,
gross,
sss, philhealth, cash,
deductions, net
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
""", (
emp_no_entry.get(),
name_entry.get(),
gender_var.get(),
position_cb.get(),
float(rate_entry.get()),
float(days_entry.get()),
gross,
float(sss_entry.get()),
float(philhealth_entry.get()),
float(cash_entry.get()),
deductions,
net
))
    conn.commit()
    load_data()
    messagebox.showinfo("Saved", "Record saved!")
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("""
SELECT emp_no, name, gender, position,
rate, days,
gross,
sss, philhealth, cash,
deductions, net
FROM payroll
""")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)
def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Please select a record to delete!")
        return
    confirm = messagebox.askyesno("Delete", "Are you sure you want to delete?")
    if not confirm:
        return
    for item in selected:
        values = tree.item(item, "values")
        cursor.execute("""
DELETE FROM payroll
WHERE emp_no=? AND name=? AND gross=? AND net=?
""", (values[0], values[1], values[6], values[11]))
        tree.delete(item)
    conn.commit()
    messagebox.showinfo("Deleted", "Record deleted successfully!")
def clear_fields():
    for entry in [emp_no_entry, name_entry, rate_entry, days_entry,
sss_entry, philhealth_entry, cash_entry]:
        entry.delete(0, tk.END)
    gross_var.set("")
    deduct_var.set("")
    net_var.set("")
    gender_var.set("")
    position_cb.set("")
def exit_app():
    if messagebox.askyesno("Exit", "Do you want to exit?"):
        root.destroy()
# ===== WINDOW =====
root = tk.Tk()
root.title("Payroll System")
root.geometry("500x700")
root.configure(bg="#08b2dd")
title = tk.Label(root, text="PAYROLL SYSTEM", font=("Arial", 15, "bold"),
bg="#f4f6f7")
title.pack(pady=10)
# ===== EMPLOYEE FRAME =====
emp_frame = tk.LabelFrame(root, text="Employee Information", padx=10, pady=10)
emp_frame.pack(padx=15, pady=5, fill="both")
tk.Label(emp_frame, text="Employee No:").grid(row=0, column=0, sticky="w")
emp_no_entry = tk.Entry(emp_frame, width=25)
emp_no_entry.grid(row=0, column=1, pady=3)
tk.Label(emp_frame, text="Employee Name:").grid(row=1, column=0, sticky="w")
name_entry = tk.Entry(emp_frame, width=25)
name_entry.grid(row=1, column=1, pady=3)
tk.Label(emp_frame, text="Gender:").grid(row=2, column=0, sticky="w")
gender_var = tk.StringVar()
tk.Radiobutton(emp_frame, text="Male", variable=gender_var, value="Male").grid(row=2, column=1, sticky="w")
tk.Radiobutton(emp_frame, text="Female", variable=gender_var, value="Female").grid(row=2, column=1,
sticky="e")
tk.Label(emp_frame, text="Position:").grid(row=3, column=0, sticky="w")
position_cb = ttk.Combobox(emp_frame, width=22)
position_cb['values'] = ("Cashier", "Bagger", "Manager", "Janitor", "Guard")
position_cb.grid(row=3, column=1, pady=3)
tk.Label(emp_frame, text="Rate per Day:").grid(row=4, column=0, sticky="w")
rate_entry = tk.Entry(emp_frame, width=25)
rate_entry.grid(row=4, column=1, pady=3)
tk.Label(emp_frame, text="Days Worked:").grid(row=5, column=0, sticky="w")
days_entry = tk.Entry(emp_frame, width=25)
days_entry.grid(row=5, column=1, pady=3)
# ===== DEDUCTIONS =====
ded_frame = tk.LabelFrame(root, text="Deductions", padx=10, pady=10)
ded_frame.pack(padx=15, pady=5, fill="both")
tk.Label(ded_frame, text="SSS:").grid(row=0, column=0, sticky="w")
sss_entry = tk.Entry(ded_frame, width=25)
sss_entry.grid(row=0, column=1, pady=3)
tk.Label(ded_frame, text="PhilHealth:").grid(row=1, column=0, sticky="w")
philhealth_entry = tk.Entry(ded_frame, width=25)
philhealth_entry.grid(row=1, column=1, pady=3)
tk.Label(ded_frame, text="Cash Advance:").grid(row=2, column=0, sticky="w")
cash_entry = tk.Entry(ded_frame, width=25)
cash_entry.grid(row=2, column=1, pady=3)
# ===== RESULTS =====
result_frame = tk.LabelFrame(root, text="Payroll Summary", padx=10, pady=10)
result_frame.pack(padx=15, pady=5, fill="both")
gross_var = tk.StringVar()
deduct_var = tk.StringVar()
net_var = tk.StringVar()
tk.Label(result_frame, text="Gross Pay:").grid(row=0, column=0, sticky="w")
tk.Entry(result_frame, textvariable=gross_var, state="readonly", width=25).grid(row=0, column=1, pady=3)
tk.Label(result_frame, text="Total Deductions:").grid(row=1, column=0, sticky="w")
tk.Entry(result_frame, textvariable=deduct_var, state="readonly", width=25).grid(row=1, column=1, pady=3)
tk.Label(result_frame, text="Net Pay:").grid(row=2, column=0, sticky="w")
tk.Entry(result_frame, textvariable=net_var, state="readonly", width=25).grid(row=2, column=1, pady=3)
# ===== TABLE =====
table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=10, fill="both", expand=True)
columns = ("EMP_NO", "NAME", "GENDER", "POSITION",
"RATE", "DAYS",
"GROSSPAY",
"SSS", "PHILHEALTH", "CASH_ADVANCE",
"DEDUCTION", "NET_PAY")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=90)
tree.pack(fill="both", expand=True)
# ===== BUTTONS =====
btn_frame = tk.Frame(root, bg="#f4f6f7")
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Compute", width=10, bg="#2ecc71",
fg="white", command=compute_pay).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Clear", width=10, bg="#fa9c04",
fg="white", command=clear_fields).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Exit", width=10, bg="#e74c3c",
fg="white", command=exit_app).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Delete", width=10, bg="#c0392b",
fg="white", command=delete_data).grid(row=0, column=3, padx=5)
load_data()
root.mainloop()
