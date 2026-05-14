import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sys
import datetime
import json


# Use AppData for persistent cross-device storage
ACTIVITIES_DIR = Path.home() / "AppData" / "Local" / "PythonEditorPro"
ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
ACTIVITIES_FILE = ACTIVITIES_DIR / "activities_data.json"

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
    """Persist activities log to disk permanently."""
    try:
        ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
        with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(activities_log, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


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

    def on_select(event):  # noqa: ARG001
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

    def commit_rename(event=None):  # noqa: ARG001
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

    def cancel_rename(event=None):  # noqa: ARG001
        rename_idx[0] = None
        rename_entry.place_forget()
        listbox.focus_set()

    rename_entry.bind("<Return>",  commit_rename)
    rename_entry.bind("<Escape>",  cancel_rename)
    rename_entry.bind("<FocusOut>", cancel_rename)

    # Double-click on listbox also triggers rename
    def on_double_click(event):  # noqa: ARG001
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
        if event is None:
            return
        w = event.widget  # type: ignore[attr-defined]
        file_menu_popup.post(w.winfo_rootx(), w.winfo_rooty() + w.winfo_height())

    file_menu_popup = tk.Menu(window, tearoff=0, bg="#1e293b", fg="#f1f5f9",
                              activebackground="#38bdf8", activeforeground="#0f172a",
                              font=("Segoe UI", 10))
    file_menu_popup.add_command(label="  📄  New File", command=newfile)
    file_menu_popup.add_command(label="  📂  Open...", command=openfile)
    file_menu_popup.add_command(label="  💾  Save",    command=savefile)
    file_menu_popup.add_command(label="  🗂  Save All → Activities", command=save_all)
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

    # ---- Activities pull-down button ---- #
    def activities_popup(event=None):
        # Rebuild menu each time so it reflects the latest activities_log
        activities_menu_popup.delete(0, tk.END)
        activities_menu_popup.add_command(
            label="  📂  Browse All Activities...",
            command=show_activities
        )
        activities_menu_popup.add_separator()
        if not activities_log:
            activities_menu_popup.add_command(label="  (No saved files yet)", state=tk.DISABLED)
        else:
            # Separate into midterm (activities 1-5), final (activities 6-8), and other
            midterm_names = {
                "activity_1_student_info.py",
                "activity_2_receipt_generator.py",
                "activity_3_grade_calculator.py",
                "activity_4_payroll_system.py",
                "activity_5_grading_system.py",
            }
            final_names = {
                "Activity_6_student_crud.py",
                "activity_7_payroll_with_login.py",
                "activity_8_grading_crud_login.py",
            }

            midterm_entries = [e for e in activities_log if e["name"] in midterm_names]
            final_entries   = [e for e in activities_log if e["name"] in final_names]
            other_entries   = [e for e in activities_log
                               if e["name"] not in midterm_names and e["name"] not in final_names]

            def make_loader(e):
                def load_entry():
                    text_editor.delete("1.0", tk.END)
                    text_editor.insert(tk.END, e["content"])
                    statusbar.config(text=f"  ✦  Loaded from Activities: {e['name']}")
                return load_entry

            # ── Midterm Activities ──
            activities_menu_popup.add_command(
                label="  ── MIDTERM ACTIVITIES ──",
                state=tk.DISABLED
            )
            if midterm_entries:
                for entry in midterm_entries:
                    icon = "🐍" if entry["type"] == ".py" else "📄"
                    activities_menu_popup.add_command(
                        label=f"  {icon}  {entry['name']}   🕐 {entry['time']}",
                        command=make_loader(entry)
                    )
            else:
                activities_menu_popup.add_command(label="    (none saved yet)", state=tk.DISABLED)

            activities_menu_popup.add_separator()

            # ── Final Activities ──
            activities_menu_popup.add_command(
                label="  ── FINAL ACTIVITIES ──",
                state=tk.DISABLED
            )
            if final_entries:
                for entry in final_entries:
                    icon = "🐍" if entry["type"] == ".py" else "📄"
                    activities_menu_popup.add_command(
                        label=f"  {icon}  {entry['name']}   🕐 {entry['time']}",
                        command=make_loader(entry)
                    )
            else:
                activities_menu_popup.add_command(label="    (none saved yet)", state=tk.DISABLED)

            # ── Other saved files (user-created) ──
            if other_entries:
                activities_menu_popup.add_separator()
                activities_menu_popup.add_command(
                    label="  ── OTHER SAVED FILES ──",
                    state=tk.DISABLED
                )
                for entry in reversed(other_entries):
                    icon = "🐍" if entry["type"] == ".py" else "📄"
                    activities_menu_popup.add_command(
                        label=f"  {icon}  {entry['name']}   🕐 {entry['time']}",
                        command=make_loader(entry)
                    )

        if event is None:
            return
        w = event.widget  # type: ignore[attr-defined]
        activities_menu_popup.post(w.winfo_rootx(), w.winfo_rooty() + w.winfo_height())

    activities_menu_popup = tk.Menu(window, tearoff=0, bg="#1e293b", fg="#f1f5f9",
                                    activebackground="#fb923c", activeforeground="#0f172a",
                                    font=("Segoe UI", 10))

    activities_btn = tk.Button(toolbar, text="📂  Activities", bg="#4a1d0e", fg="#fb923c",
                               activebackground="#c2410c", activeforeground="#ffffff",
                               font=("Georgia", 12, "bold"), relief=tk.FLAT,
                               cursor="hand2", padx=22, pady=10, bd=0, width=12,
                               command=lambda: None)
    activities_btn.pack(side=tk.LEFT, padx=6)
    activities_btn.bind("<Button-1>", activities_popup)

    # Help button
    def help_popup(event=None):
        if event is None:
            return
        w = event.widget  # type: ignore[attr-defined]
        help_menu_popup.post(w.winfo_rootx(), w.winfo_rooty() + w.winfo_height())

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

    def update_line_numbers(event=None):  # noqa: ARG001
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

    window._output_text = output_text  # type: ignore[attr-defined]

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
        fname = current_filename[0]
        with open(fname, "w") as f:
            f.write(content)
        ext = Path(fname).suffix or ".py"
        log_activity(Path(fname).name, str(Path(fname).parent), ext, content)
        statusbar.config(text=f"  ✦  Saved: {Path(fname).name}  →  Activities ✦")
    else:
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
    log_activity(f"script_{ts}.py", "(Activities)", ".py", content)
    notes_content = f"# Notes saved on {datetime.datetime.now().strftime('%b %d, %Y %I:%M %p')}\n\n"
    log_activity(f"notes_{ts}.txt", "(Activities)", ".txt", notes_content)
    statusbar.config(text=f"  ✦  Save All → script_{ts}.py & notes_{ts}.txt added to Activities ✦")

def exitprogram():
    if messagebox.askokcancel("Exit", "Do you really want to quit?"):
        save_activities()
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
    out = window._output_text  # type: ignore[attr-defined]

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

        except Exception:
            def show_err():
                out.config(state=tk.NORMAL)
                out.delete("1.0", tk.END)
                out.insert(tk.END, "❌  Failed to run code.")
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

    def on_pass_focus(e):  # noqa: ARG001
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

    # Add student info code to activities if not already present
    student_code = '''import tkinter as tk

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

root.mainloop()'''
    if not any(entry["name"] == "activity_1_student_info.py" for entry in activities_log):
        log_activity("activity_1_student_info.py", "(Activities)", ".py", student_code)

    # Add receipt generator code to activities if not already present
    receipt_code = '''import tkinter as tk

def generate_receipt():
    try:
        customer_number = int(customer_number_entry.get())
        customer_name = customer_name_entry.get()
        item = item_entry.get()
        price = int(price_entry.get())
        quantity = int(quantity_entry.get())
        
        total = price * quantity
        
        receipt_text.delete(1.0, tk.END)
        receipt_text.insert(tk.END, "----------------------------\\n")
        receipt_text.insert(tk.END, "         RECEIPT            \\n")
        receipt_text.insert(tk.END, f" customer number: {customer_number}\\n")
        receipt_text.insert(tk.END, f" customer name: {customer_name}\\n")
        receipt_text.insert(tk.END, f" item description: {item}\\n")
        receipt_text.insert(tk.END, f"YOUR TOTAL PRICE IS: {total}\\n")
        receipt_text.insert(tk.END, "----------------------------\\n")
    except ValueError:
        receipt_text.delete(1.0, tk.END)
        receipt_text.insert(tk.END, "Invalid input. Please enter numbers for customer number, price, and quantity.")

root = tk.Tk()
root.title("Receipt Generator")

tk.Label(root, text="Customer Number:").grid(row=0, column=0)
customer_number_entry = tk.Entry(root)
customer_number_entry.grid(row=0, column=1)

tk.Label(root, text="Customer Name:").grid(row=1, column=0)
customer_name_entry = tk.Entry(root)
customer_name_entry.grid(row=1, column=1)

tk.Label(root, text="Item:").grid(row=2, column=0)
item_entry = tk.Entry(root)
item_entry.grid(row=2, column=1)

tk.Label(root, text="Price:").grid(row=3, column=0)
price_entry = tk.Entry(root)
price_entry.grid(row=3, column=1)

tk.Label(root, text="Quantity:").grid(row=4, column=0)
quantity_entry = tk.Entry(root)
quantity_entry.grid(row=4, column=1)

tk.Button(root, text="Generate Receipt", command=generate_receipt).grid(row=5, column=0, columnspan=2)

receipt_text = tk.Text(root, height=10, width=40)
receipt_text.grid(row=6, column=0, columnspan=2)

root.mainloop()'''
    if not any(entry["name"] == "activity_2_receipt_generator.py" for entry in activities_log):
        log_activity("activity_2_receipt_generator.py", "(Activities)", ".py", receipt_code)

    # Add grade calculator code to activities if not already present
    grade_calculator_code = '''import tkinter as tk
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

        result_text.set(f"Student number: {number}\\nStudent: {name}\\nCourse: {course}\\nAverage: {round(average, 2)}\\nRemarks: {remarks}")
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

root.mainloop()'''
    if not any(entry["name"] == "activity_3_grade_calculator.py" for entry in activities_log):
        log_activity("activity_3_grade_calculator.py", "(Activities)", ".py", grade_calculator_code)

    payroll_system_code = '''import tkinter as tk
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

root = tk.Tk()
root.title("Payroll System")
root.geometry("420x520")
root.configure(bg="#f4f6f7")

title = tk.Label(root, text="PAYROLL SYSTEM", font=("Arial", 16, "bold"), bg="#f4f6f7")
title.pack(pady=10)

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

btn_frame = tk.Frame(root, bg="#f4f6f7")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Compute", width=10, bg="#2ecc71", fg="white", command=compute_pay).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Clear", width=10, bg="#fa9c04", fg="white", command=clear_fields).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Exit", width=10, bg="#e74c3c", fg="white", command=exit_app).grid(row=0, column=2, padx=5)

root.mainloop()'''
    if not any(entry["name"] == "activity_4_payroll_system.py" for entry in activities_log):
        log_activity("activity_4_payroll_system.py", "(Activities)", ".py", payroll_system_code)

    # Add student grading system code to activities if not already present
    grading_system_code = '''import tkinter as tk
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
        if not (0 <= prelim <= 100 and 0 <= midterm <= 100 and 0 <= final <= 100):
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
        tree.insert("", "end", values=(
            stud_id, name, course, subject, prelim, midterm, final,
            f"{average:.2f}", numerical, remark
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

def delete_record():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return
    confirm = messagebox.askyesno("Delete Record", "Are you sure you want to delete the selected record?")
    if confirm:
        tree.delete(selected_item)

root = tk.Tk()
root.title("Student Grading System")
root.geometry("950x650")
root.configure(bg="#00FFFF")
title = tk.Label(root,text="STUDENT GRADING SYSTEM",
font=("Arial",18,"bold"),bg="#00FFFF",fg="#1a3d7c")
title.pack(pady=10)
frame_info = tk.LabelFrame(root,text="Student Information",
font=("Arial",11,"bold"),padx=15,pady=10,bg="#f7fbff")
frame_info.pack(fill="x",padx=20,pady=5)
tk.Label(frame_info,text="Student\\nID:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
entry_id = ttk.Entry(frame_info)
entry_id.grid(row=0,column=1,pady=5)
tk.Label(frame_info,text="Student\\nName:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
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
frame_grades = tk.LabelFrame(root,text="Grades Input",
font=("Arial",11,"bold"),padx=15,pady=10,bg="#f7fbff")
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
button_frame = tk.Frame(root,bg="#00FFFF")
button_frame.pack(pady=10)
tk.Button(button_frame,text="Compute",width=15,bg="#2c7be5",fg="white",
font=("Arial",10,"bold"),command=compute_grade).grid(row=0,column=0,padx=10)
tk.Button(button_frame,text="Clear",width=15,bg="#dc3545",fg="white",
font=("Arial",10,"bold"),command=clear_fields).grid(row=0,column=1,padx=10)
tk.Button(button_frame,text="Delete Selected",width=15,bg="#ff8800",fg="white",
font=("Arial",10,"bold"),command=delete_record).grid(row=0,column=2,padx=10)
frame_result = tk.LabelFrame(root,text="Result",
font=("Arial",11,"bold"),padx=15,pady=15,bg="#f7fbff")
frame_result.pack(fill="x",padx=20,pady=10)
tk.Label(frame_result,text="Average\\nGrade:",bg="#f7fbff").grid(row=0,column=0,sticky="w")
avg_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="blue",bg="#f7fbff")
avg_result.grid(row=0,column=1)
tk.Label(frame_result,text="Numerical\\nValue:",bg="#f7fbff").grid(row=1,column=0,sticky="w")
num_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="green",bg="#f7fbff")
num_result.grid(row=1,column=1)
tk.Label(frame_result,text="Remarks:",bg="#f7fbff").grid(row=2,column=0,sticky="w")
remark_result = tk.Label(frame_result,font=("Arial",11,"bold"),fg="red",bg="#f7fbff")
remark_result.grid(row=2,column=1)
frame_table = tk.LabelFrame(root,text="Student Dataset Records",
font=("Arial",11,"bold"),bg="#f7fbff")
frame_table.pack(fill="both",expand=True,padx=20,pady=10)
columns = ("ID","Name","Course","Subject","Prelim","Midterm","Final","Average","Numerical","Remark")
tree = ttk.Treeview(frame_table,columns=columns,show="headings")
for col in columns:
    tree.heading(col,text=col)
    tree.column(col,width=90)
tree.pack(fill="both",expand=True)
root.mainloop()'''
    if not any(entry["name"] == "activity_5_grading_system.py" for entry in activities_log):
        log_activity("activity_5_grading_system.py", "(Activities)", ".py", grading_system_code)

    # Add student CRUD system code to activities if not already present
    crud_system_code = '''from tkinter import *
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
    Read()

def Read():
    tree.delete(*tree.get_children())
    Database()
    cursor.execute("SELECT * FROM member ORDER BY lastname ASC")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        tree.insert("", END, values=row[1:8])

def Update():
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, \'values\')
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

def Delete():
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, \'values\')
    Database()
    cursor.execute("DELETE FROM member WHERE firstname=? AND lastname=?", (values[0], values[1]))
    conn.commit()
    conn.close()
    txt_result.config(text="Deleted Successfully!", fg="red")
    Read()

def OnSelected(event):
    selected = tree.focus()
    values = tree.item(selected, \'values\')
    FIRSTNAME.set(values[0])
    LASTNAME.set(values[1])
    GENDER.set(values[2])
    ADDRESS.set(values[3])
    PROVINCE.set(values[4])
    USERNAME.set(values[5])
    PASSWORD.set(values[6])

def Exit():
    result = tkMessageBox.askquestion("Exit", "Are you sure?")
    if result == "yes":
        root.destroy()

FIRSTNAME = StringVar()
LASTNAME = StringVar()
GENDER = StringVar()
ADDRESS = StringVar()
PROVINCE = StringVar()
USERNAME = StringVar()
PASSWORD = StringVar()

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
province_combo[\'values\'] = (
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

Button(Buttons, text="Create", bg="#2ecc71", fg="white", command=Create, width=12).pack(pady=2)
Button(Buttons, text="Read", bg="#3498db", fg="white", command=Read, width=12).pack(pady=2)
Button(Buttons, text="Update", bg="#f1c40f", fg="black", command=Update, width=12).pack(pady=2)
Button(Buttons, text="Delete", bg="#e74c3c", fg="white", command=Delete, width=12).pack(pady=2)
Button(Buttons, text="Exit", bg="#34495e", fg="white", command=Exit, width=12).pack(pady=2)

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
root.mainloop()'''
    if not any(entry["name"] == "Activity_6_student_crud.py" for entry in activities_log):
        log_activity("Activity_6_student_crud.py", "(Activities)", ".py", crud_system_code)

    # Add payroll with login system code to activities if not already present
    payroll_login_code = '''import tkinter as tk
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
emp_no TEXT, name TEXT, gender TEXT, position TEXT,
rate REAL, days REAL, sss REAL, philhealth REAL,
cash REAL, gross REAL, deductions REAL, net REAL
)
""")
try: cursor.execute("ALTER TABLE payroll ADD COLUMN sss REAL")
except: pass
try: cursor.execute("ALTER TABLE payroll ADD COLUMN philhealth REAL")
except: pass
try: cursor.execute("ALTER TABLE payroll ADD COLUMN cash REAL")
except: pass
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
INSERT INTO payroll (emp_no, name, gender, position, rate, days, gross,
sss, philhealth, cash, deductions, net) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
""", (
        emp_no_entry.get(), name_entry.get(), gender_var.get(), position_cb.get(),
        float(rate_entry.get()), float(days_entry.get()), gross,
        float(sss_entry.get()), float(philhealth_entry.get()), float(cash_entry.get()),
        deductions, net
    ))
    conn.commit()
    load_data()
    messagebox.showinfo("Saved", "Record saved!")

def load_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("""
SELECT emp_no, name, gender, position, rate, days, gross,
sss, philhealth, cash, deductions, net FROM payroll
""")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Please select a record to delete!")
        return
    if not messagebox.askyesno("Delete", "Are you sure you want to delete?"):
        return
    for item in selected:
        values = tree.item(item, "values")
        cursor.execute("DELETE FROM payroll WHERE emp_no=? AND name=? AND gross=? AND net=?",
                       (values[0], values[1], values[6], values[11]))
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

tk.Label(root, text="PAYROLL SYSTEM", font=("Arial", 15, "bold"), bg="#f4f6f7").pack(pady=10)

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
tk.Radiobutton(emp_frame, text="Female", variable=gender_var, value="Female").grid(row=2, column=1, sticky="e")
tk.Label(emp_frame, text="Position:").grid(row=3, column=0, sticky="w")
position_cb = ttk.Combobox(emp_frame, width=22)
position_cb[\'values\'] = ("Cashier", "Bagger", "Manager", "Janitor", "Guard")
position_cb.grid(row=3, column=1, pady=3)
tk.Label(emp_frame, text="Rate per Day:").grid(row=4, column=0, sticky="w")
rate_entry = tk.Entry(emp_frame, width=25)
rate_entry.grid(row=4, column=1, pady=3)
tk.Label(emp_frame, text="Days Worked:").grid(row=5, column=0, sticky="w")
days_entry = tk.Entry(emp_frame, width=25)
days_entry.grid(row=5, column=1, pady=3)

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

table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=10, fill="both", expand=True)
columns = ("EMP_NO","NAME","GENDER","POSITION","RATE","DAYS",
           "GROSSPAY","SSS","PHILHEALTH","CASH_ADVANCE","DEDUCTION","NET_PAY")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=90)
tree.pack(fill="both", expand=True)

btn_frame = tk.Frame(root, bg="#f4f6f7")
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Compute", width=10, bg="#2ecc71", fg="white", command=compute_pay).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Clear",   width=10, bg="#fa9c04", fg="white", command=clear_fields).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Exit",    width=10, bg="#e74c3c", fg="white", command=exit_app).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Delete",  width=10, bg="#c0392b", fg="white", command=delete_data).grid(row=0, column=3, padx=5)

load_data()
root.mainloop()'''
    if not any(entry["name"] == "activity_7_payroll_with_login.py" for entry in activities_log):
        log_activity("activity_7_payroll_with_login.py", "(Activities)", ".py", payroll_login_code)

    # Add grading system with CRUD and login to activities if not already present
    grading_crud_login_code = '''import tkinter as tk
from tkinter import ttk, messagebox

def open_main_app():
    login_win.destroy()

    def compute_grade():
        try:
            prelim = float(entry_prelim.get())
            midterm = float(entry_midterm.get())
            final = float(entry_final.get())
            if not (0 <= prelim <= 100 and 0 <= midterm <= 100 and 0 <= final <= 100):
                messagebox.showerror("Error", "Grades must be between 0 and 100")
                return None, None, None
            average = round(((prelim*0.20)+(midterm*0.30)+(final*0.50)),2)
            if average >= 97: numerical="1.00"; remark="Excellent"
            elif average >= 94: numerical="1.25"; remark="Very Good"
            elif average >= 91: numerical="1.50"; remark="Very Good"
            elif average >= 88: numerical="1.75"; remark="Good"
            elif average >= 85: numerical="2.00"; remark="Above Average"
            elif average >= 82: numerical="2.25"; remark="Above Average"
            elif average >= 79: numerical="2.50"; remark="Average"
            elif average >= 76: numerical="2.75"; remark="Average"
            elif average >= 75: numerical="3.00"; remark="Passing"
            elif average >= 72: numerical="3.25"; remark="Conditional"
            elif average >= 69: numerical="3.50"; remark="Conditional"
            elif average >= 66: numerical="3.75"; remark="Failed"
            elif average >= 65: numerical="4.00"; remark="Failed"
            else: numerical="5.00"; remark="Failed"
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
            stud_id, name, course, subject,
            entry_prelim.get(), entry_midterm.get(), entry_final.get(),
            f"{average:.2f}", numerical, remark
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
        if messagebox.askyesno("Delete Record", "Are you sure you want to delete the selected record?"):
            tree.delete(selected_item)

    def update_record():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update.")
            return
        average, numerical, remark = compute_grade()
        if average is None:
            return
        tree.item(selected_item, values=(
            entry_id.get(), entry_name.get(), combo_course.get(), entry_subject.get(),
            entry_prelim.get(), entry_midterm.get(), entry_final.get(),
            f"{average:.2f}", numerical, remark
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

    root = tk.Tk()
    root.title("Student Grading System (CRUD)")
    root.geometry("900x650")
    root.configure(bg="#00FFFF")

    tk.Label(root, text="STUDENT GRADING SYSTEM", font=("Arial",18,"bold"),
             bg="#00FFFF", fg="#1a3d7c").pack(pady=10)

    frame_info = tk.LabelFrame(root, text="Student Information", font=("Arial",11,"bold"),
                               padx=15, pady=10, bg="#f7fbff")
    frame_info.pack(fill="x", padx=20, pady=5)
    tk.Label(frame_info, text="Student ID:", bg="#f7fbff").grid(row=0, column=0, sticky="w")
    entry_id = ttk.Entry(frame_info); entry_id.grid(row=0, column=1, pady=5)
    tk.Label(frame_info, text="Student Name:", bg="#f7fbff").grid(row=1, column=0, sticky="w")
    entry_name = ttk.Entry(frame_info); entry_name.grid(row=1, column=1, pady=5)
    tk.Label(frame_info, text="Course:", bg="#f7fbff").grid(row=2, column=0, sticky="w")
    combo_course = ttk.Combobox(frame_info,
        values=["BSIT","BSCS","BSBA","BSED","BSCE","BSME","BSEE","BSCpE","BSTCM","BSES","BSMET","BSAP"],
        state="readonly"); combo_course.grid(row=2, column=1, pady=5)
    tk.Label(frame_info, text="Subject:", bg="#f7fbff").grid(row=3, column=0, sticky="w")
    entry_subject = ttk.Entry(frame_info); entry_subject.grid(row=3, column=1, pady=5)

    frame_grades = tk.LabelFrame(root, text="Grades Input", font=("Arial",11,"bold"),
                                 padx=15, pady=10, bg="#f7fbff")
    frame_grades.pack(fill="x", padx=20, pady=10)
    tk.Label(frame_grades, text="Prelim:", bg="#f7fbff").grid(row=0, column=0)
    entry_prelim = ttk.Entry(frame_grades, width=10); entry_prelim.grid(row=0, column=1, padx=10)
    tk.Label(frame_grades, text="Midterm:", bg="#f7fbff").grid(row=0, column=2)
    entry_midterm = ttk.Entry(frame_grades, width=10); entry_midterm.grid(row=0, column=3, padx=10)
    tk.Label(frame_grades, text="Final:", bg="#f7fbff").grid(row=0, column=4)
    entry_final = ttk.Entry(frame_grades, width=10); entry_final.grid(row=0, column=5, padx=10)

    button_frame = tk.Frame(root, bg="#00FFFF")
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Add / Compute", width=15, bg="#2c7be5", fg="white",
              font=("Arial",10,"bold"), command=add_record).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Update Selected", width=15, bg="#ffc107", fg="white",
              font=("Arial",10,"bold"), command=update_record).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Clear Fields", width=15, bg="#dc3545", fg="white",
              font=("Arial",10,"bold"), command=clear_fields).grid(row=0, column=2, padx=10)
    tk.Button(button_frame, text="Delete Selected", width=15, bg="#ff8800", fg="white",
              font=("Arial",10,"bold"), command=delete_record).grid(row=0, column=3, padx=10)

    frame_result = tk.LabelFrame(root, text="Result", font=("Arial",11,"bold"),
                                 padx=15, pady=15, bg="#f7fbff")
    frame_result.pack(fill="x", padx=20, pady=10)
    tk.Label(frame_result, text="Average Grade:", bg="#f7fbff").grid(row=0, column=0, sticky="w")
    avg_result = tk.Label(frame_result, font=("Arial",11,"bold"), fg="blue", bg="#f7fbff")
    avg_result.grid(row=0, column=1)
    tk.Label(frame_result, text="Numerical Value:", bg="#f7fbff").grid(row=1, column=0, sticky="w")
    num_result = tk.Label(frame_result, font=("Arial",11,"bold"), fg="green", bg="#f7fbff")
    num_result.grid(row=1, column=1)
    tk.Label(frame_result, text="Remarks:", bg="#f7fbff").grid(row=2, column=0, sticky="w")
    remark_result = tk.Label(frame_result, font=("Arial",11,"bold"), fg="red", bg="#f7fbff")
    remark_result.grid(row=2, column=1)

    frame_table = tk.LabelFrame(root, text="Student Dataset Records",
                                font=("Arial",11,"bold"), bg="#f7fbff")
    frame_table.pack(fill="both", expand=True, padx=20, pady=10)
    columns = ("ID","Name","Course","Subject","Prelim","Midterm","Final","Average","Numerical","Remark")
    tree = ttk.Treeview(frame_table, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=90)
    tree.pack(fill="both", expand=True)
    tree.bind("<Double-1>", load_record)

    root.mainloop()


def check_login():
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "1234"
    if login_entry_user.get() == VALID_USERNAME and login_entry_pass.get() == VALID_PASSWORD:
        open_main_app()
    else:
        login_error_label.config(text="Invalid username or password.", fg="red")
        login_entry_pass.delete(0, tk.END)


login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("350x250")
login_win.resizable(False, False)
login_win.configure(bg="#00FFFF")

tk.Label(login_win, text="STUDENT GRADING SYSTEM", font=("Arial",13,"bold"),
         bg="#00FFFF", fg="#1a3d7c").pack(pady=(20,5))
tk.Label(login_win, text="Please log in to continue", font=("Arial",9),
         bg="#00FFFF", fg="#333333").pack(pady=(0,15))

login_frame = tk.Frame(login_win, bg="#f7fbff", padx=20, pady=15)
login_frame.pack(padx=20, fill="x")

tk.Label(login_frame, text="Username:", bg="#f7fbff", font=("Arial",10)).grid(row=0, column=0, sticky="w", pady=5)
login_entry_user = ttk.Entry(login_frame, width=20)
login_entry_user.grid(row=0, column=1, pady=5, padx=5)
login_entry_user.focus()

tk.Label(login_frame, text="Password:", bg="#f7fbff", font=("Arial",10)).grid(row=1, column=0, sticky="w", pady=5)
login_entry_pass = ttk.Entry(login_frame, width=20, show="*")
login_entry_pass.grid(row=1, column=1, pady=5, padx=5)
login_entry_pass.bind("<Return>", lambda event: check_login())

login_error_label = tk.Label(login_win, text="", bg="#00FFFF", font=("Arial",9))
login_error_label.pack(pady=(5,0))

tk.Button(login_win, text="Login", width=15, bg="#2c7be5", fg="white",
          font=("Arial",10,"bold"), command=check_login).pack(pady=8)

login_win.mainloop()'''
    if not any(entry["name"] == "activity_8_grading_crud_login.py" for entry in activities_log):
        log_activity("activity_8_grading_crud_login.py", "(Activities)", ".py", grading_crud_login_code)

    start_login()
