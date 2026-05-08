import tkinter as tk
from tkinter import ttk, messagebox

# ---------- LOGIN WINDOW ----------

def open_main_app():
    login_win.destroy()

    # ---------- FUNCTIONS ----------

    def compute_grade():
        try:
            prelim = float(entry_prelim.get())
            midterm = float(entry_midterm.get())
            final = float(entry_final.get())

            if not (0 <= prelim <= 100 and 0 <= midterm <= 100 and 0 <= final <= 100):
                messagebox.showerror("Error", "Grades must be between 0 and 100")
                return None, None, None

            average = round(((prelim*0.20)+(midterm*0.30)+(final*0.50)),2)

            if average >= 97:
                numerical="1.00"; remark="Excellent"
            elif average >= 94:
                numerical="1.25"; remark="Very Good"
            elif average >= 91:
                numerical="1.50"; remark="Very Good"
            elif average >= 88:
                numerical="1.75"; remark="Good"
            elif average >= 85:
                numerical="2.00"; remark="Above Average"
            elif average >= 82:
                numerical="2.25"; remark="Above Average"
            elif average >= 79:
                numerical="2.50"; remark="Average"
            elif average >= 76:
                numerical="2.75"; remark="Average"
            elif average >= 75:
                numerical="3.00"; remark="Passing"
            elif average >= 72:
                numerical="3.25"; remark="Conditional"
            elif average >= 69:
                numerical="3.50"; remark="Conditional"
            elif average >= 66:
                numerical="3.75"; remark="Failed"
            elif average >= 65:
                numerical="4.00"; remark="Failed"
            else:
                numerical="5.00"; remark="Failed"

            avg_result.config(text=f"{average:.2f}")
            num_result.config(text=numerical)
            remark_result.config(text=remark)

            return average, numerical, remark

        except ValueError:
            messagebox.showerror("Error","Please enter valid numbers")
            return None, None, None


    def add_record():
        stud_id = entry_id.get()
        name = entry_name.get()
        course = combo_course.get()
        subject = entry_subject.get()

        average, numerical, remark = compute_grade()
        if average is None:
            return

        tree.insert("", "end", values=(
            stud_id,
            name,
            course,
            subject,
            entry_prelim.get(),
            entry_midterm.get(),
            entry_final.get(),
            f"{average:.2f}",
            numerical,
            remark
        ))

        clear_fields()


    def clear_fields():
        entry_id.delete(0, tk.END)
        entry_name.delete(0, tk.END)
        entry_subject.delete(0, tk.END)
        entry_prelim.delete(0, tk.END)
        entry_midterm.delete(0, tk.END)
        entry_final.delete(0, tk.END)
        combo_course.set("")

        avg_result.config(text="")
        num_result.config(text="")
        remark_result.config(text="")


    def delete_record():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        confirm = messagebox.askyesno("Delete Record", "Are you sure you want to delete the selected record?")
        if confirm:
            tree.delete(selected_item)


    def update_record():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update.")
            return

        stud_id = entry_id.get()
        name = entry_name.get()
        course = combo_course.get()
        subject = entry_subject.get()

        average, numerical, remark = compute_grade()
        if average is None:
            return

        tree.item(selected_item, values=(
            stud_id,
            name,
            course,
            subject,
            entry_prelim.get(),
            entry_midterm.get(),
            entry_final.get(),
            f"{average:.2f}",
            numerical,
            remark
        ))

        clear_fields()


    def load_record(event):
        selected_item = tree.selection()
        if not selected_item:
            return

        values = tree.item(selected_item, "values")
        entry_id.delete(0, tk.END); entry_id.insert(0, values[0])
        entry_name.delete(0, tk.END); entry_name.insert(0, values[1])
        combo_course.set(values[2])
        entry_subject.delete(0, tk.END); entry_subject.insert(0, values[3])
        entry_prelim.delete(0, tk.END); entry_prelim.insert(0, values[4])
        entry_midterm.delete(0, tk.END); entry_midterm.insert(0, values[5])
        entry_final.delete(0, tk.END); entry_final.insert(0, values[6])

        avg_result.config(text=values[7])
        num_result.config(text=values[8])
        remark_result.config(text=values[9])


    # ---------- WINDOW ----------

    root = tk.Tk()
    root.title("Student Grading System (CRUD)")
    root.geometry("900x650")
    root.configure(bg="#00FFFF")

    title = tk.Label(root,text="STUDENT GRADING SYSTEM",
                     font=("Arial",18,"bold"),
                     bg="#00FFFF",
                     fg="#1a3d7c")
    title.pack(pady=10)

    # --- STUDENT INFO FRAME ---
    frame_info = tk.LabelFrame(root,text="Student Information",
                               font=("Arial",11,"bold"),
                               padx=15,pady=10,
                               bg="#f7fbff")
    frame_info.pack(fill="x",padx=20,pady=5)

    tk.Label(frame_info,text="Student ID:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
    entry_id = ttk.Entry(frame_info); entry_id.grid(row=0,column=1,pady=5)
    tk.Label(frame_info,text="Student Name:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
    entry_name = ttk.Entry(frame_info); entry_name.grid(row=1,column=1,pady=5)
    tk.Label(frame_info,text="Course:",bg="#f7fbff").grid(row=2,column=0,sticky="w")
    combo_course = ttk.Combobox(frame_info,
                                values=["BSIT","BSCS","BSBA","BSED","BSCE","BSME","BSEE","BSCpE","BSTCM","BSES","BSMET","BSAP"],
                                state="readonly"); combo_course.grid(row=2,column=1,pady=5)
    tk.Label(frame_info,text="Subject:",bg="#f7fbff").grid(row=3,column=0,sticky="w")
    entry_subject = ttk.Entry(frame_info); entry_subject.grid(row=3,column=1,pady=5)

    # --- GRADES FRAME ---
    frame_grades = tk.LabelFrame(root,text="Grades Input",
                                 font=("Arial",11,"bold"),
                                 padx=15,pady=10,
                                 bg="#f7fbff")
    frame_grades.pack(fill="x",padx=20,pady=10)

    tk.Label(frame_grades,text="Prelim:",bg="#f7fbff").grid(row=0,column=0)
    entry_prelim = ttk.Entry(frame_grades,width=10); entry_prelim.grid(row=0,column=1,padx=10)
    tk.Label(frame_grades,text="Midterm:",bg="#f7fbff").grid(row=0,column=2)
    entry_midterm = ttk.Entry(frame_grades,width=10); entry_midterm.grid(row=0,column=3,padx=10)
    tk.Label(frame_grades,text="Final:",bg="#f7fbff").grid(row=0,column=4)
    entry_final = ttk.Entry(frame_grades,width=10); entry_final.grid(row=0,column=5,padx=10)

    # --- BUTTONS ---
    button_frame = tk.Frame(root,bg="#00FFFF")
    button_frame.pack(pady=10)

    compute_btn = tk.Button(button_frame,text="Add / Compute",
                            width=15,bg="#2c7be5",fg="white",
                            font=("Arial",10,"bold"),
                            command=add_record)
    compute_btn.grid(row=0,column=0,padx=10)

    update_btn = tk.Button(button_frame,text="Update Selected",
                           width=15,bg="#ffc107",fg="white",
                           font=("Arial",10,"bold"),
                           command=update_record)
    update_btn.grid(row=0,column=1,padx=10)

    clear_btn = tk.Button(button_frame,text="Clear Fields",
                          width=15,bg="#dc3545",fg="white",
                          font=("Arial",10,"bold"),
                          command=clear_fields)
    clear_btn.grid(row=0,column=2,padx=10)

    delete_btn = tk.Button(button_frame,text="Delete Selected",
                           width=15,bg="#ff8800",fg="white",
                           font=("Arial",10,"bold"),
                           command=delete_record)
    delete_btn.grid(row=0,column=3,padx=10)


    # --- RESULT FRAME ---
    frame_result = tk.LabelFrame(root,text="Result",
                                 font=("Arial",11,"bold"),
                                 padx=15,pady=15,
                                 bg="#f7fbff")
    frame_result.pack(fill="x",padx=20,pady=10)

    tk.Label(frame_result,text="Average Grade:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
    avg_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="blue",bg="#f7fbff")
    avg_result.grid(row=0,column=1)

    tk.Label(frame_result,text="Numerical Value:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
    num_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="green",bg="#f7fbff")
    num_result.grid(row=1,column=1)

    tk.Label(frame_result,text="Remarks:",bg="#f7fbff").grid(row=2,column=0,sticky="w")
    remark_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="red",bg="#f7fbff")
    remark_result.grid(row=2,column=1)

    # --- DATASET TABLE ---
    frame_table = tk.LabelFrame(root,text="Student Dataset Records",
                                font=("Arial",11,"bold"),
                                bg="#f7fbff")
    frame_table.pack(fill="both",expand=True,padx=20,pady=10)

    columns = ("ID","Name","Course","Subject","Prelim","Midterm","Final","Average","Numerical","Remark")

    tree = ttk.Treeview(frame_table,columns=columns,show="headings")

    for col in columns:
        tree.heading(col,text=col)
        tree.column(col,width=90)

    tree.pack(fill="both",expand=True)

    # Bind double-click to load selected record for updating
    tree.bind("<Double-1>", load_record)

    # Run the application
    root.mainloop()


def check_login():
    # ---------- CREDENTIALS (change username/password here) ----------
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "1234"

    username = login_entry_user.get()
    password = login_entry_pass.get()

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        open_main_app()
    else:
        login_error_label.config(text="Invalid username or password.", fg="red")
        login_entry_pass.delete(0, tk.END)


# ---------- LOGIN WINDOW SETUP ----------

login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("350x250")
login_win.resizable(False, False)
login_win.configure(bg="#00FFFF")

tk.Label(login_win, text="STUDENT GRADING SYSTEM",
         font=("Arial", 13, "bold"),
         bg="#00FFFF", fg="#1a3d7c").pack(pady=(20, 5))

tk.Label(login_win, text="Please log in to continue",
         font=("Arial", 9),
         bg="#00FFFF", fg="#333333").pack(pady=(0, 15))

login_frame = tk.Frame(login_win, bg="#f7fbff", padx=20, pady=15)
login_frame.pack(padx=20, fill="x")

tk.Label(login_frame, text="Username:", bg="#f7fbff",
         font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
login_entry_user = ttk.Entry(login_frame, width=20)
login_entry_user.grid(row=0, column=1, pady=5, padx=5)
login_entry_user.focus()

tk.Label(login_frame, text="Password:", bg="#f7fbff",
         font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
login_entry_pass = ttk.Entry(login_frame, width=20, show="*")
login_entry_pass.grid(row=1, column=1, pady=5, padx=5)

# Allow pressing Enter to log in
login_entry_pass.bind("<Return>", lambda event: check_login())

login_error_label = tk.Label(login_win, text="", bg="#00FFFF",
                             font=("Arial", 9))
login_error_label.pack(pady=(5, 0))

tk.Button(login_win, text="Login",
          width=15, bg="#2c7be5", fg="white",
          font=("Arial", 10, "bold"),
          command=check_login).pack(pady=8)

login_win.mainloop()
