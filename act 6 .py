from tkinter import *
from tkinter import ttk
import sqlite3
import tkinter.messagebox as tkMessageBox

root = Tk()
root.title("Student Information")
root.configure(bg="#2c3e50")

width = 900
height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)

# ================= DATABASE FIXED =================
def Database():
    global conn, cursor
    conn = sqlite3.connect("pythontut.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member (
            mem_id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            gender TEXT,
            address TEXT,
            province TEXT,
            username TEXT,
            password TEXT
        )
    """)

# ================= CREATE =================
def Create():
    if "" in (FIRSTNAME.get(), LASTNAME.get(), GENDER.get(),
              ADDRESS.get(), PROVINCE.get(), USERNAME.get(), PASSWORD.get()):
        txt_result.config(text="Please complete all fields!", fg="red")
        return

    Database()
    cursor.execute("""
        INSERT INTO member (firstname, lastname, gender, address, province, username, password)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        FIRSTNAME.get(), LASTNAME.get(), GENDER.get(),
        ADDRESS.get(), PROVINCE.get(), USERNAME.get(), PASSWORD.get()
    ))
    conn.commit()
    conn.close()

    txt_result.config(text="Data Created Successfully!", fg="green")

    # refresh table after create
    Read()

# ================= READ =================
def Read():
    tree.delete(*tree.get_children())
    Database()
    cursor.execute("SELECT * FROM member ORDER BY lastname ASC")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", END, values=row[1:8])

# ================= UPDATE =================
def Update():
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, 'values')

    Database()
    cursor.execute("""
        UPDATE member SET firstname=?, lastname=?, gender=?, address=?, province=?, username=?, password=?
        WHERE firstname=? AND lastname=?
    """, (
        FIRSTNAME.get(), LASTNAME.get(), GENDER.get(),
        ADDRESS.get(), PROVINCE.get(),
        USERNAME.get(), PASSWORD.get(),
        values[0], values[1]
    ))
    conn.commit()
    conn.close()

    txt_result.config(text="Updated Successfully!", fg="blue")
    Read()

# ================= DELETE =================
def Delete():
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, 'values')

    Database()
    cursor.execute("DELETE FROM member WHERE firstname=? AND lastname=?", (values[0], values[1]))
    conn.commit()
    conn.close()

    txt_result.config(text="Deleted Successfully!", fg="red")
    Read()

# ================= SELECT =================
def OnSelected(event):
    selected = tree.focus()
    values = tree.item(selected, 'values')

    FIRSTNAME.set(values[0])
    LASTNAME.set(values[1])
    GENDER.set(values[2])
    ADDRESS.set(values[3])
    PROVINCE.set(values[4])
    USERNAME.set(values[5])
    PASSWORD.set(values[6])

# ================= EXIT =================
def Exit():
    result = tkMessageBox.askquestion("Exit", "Are you sure?")
    if result == "yes":
        root.destroy()

# ================= VARIABLES =================
FIRSTNAME = StringVar()
LASTNAME = StringVar()
GENDER = StringVar()
ADDRESS = StringVar()
PROVINCE = StringVar()
USERNAME = StringVar()
PASSWORD = StringVar()

# ================= UI =================
Top = Frame(root, bg="#34495e", height=50)
Top.pack(fill=X)

Label(Top, text="Student CRUD System", font=("Arial", 20, "bold"),
      bg="#34495e", fg="white").pack()

Left = Frame(root, bg="#ecf0f1", width=300)
Left.pack(side=LEFT, fill=Y)

Right = Frame(root, bg="#bdc3c7")
Right.pack(side=RIGHT, expand=1, fill=BOTH)

Forms = Frame(Left, bg="#ecf0f1")
Forms.pack(pady=10)

Buttons = Frame(Left, bg="#ecf0f1")
Buttons.pack(pady=10)

# ================= INPUTS =================
Label(Forms, text="Firstname", bg="#ecf0f1").grid(row=0, column=0)
Entry(Forms, textvariable=FIRSTNAME).grid(row=0, column=1)

Label(Forms, text="Lastname", bg="#ecf0f1").grid(row=1, column=0)
Entry(Forms, textvariable=LASTNAME).grid(row=1, column=1)

Label(Forms, text="Gender", bg="#ecf0f1").grid(row=2, column=0)
FrameGender = Frame(Forms, bg="#ecf0f1")
FrameGender.grid(row=2, column=1)
Radiobutton(FrameGender, text="Male", variable=GENDER, value="Male").pack(side=LEFT)
Radiobutton(FrameGender, text="Female", variable=GENDER, value="Female").pack(side=LEFT)

Label(Forms, text="Address", bg="#ecf0f1").grid(row=3, column=0)
Entry(Forms, textvariable=ADDRESS).grid(row=3, column=1)

Label(Forms, text="Province", bg="#ecf0f1").grid(row=4, column=0)
province_combo = ttk.Combobox(Forms, textvariable=PROVINCE, state="readonly")
province_combo['values'] = (
    "Bukidnon", "Camiguin", "Lanao del Norte", "Misamis Oriental",
    "Misamis Occidental", "Davao del Sur", "Davao del Norte",
    "Zamboanga del Sur", "Zamboanga del Norte",
    "South Cotabato", "Sultan Kudarat",
    "Agusan del Norte", "Agusan del Sur",
    "Surigao del Norte", "Surigao del Sur"
)
province_combo.grid(row=4, column=1)

Label(Forms, text="Username", bg="#ecf0f1").grid(row=5, column=0)
Entry(Forms, textvariable=USERNAME).grid(row=5, column=1)

Label(Forms, text="Password", bg="#ecf0f1").grid(row=6, column=0)
Entry(Forms, textvariable=PASSWORD, show="*").grid(row=6, column=1)

txt_result = Label(Buttons, bg="#ecf0f1")
txt_result.pack()

# ================= BUTTONS =================
Button(Buttons, text="Create", bg="#2ecc71", fg="white", command=Create, width=12).pack(pady=2)
Button(Buttons, text="Read", bg="#3498db", fg="white", command=Read, width=12).pack(pady=2)
Button(Buttons, text="Update", bg="#f1c40f", fg="black", command=Update, width=12).pack(pady=2)
Button(Buttons, text="Delete", bg="#e74c3c", fg="white", command=Delete, width=12).pack(pady=2)
Button(Buttons, text="Exit", bg="#34495e", fg="white", command=Exit, width=12).pack(pady=2)

# ================= TABLE =================
scrollbarx = Scrollbar(Right, orient=HORIZONTAL)
scrollbary = Scrollbar(Right, orient=VERTICAL)

tree = ttk.Treeview(Right,
    columns=("Firstname", "Lastname", "Gender", "Address", "Province", "Username", "Password"),
    xscrollcommand=scrollbarx.set,
    yscrollcommand=scrollbary.set
)

scrollbarx.pack(side=BOTTOM, fill=X)
scrollbary.pack(side=RIGHT, fill=Y)

scrollbarx.config(command=tree.xview)
scrollbary.config(command=tree.yview)

tree.heading("Firstname", text="Firstname")
tree.heading("Lastname", text="Lastname")
tree.heading("Gender", text="Gender")
tree.heading("Address", text="Address")
tree.heading("Province", text="Province")
tree.heading("Username", text="Username")
tree.heading("Password", text="Password")

tree.pack(fill=BOTH, expand=1)
tree.bind("<Double-1>", OnSelected)

Read()
root.mainloop()
