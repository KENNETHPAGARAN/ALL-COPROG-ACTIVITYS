import tkinter as tk

student_id = "2025300218"
student_name = "KENNETH JIM ELRYS G.PAGARAN"
course = "BS Information technology"
year_level = "1st year"

root = tk.Tk()
root.title("Student Information")

tk.Label(root, text="STUDENT INFORMATION", font=("Arial", 16, "bold")).pack(pady=10)
tk.Label(root, text="-------------------").pack()

tk.Label(root, text=f"Student ID: {student_id}").pack(anchor="w", padx=20)
tk.Label(root, text=f"Name: {student_name}").pack(anchor="w", padx=20)
tk.Label(root, text=f"Course: {course}").pack(anchor="w", padx=20)
tk.Label(root, text=f"Year Level: {year_level}").pack(anchor="w", padx=20)

root.mainloop()
