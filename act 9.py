import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sys
import io
import datetime
import json
import os


ACTIVITIES_FILE = Path(__file__).parent / "activities_data.json"

activities_log = []


def load_activities():
    """Load saved activities from disk on startup."""
    global activities_log
    if ACTIVITIES_FILE.exists():
        try:
            with open(ACTIVITIES_FILE, "r", encoding="utf-8") as f:
                activities_log = json.load(f)
        except Exception:
            activities_log = []


def save_activities():
    """Persist activities log to disk."""
    try:
        with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(activities_log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Could not save activities: {e}")


# ---- Helper: Record a Save Activity ---- #
def log_activity(name, path, file_type, content):
    activities_log.append({
        "name": name,
        "path": path,
        "type": file_type,
        "time": datetime.datetime.now().strftime("%b %d, %Y  %I:%M %p"),
        "content": content,
    })
    save_activities()   # persist immediately after every save


# ---- Activities Window ---- #
def show_activities():
    act_win = tk.Toplevel(window)
    act_win.title("📂  Activities — Saved Works")
    act_win.geometry("720x520")
    act_win.configure(bg="#0f172a")
    act_win.resizable(True, True)

    act_win.update_idletasks()
    x = (act_win.winfo_screenwidth()  // 2) - 360
    y = (act_win.winfo_screenheight() // 2) - 260
    act_win.geometry(f"720x520+{x}+{y}")

    # Header
    hdr = tk.Frame(act_win, bg="#1e3a5f")
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text="📂  Activities — Saved Works",
             font=("Georgia", 13, "bold"), bg="#1e3a5f", fg="#93c5fd",
             padx=16, pady=10).pack(side=tk.LEFT)
    tk.Label(hdr, text=f"{len(activities_log)} file(s) saved",
             font=("Segoe UI", 9), bg="#1e3a5f", fg="#475569",
             padx=14).pack(side=tk.RIGHT)

    # Body: list left + preview right
    body = tk.Frame(act_win, bg="#0f172a")
    body.pack(fill=tk.BOTH, expand=True)

    # Left list
    list_frame = tk.Frame(body, bg="#0d1117", width=240)
    list_frame.pack(side=tk.LEFT, fill=tk.Y)
    list_frame.pack_propagate(False)

    tk.Label(list_frame, text="  Saved Files", font=("Segoe UI", 9, "bold"),
             bg="#1e293b", fg="#64748b", anchor="w", pady=6).pack(fill=tk.X)

    listbox = tk.Listbox(list_frame, bg="#0d1117", fg="#e2e8f0",
                         selectbackground="#1e3a5f", selectforeground="#93c5fd",
                         font=("Consolas", 10), relief=tk.FLAT, bd=0,
                         highlightthickness=0, activestyle="none")
    listbox.pack(fill=tk.BOTH, expand=True)

    ls = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
    ls.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=ls.set)

    tk.Button(list_frame, text="🗑 Delete Selected", command=lambda: delete_selected(),
              bg="#2d1515", fg="#f87171", font=("Segoe UI", 9),
              relief=tk.FLAT, cursor="hand2", padx=10, pady=8,
              activebackground="#7f1d1d", activeforeground="#ffffff", bd=0
              ).pack(fill=tk.X, padx=10, pady=(8, 10))

    # Right preview
    preview_frame = tk.Frame(body, bg="#0f172a")
    preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    info_bar = tk.Frame(preview_frame, bg="#1e293b")
    info_bar.pack(fill=tk.X)
    info_name = tk.Label(info_bar, text="  Select a file to preview",
                         font=("Georgia", 11, "bold"), bg="#1e293b", fg="#93c5fd",
                         padx=14, pady=8, anchor="w")
    info_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
    info_time = tk.Label(info_bar, text="", font=("Segoe UI", 8),
                         bg="#1e293b", fg="#475569", padx=14)
    info_time.pack(side=tk.RIGHT)

    preview_text = tk.Text(preview_frame, wrap=tk.NONE, bg="#0d1117", fg="#a3e635",
                           font=("Consolas", 11), padx=14, pady=8,
                           relief=tk.FLAT, state=tk.DISABLED)
    preview_text.pack(fill=tk.BOTH, expand=True)

    ps = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
    ps.pack(side=tk.RIGHT, fill=tk.Y)
    preview_text.config(yscrollcommand=ps.set)

    # Populate list (newest first)
    if not activities_log:
        listbox.insert(tk.END, "  No saved files yet.")
    else:
        for entry in reversed(activities_log):
            icon = "🐍" if entry["type"] == ".py" else "📄"
            listbox.insert(tk.END, f"  {icon}  {entry['name']}")

    def on_select(event):
        sel = listbox.curselection()
        if not sel:
            return
        idx = len(activities_log) - 1 - sel[0]
        if not (0 <= idx < len(activities_log)):
            return
        entry = activities_log[idx]
        info_name.config(text=f"  {entry['name']}")
        info_time.config(text=f"🕐  {entry['time']}    📁  {entry['path']}")
        preview_text.config(state=tk.NORMAL)
        preview_text.delete("1.0", tk.END)
        preview_text.insert(tk.END, entry["content"])
        preview_text.config(state=tk.DISABLED)

    listbox.bind("<<ListboxSelect>>", on_select)

    # ---- Inline rename widget (hidden until triggered) ---- #
    rename_var   = tk.StringVar()
    rename_entry = tk.Entry(list_frame, textvariable=rename_var,
                            bg="#1e3a5f", fg="#ffffff",
                            insertbackground="#38bdf8",
                            font=("Consolas", 10), relief=tk.FLAT,
                            highlightthickness=1,
                            highlightbackground="#38bdf8", bd=4)
    # (placed but not packed yet — shown on demand)

    rename_idx = [None]   # which log index is being renamed

    def start_rename():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Activities", "Please select a file first.")
            return
        if not activities_log:
            return
        list_idx   = sel[0]
        log_idx    = len(activities_log) - 1 - list_idx
        if not (0 <= log_idx < len(activities_log)):
            return
        rename_idx[0] = log_idx

        # Pre-fill with current name
        rename_var.set(activities_log[log_idx]["name"])

        # Position the Entry over the selected listbox item
        item_y = list_idx * listbox.winfo_reqheight() // max(listbox.size(), 1)
        rename_entry.place(x=0, y=item_y,
                           width=list_frame.winfo_width() - 12,
                           height=24)
        rename_entry.lift()
        rename_entry.focus_set()
        rename_entry.selection_range(0, tk.END)

    def commit_rename(event=None):
        if rename_idx[0] is None:
            return
        new_name = rename_var.get().strip()
        if new_name:
            activities_log[rename_idx[0]]["name"] = new_name
            # Refresh the listbox in place
            list_idx = len(activities_log) - 1 - rename_idx[0]
            icon = "🐍" if activities_log[rename_idx[0]]["type"] == ".py" else "📄"
            listbox.delete(list_idx)
            listbox.insert(list_idx, f"  {icon}  {new_name}")
            listbox.selection_set(list_idx)
            # Update the info bar if that file is previewed
            info_name.config(text=f"  {new_name}")
            save_activities()   # persist the rename
            statusbar.config(text=f"  ✦  Renamed to: {new_name}")
        cancel_rename()

    def cancel_rename(event=None):
        rename_idx[0] = None
        rename_entry.place_forget()
        listbox.focus_set()

    rename_entry.bind("<Return>",  commit_rename)
    rename_entry.bind("<Escape>",  cancel_rename)
    rename_entry.bind("<FocusOut>", cancel_rename)

    # Double-click on listbox also triggers rename
    def on_double_click(event):
        start_rename()
    listbox.bind("<Double-Button-1>", on_double_click)

    # Bottom action bar
    action_bar = tk.Frame(act_win, bg="#1e293b")
    action_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Activities", "Please select a file first.")
            return
        idx = len(activities_log) - 1 - sel[0]
        entry = activities_log[idx]
        text_editor.delete("1.0", tk.END)
        text_editor.insert(tk.END, entry["content"])
        statusbar.config(text=f"  ✦  Loaded from Activities: {entry['name']}")
        act_win.destroy()

    def delete_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Activities", "Please select a file first.")
            return
        idx = len(activities_log) - 1 - sel[0]
        entry = activities_log[idx]
        if messagebox.askyesno("Remove", f"Remove '{entry['name']}' from Activities?\n(This won't delete the actual file.)"):
            activities_log.pop(idx)
            save_activities()   # persist the deletion
            act_win.destroy()
            show_activities()

    tk.Button(action_bar, text="📥  Load into Editor", command=load_selected,
              bg="#1e3a5f", fg="#93c5fd", font=("Segoe UI", 10, "bold"),
              relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
              activebackground="#1d4ed8", activeforeground="#ffffff", bd=0
              ).pack(side=tk.LEFT, padx=10, pady=8)

    tk.Button(action_bar, text="✏  Rename", command=start_rename,
              bg="#1a3a2a", fg="#6ee7b7", font=("Segoe UI", 10, "bold"),
              relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
              activebackground="#065f46", activeforeground="#ffffff", bd=0
              ).pack(side=tk.LEFT, pady=8)

    tk.Button(action_bar, text="🗑  Delete Selected", command=delete_selected,
              bg="#2d1515", fg="#f87171", font=("Segoe UI", 10),
              relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
              activebackground="#7f1d1d", activeforeground="#ffffff", bd=0
              ).pack(side=tk.LEFT, padx=6, pady=8)

    tk.Button(action_bar, text="Close", command=act_win.destroy,
              bg="#1e293b", fg="#64748b", font=("Segoe UI", 10),
              relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
              activebackground="#334155", bd=0
              ).pack(side=tk.RIGHT, padx=10, pady=8)


# ---- Main Editor Window ---- #
def show_main_editor():
    global window, text_editor, statusbar

    window = tk.Tk()
    window.title("✦ Python Pull Down Menu")
    window.geometry("960x720")
    window.resizable(True, True)
    window.configure(bg="#0f172a")

    window.update_idletasks()
    x = (window.winfo_screenwidth()  // 2) - 480
    y = (window.winfo_screenheight() // 2) - 360
    window.geometry(f"960x720+{x}+{y}")

    # ---- Welcome Header ---- #
    header_frame = tk.Frame(window, bg="#1e293b")
    header_frame.pack(fill=tk.X)
    tk.Label(header_frame, text="✦ PYTHON PULL DOWN MENU ✦",
             font=("Georgia", 15, "bold"), bg="#1e293b", fg="#38bdf8", pady=10).pack()
    tk.Label(header_frame, text="Write · Run · Save  —  Your coding workspace",
             font=("Segoe UI", 9), bg="#1e293b", fg="#64748b").pack(pady=(0, 8))

    # ---- Toolbar ---- #
    toolbar = tk.Frame(window, bg="#0f172a", pady=10)
    toolbar.pack(fill=tk.X)

    btn_cfg = {
        "font": ("Georgia", 12, "bold"),
        "relief": tk.FLAT,
        "cursor": "hand2",
        "padx": 22,
        "pady": 10,
        "bd": 0,
        "width": 10,
    }

    # File button
    def file_popup(event=None):
        file_menu_popup.post(event.widget.winfo_rootx(),
                             event.widget.winfo_rooty() + event.widget.winfo_height())

    file_menu_popup = tk.Menu(window, tearoff=0, bg="#1e293b", fg="#f1f5f9",
                              activebackground="#38bdf8", activeforeground="#0f172a",
                              font=("Segoe UI", 10))
    file_menu_popup.add_command(label="  📄  New File", command=newfile)
    file_menu_popup.add_command(label="  📂  Open...", command=openfile)
    file_menu_popup.add_command(label="  💾  Save",    command=savefile)
    file_menu_popup.add_command(label="  🗂  Save All → Activities",command=save_all)
    file_menu_popup.add_separator()
    file_menu_popup.add_command(label="  🚪  Exit",    command=exitprogram)

    file_btn = tk.Button(toolbar, text="📁  File", bg="#1e3a5f", fg="#93c5fd",
                         activebackground="#1d4ed8", activeforeground="#ffffff",
                         **btn_cfg, command=lambda: None)
    file_btn.pack(side=tk.LEFT, padx=(20, 6))
    file_btn.bind("<Button-1>", file_popup)

    # Run button
    tk.Button(toolbar, text="▶  Run", bg="#064e3b", fg="#6ee7b7",
              activebackground="#059669", activeforeground="#ffffff",
              command=run_code, **btn_cfg).pack(side=tk.LEFT, padx=6)

    # Activities button
    tk.Button(toolbar, text="📂  Activities", bg="#4a1d0e", fg="#fb923c",
              activebackground="#c2410c", activeforeground="#ffffff",
              command=show_activities,
              font=("Georgia", 12, "bold"), relief=tk.FLAT,
              cursor="hand2", padx=22, pady=10, bd=0, width=12
              ).pack(side=tk.LEFT, padx=6)

    # Help button
    def help_popup(event=None):
        help_menu_popup.post(event.widget.winfo_rootx(),
                             event.widget.winfo_rooty() + event.widget.winfo_height())

    help_menu_popup = tk.Menu(window, tearoff=0, bg="#1e293b", fg="#f1f5f9",
                              activebackground="#38bdf8", activeforeground="#0f172a",
                              font=("Segoe UI", 10))
    help_menu_popup.add_command(label="  ℹ  About",     command=about)
    help_menu_popup.add_command(label="  ⌨  Shortcuts", command=show_shortcuts)

    help_btn = tk.Button(toolbar, text="❓  Help", bg="#3b1f5e", fg="#c4b5fd",
                         activebackground="#7c3aed", activeforeground="#ffffff",
                         **btn_cfg, command=lambda: None)
    help_btn.pack(side=tk.LEFT, padx=6) 
    help_btn.bind("<Button-1>", help_popup)

    def show_personal_info():
        pi = tk.Toplevel(window)
        pi.title("My Personal Info")
        pi.geometry("380x260")
        pi.configure(bg="#0f172a")
        pi.resizable(False, False)
        pi.update_idletasks()
        x = (pi.winfo_screenwidth() // 2) - 190
        y = (pi.winfo_screenheight() // 2) - 130
        pi.geometry(f"380x260+{x}+{y}")

        tk.Label(pi, text="My Personal Info", font=("Georgia", 14, "bold"),
                 bg="#0f172a", fg="#38bdf8").pack(pady=(18, 6))
        tk.Label(pi, text=(
            "Name: Kenneth Jim Elrys G. Pagaran\n"
            "Location: Indahag, Cagayan de Oro City\n"
            "Age: 17\n"
            "ID Number: 2025300218\n"
            "Current School: USTP CDO\n"
            "Course: BS Information Technology\n"
            "Gender: Male\n"
        ), font=("Segoe UI", 10), bg="#0f172a", fg="#cbd5e1",
                 justify="left").pack(padx=24, pady=8)
        tk.Button(pi, text="Close", command=pi.destroy,
                  bg="#1e293b", fg="#93c5fd", font=("Segoe UI", 10),
                  relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
                  activebackground="#334155", activeforeground="#ffffff", bd=0
                  ).pack(pady=(0, 16))

    tk.Button(toolbar, text="👤  My Personal Info", bg="#1f2d3d", fg="#a5b4fc",
              activebackground="#334155", activeforeground="#ffffff",
              command=show_personal_info,
              font=("Georgia", 12, "bold"), relief=tk.FLAT,
              cursor="hand2", padx=18, pady=10, bd=0, width=14
              ).pack(side=tk.LEFT, padx=6)

    # Logout button
    tk.Button(toolbar, text="⏻ Logout", bg="#1e293b", fg="#94a3b8",
              activebackground="#0f172a", activeforeground="#f87171",
              font=("Segoe UI", 10), relief=tk.FLAT, cursor="hand2",
              padx=12, pady=10, bd=0,
              command=lambda: [window.destroy(), start_login()]
              ).pack(side=tk.RIGHT, padx=20)

    # Divider
    tk.Frame(window, bg="#334155", height=1).pack(fill=tk.X)

    # ---- Paned Layout ---- #
    paned = tk.PanedWindow(window, orient=tk.VERTICAL, bg="#334155",
                           sashwidth=5, sashrelief=tk.FLAT, bd=0)
    paned.pack(fill=tk.BOTH, expand=True)

    # Editor pane
    editor_frame = tk.Frame(paned, bg="#0f172a")
    paned.add(editor_frame, stretch="always", minsize=150)

    line_numbers = tk.Text(editor_frame, width=4, padx=6, pady=6,
                           bg="#1e293b", fg="#475569", relief=tk.FLAT,
                           font=("Consolas", 12), state=tk.DISABLED,
                           cursor="arrow", selectbackground="#1e293b")
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    text_editor = tk.Text(editor_frame, wrap=tk.NONE, undo=True,
                          bg="#0d1117", fg="#e2e8f0",
                          insertbackground="#38bdf8",
                          selectbackground="#1e3a5f",
                          selectforeground="#93c5fd",
                          font=("Consolas", 12),
                          padx=10, pady=6, relief=tk.FLAT, tabs=("1c",))
    text_editor.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    text_editor.insert(tk.END, "# Welcome! Start typing your Python code here...\n\n")

    scroll_y = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=text_editor.yview)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    text_editor.config(yscrollcommand=scroll_y.set)

    scroll_x = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=text_editor.xview)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    text_editor.config(xscrollcommand=scroll_x.set)

    def update_line_numbers(event=None):
        lines = text_editor.get("1.0", tk.END).count("\n")
        line_numbers.config(state=tk.NORMAL)
        line_numbers.delete("1.0", tk.END)
        for i in range(1, lines + 1):
            line_numbers.insert(tk.END, f" {i}\n")
        line_numbers.config(state=tk.DISABLED)

    text_editor.bind("<KeyRelease>", update_line_numbers)
    update_line_numbers()

    # Output pane
    output_pane = tk.Frame(paned, bg="#0f172a")
    paned.add(output_pane, stretch="never", minsize=90)

    out_hdr = tk.Frame(output_pane, bg="#064e3b")
    out_hdr.pack(fill=tk.X)
    tk.Label(out_hdr, text="▶  Output Console",
             font=("Georgia", 10, "bold"), bg="#064e3b", fg="#6ee7b7",
             padx=12, pady=6).pack(side=tk.LEFT)

    def clear_output():
        output_text.config(state=tk.NORMAL)
        output_text.delete("1.0", tk.END)
        output_text.config(state=tk.DISABLED)
        statusbar.config(text="  ✦  Output cleared")

    tk.Button(out_hdr, text="🗑 Clear", command=clear_output,
              bg="#064e3b", fg="#6ee7b7", font=("Segoe UI", 9),
              relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
              activebackground="#065f46", bd=0).pack(side=tk.RIGHT, padx=8, pady=3)

    output_text = tk.Text(output_pane, wrap=tk.WORD,
                          bg="#0d1117", fg="#a3e635",
                          font=("Consolas", 11), padx=14, pady=8,
                          relief=tk.FLAT, state=tk.DISABLED)
    output_text.pack(fill=tk.BOTH, expand=True)

    out_scroll = ttk.Scrollbar(output_pane, orient=tk.VERTICAL, command=output_text.yview)
    out_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    output_text.config(yscrollcommand=out_scroll.set)

    window._output_text = output_text

    # Status bar
    status_frame = tk.Frame(window, bg="#1e293b", height=26)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    statusbar = tk.Label(status_frame, text="  ✦  Ready  |  Python Editor Pro",
                         font=("Segoe UI", 9), bg="#1e293b", fg="#64748b", anchor="w")
    statusbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
    tk.Label(status_frame, text="v3.0  ✦  ",
             font=("Segoe UI", 9), bg="#1e293b", fg="#334155").pack(side=tk.RIGHT)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",   background="#1e293b", troughcolor="#0f172a", arrowcolor="#334155", borderwidth=0)
    style.configure("Horizontal.TScrollbar", background="#1e293b", troughcolor="#0f172a", arrowcolor="#334155", borderwidth=0)

    window.bind("<Control-n>", lambda e: newfile())
    window.bind("<Control-o>", lambda e: openfile())
    window.bind("<Control-s>", lambda e: savefile())
    window.bind("<Control-S>", lambda e: save_all())
    window.bind("<Control-q>", lambda e: exitprogram())
    window.bind("<F5>",        lambda e: run_code())

    window.mainloop()


# ---- Editor Functions ---- #
def newfile():
    current_filename[0] = None
    text_editor.delete("1.0", tk.END)
    text_editor.insert(tk.END, "# Start typing your Python code here...\n")
    statusbar.config(text="  ✦  New file created")

def openfile():
    filename = filedialog.askopenfilename(
        title="Open File",
        filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        with open(filename, "r") as f:
            content = f.read()
        current_filename[0] = filename
        text_editor.delete("1.0", tk.END)
        text_editor.insert(tk.END, content)
        statusbar.config(text=f"  ✦  Opened: {Path(filename).name}")

# Tracks the current working filename across saves
current_filename = [None]  # use list so inner functions can mutate it

def savefile():
    """Save — if already named, overwrite silently. If new, ask for a name once."""
    content = text_editor.get("1.0", tk.END)
    if current_filename[0]:
        # Already has a name — just overwrite silently
        fname = current_filename[0]
        with open(fname, "w") as f:
            f.write(content)
        ext = Path(fname).suffix or ".py"
        log_activity(Path(fname).name, str(Path(fname).parent), ext, content)
        statusbar.config(text=f"  ✦  Saved: {Path(fname).name}  →  Activities ✦")
    else:
        # First time saving — ask for a name, then never ask again
        fname = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save File As"
        )
        if fname:
            current_filename[0] = fname
            with open(fname, "w") as f:
                f.write(content)
            ext = Path(fname).suffix or ".py"
            log_activity(Path(fname).name, str(Path(fname).parent), ext, content)
            statusbar.config(text=f"  ✦  Saved: {Path(fname).name}  →  Activities ✦")

def save_all():
    """Save All — instantly saves BOTH script.py and notes.txt directly to Activities, no dialog."""
    content = text_editor.get("1.0", tk.END)
    ts = datetime.datetime.now().strftime("%H%M%S")
    # Log code snapshot
    log_activity(f"script_{ts}.py", "(Activities)", ".py", content)
    # Log a notes snapshot with a header
    notes_content = f"# Notes saved on {datetime.datetime.now().strftime('%b %d, %Y %I:%M %p')}\n\n"
    log_activity(f"notes_{ts}.txt", "(Activities)", ".txt", notes_content)
    statusbar.config(text=f"  ✦  Save All → script_{ts}.py & notes_{ts}.txt added to Activities ✦")

def exitprogram():
    if messagebox.askokcancel("Exit", "Do you really want to quit?"):
        save_activities()   # make sure everything is persisted
        window.destroy()

def about():
    messagebox.showinfo("About",
                        "✦ Python Editor Pro v3.0 ✦\n\n"
                        "A professional code editor built with Tkinter.\n\n"
                        "Default login:\n  Username: admin\n  Password: admin\n\n"
                        "Features:\n"
                        "  • Inline output console\n"
                        "  • Activities — browse all saved files\n"
                        "  • Line numbers  •  Keyboard shortcuts")
    statusbar.config(text="  ✦  About dialog opened")

def show_shortcuts():
    sw = tk.Toplevel(window)
    sw.title("Keyboard Shortcuts")
    sw.geometry("320x250")
    sw.configure(bg="#0f172a")
    sw.resizable(False, False)
    tk.Label(sw, text="⌨  Keyboard Shortcuts",
             font=("Georgia", 13, "bold"), bg="#0f172a", fg="#38bdf8").pack(pady=(18, 10))
    for key, action in [
        ("Ctrl + N",       "New File"),
        ("Ctrl + O",       "Open File"),
        ("Ctrl + S",       "Save File"),
        ("Ctrl + Shift+S", "Save All"),
        ("Ctrl + Q",       "Exit"),
        ("F5",             "Run Code"),
    ]:
        row = tk.Frame(sw, bg="#1e293b")
        row.pack(fill=tk.X, padx=20, pady=2)
        tk.Label(row, text=key,    font=("Consolas", 10, "bold"),
                 bg="#1e293b", fg="#38bdf8", width=16, anchor="w", padx=8, pady=4).pack(side=tk.LEFT)
        tk.Label(row, text=action, font=("Segoe UI", 10),
                 bg="#1e293b", fg="#94a3b8", anchor="w", padx=8).pack(side=tk.LEFT)

def run_code():
    import subprocess
    import tempfile
    import threading
    import os

    code = text_editor.get("1.0", tk.END)
    out = window._output_text

    # Clear and show running indicator
    out.config(state=tk.NORMAL)
    out.delete("1.0", tk.END)
    out.config(state=tk.DISABLED)
    window.update_idletasks()
    statusbar.config(text="  ✦  Running code...")

    def execute():
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=50
            )
            stdout = proc.stdout
            stderr = proc.stderr

            def show_result():
                out.config(state=tk.NORMAL)
                out.delete("1.0", tk.END)
                if stdout:
                    out.insert(tk.END, stdout)
                if stderr:
                    out.insert(tk.END, "\n❌  Errors / Warnings:\n", "err_title")
                    out.insert(tk.END, stderr, "err_body")
                if not stdout and not stderr:
                    out.insert(tk.END, "✅  Code ran with no output.")
                out.tag_config("err_title", foreground="#f87171",
                               font=("Consolas", 11, "bold"))
                out.tag_config("err_body",  foreground="#fca5a5")
                out.config(state=tk.DISABLED)
                out.see(tk.END)
                statusbar.config(text="  ✦  Code executed successfully")
            window.after(0, show_result)

        except subprocess.TimeoutExpired:
            def show_timeout():
                out.config(state=tk.NORMAL)
                out.delete("1.0", tk.END)
                out.insert(tk.END, "⏰  Timeout: code took longer than 50 seconds.")
                out.config(state=tk.DISABLED)
                statusbar.config(text="  ✦  Execution timed out")
            window.after(0, show_timeout)

        except Exception as e:
            def show_err(err=e):
                out.config(state=tk.NORMAL)
                out.delete("1.0", tk.END)
                out.insert(tk.END, f"❌  Failed to run: {err}")
                out.config(state=tk.DISABLED)
                statusbar.config(text="  ✦  Execution failed")
            window.after(0, show_err)

        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    threading.Thread(target=execute, daemon=True).start()


# ---- Login ---- #
def start_login():
    root = tk.Tk()
    root.withdraw()

    login_win = tk.Toplevel(root)
    login_win.title("Login — pull down menu")
    login_win.geometry("420x370")
    login_win.resizable(False, False)
    login_win.configure(bg="#0f172a")
    login_win.protocol("WM_DELETE_WINDOW", root.destroy)

    login_win.update_idletasks()
    x = (login_win.winfo_screenwidth()  // 2) - 210
    y = (login_win.winfo_screenheight() // 2) - 185
    login_win.geometry(f"420x370+{x}+{y}")

    tk.Label(login_win, text="🔐", font=("Segoe UI Emoji", 38),
             bg="#0f172a", fg="#38bdf8").pack(pady=(28, 4))
    tk.Label(login_win, text="Welcome Back", font=("Georgia", 17, "bold"),
             bg="#0f172a", fg="#f1f5f9").pack()
    tk.Label(login_win, text="Sign in your account", font=("Segoe UI", 10),
             bg="#0f172a", fg="#64748b").pack(pady=(2, 16))

    # Username field
    uf = tk.Frame(login_win, bg="#1e293b", highlightthickness=1, highlightbackground="#334155")
    uf.pack(padx=40, fill=tk.X, pady=(0, 8))
    tk.Label(uf, text="👤", bg="#1e293b", fg="#38bdf8",
             font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=(10, 0))
    user_entry = tk.Entry(uf, bg="#1e293b", fg="#94a3b8",
                          insertbackground="#38bdf8", relief=tk.FLAT,
                          font=("Consolas", 12), bd=0)
    user_entry.pack(fill=tk.X, padx=6, pady=10)
    user_entry.insert(0, "Username")
    user_entry.bind("<FocusIn>", lambda e: (user_entry.delete(0, tk.END),
                                             user_entry.config(fg="#f1f5f9"))
                    if user_entry.get() == "Username" else None)

    # Password field
    pf = tk.Frame(login_win, bg="#1e293b", highlightthickness=1, highlightbackground="#334155")
    pf.pack(padx=40, fill=tk.X, pady=(0, 6))
    tk.Label(pf, text="🔑", bg="#1e293b", fg="#38bdf8",
             font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=(10, 0))
    pass_entry = tk.Entry(pf, bg="#1e293b", fg="#94a3b8",
                          insertbackground="#38bdf8", relief=tk.FLAT,
                          font=("Consolas", 12), bd=0, show="")
    pass_entry.pack(fill=tk.X, padx=6, pady=10)
    pass_entry.insert(0, "Password")

    def on_pass_focus(e):
        if pass_entry.get() == "Password":
            pass_entry.delete(0, tk.END)
            pass_entry.config(show="•", fg="#f1f5f9")
    pass_entry.bind("<FocusIn>", on_pass_focus)

    error_label = tk.Label(login_win, text="", font=("Segoe UI", 9),
                           bg="#0f172a", fg="#f87171")
    error_label.pack(pady=(2, 6))

    def attempt_login():
        u = user_entry.get()
        p = pass_entry.get()
        if u == "admin" and p in ("admin", "1234"):
            root.destroy()
            show_main_editor()
        else:
            error_label.config(text="⚠  Invalid credentials. Try  admin / admin")
            pf.config(highlightbackground="#f87171")

    tk.Button(login_win, text="Sign In →", command=attempt_login,
              bg="#0ea5e9", fg="#0f172a", font=("Georgia", 12, "bold"),
              relief=tk.FLAT, cursor="hand2", padx=20, pady=10,
              activebackground="#38bdf8", activeforeground="#0f172a", bd=0
              ).pack(padx=40, fill=tk.X)
    login_win.bind("<Return>", lambda e: attempt_login())

    root.mainloop()


# ---- Entry Point ---- #
if __name__ == "__main__":
    load_activities() 
    start_login()
