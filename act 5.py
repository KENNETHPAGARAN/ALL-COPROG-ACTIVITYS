import tkinter as tk
from tkinter import ttk, messagebox
# ---------- FUNCTIONS ----------
def compute_grade():
    try:
        stud_id = entry_id.get()
        name = entry_name.get()
        course = combo_course.get()
        subject = entry_subject.get()
        prelim = float(entry_prelim.get())
        midterm = float(entry_midterm.get())
        final = float(entry_final.get())
        if not (0 <= prelim <= 100 and 0 <= midterm <= 100 and 0 <= final <=
100):
            messagebox.showerror("Error", "Grades must be between 0 and 100")
            return
        average = ((prelim*0.30)+(midterm*0.30)+(final*0.40))
        if 97 <= average <= 100:
            numerical="1.00"; remark="Excellent"
        elif 94 <= average <= 96:
            numerical="1.25"; remark="Very Good"
        elif 91 <= average <= 93:
            numerical="1.50"; remark="Very Good"
        elif 88 <= average <= 90:
            numerical="1.75"; remark="Good"
        elif 85 <= average <= 87:
            numerical="2.00"; remark="Above Average"
        elif 82 <= average <= 84:
            numerical="2.25"; remark="Above Average"
        elif 79 <= average <= 81:
            numerical="2.50"; remark="Average"
        elif 76 <= average <= 78:
            numerical="2.75"; remark="Average"
        elif average == 75:
            numerical="3.00"; remark="Passing"
        elif 72 <= average <= 74:
            numerical="3.25"; remark="Conditional"
        elif 69 <= average <= 71:
            numerical="3.50"; remark="Conditional"
        elif 66 <= average <= 68:
            numerical="3.75"; remark="Failed"
        elif average == 65:
            numerical="4.00"; remark="Failed"
        else:
            numerical="5.00"; remark="Failed"
        avg_result.config(text=f"{average:.2f}")
        num_result.config(text=numerical)
        remark_result.config(text=remark)
        # ---------- ADD RECORD TO DATASET TABLE ----------
        tree.insert("", "end", values=(
            stud_id,
            name,
            course,
            subject,
            prelim,
            midterm,
            final,
            f"{average:.2f}",
            numerical,
            remark
        ))
    except ValueError:
        messagebox.showerror("Error","Please enter valid numbers")

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
# ---------- DELETE FUNCTION ----------
def delete_record():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return
    confirm = messagebox.askyesno("Delete Record", "Are you sure you want to delete the selected record?")
    if confirm:
        tree.delete(selected_item)
# ---------- WINDOW ----------
root = tk.Tk()
root.title("Student Grading System")
root.geometry("950x650")
root.configure(bg="#00FFFF")
title = tk.Label(root,text="STUDENT GRADING SYSTEM",
font=("Arial",18,"bold"),
bg="#00FFFF",
fg="#1a3d7c")
title.pack(pady=10)
# ---------- STUDENT INFO FRAME ----------
frame_info = tk.LabelFrame(root,text="Student Information",
font=("Arial",11,"bold"),
padx=15,pady=10,
bg="#f7fbff")
frame_info.pack(fill="x",padx=20,pady=5)
tk.Label(frame_info,text="Student\nID:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
entry_id = ttk.Entry(frame_info)
entry_id.grid(row=0,column=1,pady=5)
tk.Label(frame_info,text="Student\nName:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
entry_name = ttk.Entry(frame_info)
entry_name.grid(row=1,column=1,pady=5)
tk.Label(frame_info,text="Course:",bg="#f7fbff").grid(row=2,column=0,sticky="w")
combo_course = ttk.Combobox(frame_info,
values=["BSIT","BSCS","BSBA","BSED","BSBA","BSCE","BSME","BSEE","BSCpE","BSTCM","BSES","BSMET","BSAP"],
state="readonly")
combo_course.grid(row=2,column=1,pady=5)
tk.Label(frame_info,text="Subject:",bg="#f7fbff").grid(row=3,column=0,sticky="w")
entry_subject = ttk.Entry(frame_info)
entry_subject.grid(row=3,column=1,pady=5)
# ---------- GRADES FRAME ----------
frame_grades = tk.LabelFrame(root,text="Grades Input",
font=("Arial",11,"bold"),
padx=15,pady=10,
bg="#f7fbff")
frame_grades.pack(fill="x",padx=20,pady=10)
tk.Label(frame_grades,text="Prelim:",bg="#f7fbff").grid(row=0,column=0)
entry_prelim = ttk.Entry(frame_grades,width=10)
entry_prelim.grid(row=0,column=1,padx=10)
tk.Label(frame_grades,text="Midterm:",bg="#f7fbff").grid(row=0,column=2)
entry_midterm = ttk.Entry(frame_grades,width=10)
entry_midterm.grid(row=0,column=3,padx=10)
tk.Label(frame_grades,text="Final:",bg="#f7fbff").grid(row=0,column=4)
entry_final = ttk.Entry(frame_grades,width=10)
entry_final.grid(row=0,column=5,padx=10)
# ---------- BUTTONS ----------
button_frame = tk.Frame(root,bg="#00FFFF")
button_frame.pack(pady=10)
compute_btn = tk.Button(button_frame,text="Compute",
width=15,bg="#2c7be5",fg="white",
font=("Arial",10,"bold"),
command=compute_grade)
compute_btn.grid(row=0,column=0,padx=10)
clear_btn = tk.Button(button_frame,text="Clear",
width=15,bg="#dc3545",fg="white",
font=("Arial",10,"bold"),
command=clear_fields)
clear_btn.grid(row=0,column=1,padx=10)
delete_btn = tk.Button(button_frame,text="Delete Selected",
width=15,bg="#ff8800",fg="white",
font=("Arial",10,"bold"),
command=delete_record)
delete_btn.grid(row=0,column=2,padx=10)
# ---------- RESULT FRAME ----------
frame_result = tk.LabelFrame(root,text="Result",
font=("Arial",11,"bold"),
padx=15,pady=15,
bg="#f7fbff")
frame_result.pack(fill="x",padx=20,pady=10)
tk.Label(frame_result,text="Average\nGrade:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
avg_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="blue",bg="#f7fbff")
avg_result.grid(row=0,column=1)
tk.Label(frame_result,text="Numerical\nValue:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
num_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="green",bg="#f7fbff")
num_result.grid(row=1,column=1)
tk.Label(frame_result,text="Remarks:",bg="#f7fbff").grid(row=2,column=0,sticky="w")
remark_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="red",bg="#f7fbff")
remark_result.grid(row=2,column=1)
# ---------- DATASET TABLE ----------
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
root.mainloop()

