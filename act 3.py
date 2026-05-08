import tkinter as tk
from tkinter import messagebox

def calculate_grade():
    try:
        number = int(entry_number.get())
        name = entry_name.get()
        course = entry_course.get()
        prelim = float(entry_prelim.get())
        midterm = float(entry_midterm.get())
        final = float(entry_final.get())

        average = (prelim * 0.20) + (midterm * 0.30) + (final * 0.50)

        if average >= 75:
            remarks = "Passed"
        else:
            remarks = "Failed"

        result_text.set(f"Student number: {number}\nStudent: {name}\nCourse: {course}\nAverage: {round(average, 2)}\nRemarks: {remarks}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for grades.")

def clear_fields():
    entry_number.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_course.delete(0, tk.END)
    entry_prelim.delete(0, tk.END)
    entry_midterm.delete(0, tk.END)
    entry_final.delete(0, tk.END)
    result_text.set("")

root = tk.Tk()
root.title("Grade Calculator")
root.geometry("520x560")
root.minsize(500, 520)
root.resizable(True, True)
root.configure(bg="#e8f2ff")

# Create a frame for inputs
frame = tk.Frame(root, padx=20, pady=20, bg="#e8f2ff")
frame.pack(expand=True, fill=tk.BOTH)
frame.grid_columnconfigure(1, weight=1)

header = tk.Label(frame, text="Grade Calculator", font=("Segoe UI", 18, "bold"), bg="#e8f2ff", fg="#1b3a75")
header.grid(row=0, column=0, columnspan=2, pady=(0, 18), sticky="ew")

label_options = {"font": ("Segoe UI", 10), "bg": "#e8f2ff", "fg": "#1b3a75"}
entry_options = {"bd": 2, "relief": "groove", "font": ("Segoe UI", 10)}

for text, row in [("Student Number:", 1), ("Student Name:", 2), ("Student Course:", 3), ("Prelim Grade:", 4), ("Midterm Grade:", 5), ("Final Grade:", 6)]:
    tk.Label(frame, text=text, **label_options).grid(row=row, column=0, sticky="e", pady=7)

entry_number = tk.Entry(frame, **entry_options)
entry_number.grid(row=1, column=1, pady=7, padx=(10, 0), sticky="ew")
entry_name = tk.Entry(frame, **entry_options)
entry_name.grid(row=2, column=1, pady=7, padx=(10, 0), sticky="ew")
entry_course = tk.Entry(frame, **entry_options)
entry_course.grid(row=3, column=1, pady=7, padx=(10, 0), sticky="ew")
entry_prelim = tk.Entry(frame, **entry_options)
entry_prelim.grid(row=4, column=1, pady=7, padx=(10, 0), sticky="ew")
entry_midterm = tk.Entry(frame, **entry_options)
entry_midterm.grid(row=5, column=1, pady=7, padx=(10, 0), sticky="ew")
entry_final = tk.Entry(frame, **entry_options)
entry_final.grid(row=6, column=1, pady=7, padx=(10, 0), sticky="ew")

calculate_button = tk.Button(frame, text="Calculate", command=calculate_grade, bg="#4c8bf5", fg="white", activebackground="#3b6cd1", relief="flat", font=("Segoe UI", 11, "bold"), padx=10, pady=8)
calculate_button.grid(row=7, column=0, columnspan=2, pady=16, sticky="ew")

clear_button = tk.Button(frame, text="Add Another Student", command=clear_fields, bg="#5ac18e", fg="white", activebackground="#4a9b78", relief="flat", font=("Segoe UI", 11, "bold"), padx=10, pady=8)
clear_button.grid(row=8, column=0, columnspan=2, pady=8, sticky="ew")

result_text = tk.StringVar()
result_label = tk.Label(frame, textvariable=result_text, justify="left", bg="#fff8c4", relief="sunken", padx=12, pady=12, anchor="w", font=("Segoe UI", 10))
result_label.grid(row=9, column=0, columnspan=2, pady=18, sticky="ew")

root.mainloop()

