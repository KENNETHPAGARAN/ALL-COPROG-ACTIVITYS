import tkinter as tk
from tkinter import messagebox

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


    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers!")

def clear_fields():
    for entry in [emp_no_entry, name_entry, rate_entry, days_entry,
                  sss_entry, philhealth_entry, cash_entry]:
        entry.delete(0, tk.END)

    gross_var.set("")
    deduct_var.set("")
    net_var.set("")

def exit_app():
    if messagebox.askyesno("Exit", "Do you want to exit?"):
        root.destroy()

# Window
root = tk.Tk()
root.title("Payroll System")
root.geometry("420x520")
root.configure(bg="#f4f6f7")

title = tk.Label(root, text="PAYROLL SYSTEM", font=("Arial", 16, "bold"),
                 bg="#f4f6f7")
title.pack(pady=10)

# ===== Employee Frame =====
emp_frame = tk.LabelFrame(root, text="Employee Information", padx=10, pady=10)
emp_frame.pack(padx=15, pady=5, fill="both")

tk.Label(emp_frame, text="Employee No:").grid(row=0, column=0, sticky="w")
emp_no_entry = tk.Entry(emp_frame, width=25)
emp_no_entry.grid(row=0, column=1, pady=3)

tk.Label(emp_frame, text="Employee Name:").grid(row=1, column=0, sticky="w")
name_entry = tk.Entry(emp_frame, width=25)
name_entry.grid(row=1, column=1, pady=3)

tk.Label(emp_frame, text="Rate per Day:").grid(row=2, column=0, sticky="w")
rate_entry = tk.Entry(emp_frame, width=25)
rate_entry.grid(row=2, column=1, pady=3)

tk.Label(emp_frame, text="Days Worked:").grid(row=3, column=0, sticky="w")
days_entry = tk.Entry(emp_frame, width=25)
days_entry.grid(row=3, column=1, pady=3)

# ===== Deductions Frame =====
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

# ===== Results Frame =====
result_frame = tk.LabelFrame(root, text="Payroll Summary", padx=10, pady=10)
result_frame.pack(padx=15, pady=5, fill="both")

gross_var = tk.StringVar()
deduct_var = tk.StringVar()
net_var = tk.StringVar()

tk.Label(result_frame, text="Gross Pay:").grid(row=0, column=0, sticky="w")
tk.Entry(result_frame, textvariable=gross_var, state="readonly", width=25)\
    .grid(row=0, column=1, pady=3)

tk.Label(result_frame, text="Total Deductions:").grid(row=1, column=0, sticky="w")
tk.Entry(result_frame, textvariable=deduct_var, state="readonly", width=25)\
    .grid(row=1, column=1, pady=3)

tk.Label(result_frame, text="Net Pay:").grid(row=2, column=0, sticky="w")
tk.Entry(result_frame, textvariable=net_var, state="readonly", width=25)\
    .grid(row=2, column=1, pady=3)

# ===== Buttons =====
btn_frame = tk.Frame(root, bg="#f4f6f7")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Compute", width=10, bg="#2ecc71",
          fg="white", command=compute_pay).grid(row=0, column=0, padx=5)

tk.Button(btn_frame, text="Clear", width=10, bg="#fa9c04",
          fg="white", command=clear_fields).grid(row=0, column=1, padx=5)

tk.Button(btn_frame, text="Exit", width=10, bg="#e74c3c",
          fg="white", command=exit_app).grid(row=0, column=2, padx=5)

root.mainloop()


