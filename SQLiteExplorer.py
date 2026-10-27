#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
======================================
SQLite Explorer by ScarfacePalmer 2026
======================================
'''

import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class SQLiteViewer(ctk.CTk):
    ROW_HEIGHT = 35  
    HEADER_TOP = 32
    HEADER_HEIGHT = 65
    CHECKBOX_WIDTH = 48
    MIN_COL_WIDTH = 85
    MAX_COL_WIDTH = 500

    def __init__(self):
        super().__init__()
        self.title("SQLite Viewer")
        self.geometry("1450x850")
        self.minsize(900, 500)

        self.accent_color = "#008080"
        self.accent_hover = "#006666"

        self.conn, self.db_path = None, None
        self.table_names, self.columns, self.rows, self.filtered_indices = [], [], [], []
        self.selected_rows, self.selected_columns = set(), set()
        self.filter_vars, self.filter_entries, self.column_widths = [], [], {}

        self.current_lang = "DE"
        self.translations = {
            "DE": {
                "title": "SQLite Viewer", "open_db": "📂 Datenbank öffnen", "open_sql": "📄 SQL-Dump öffnen",
                "table_lbl": "Tabelle:", "refresh": "⟳ Aktualisieren", "all_rows": "Alle Zeilen",
                "all_cols": "Alle Spalten", "copy_sel": "📋 Auswahl kopieren", "export_sel": "📊 Exportieren",
                "ready": "Bereit", "db_dialog_title": "SQLite-Datenbank öffnen", "db_types": "SQLite Datenbanken",
                "all_files": "Alle Dateien", "sql_dialog_title": "SQLite SQL-Dump öffnen", "sql_types": "SQL-Dumps",
                "open_err": "Datenbank konnte nicht geöffnet werden", "sql_err": "SQL-Dump konnte nicht geladen werden",
                "sql_decode_err": "Der SQL-Dump konnte nicht als Text gelesen werden.", "no_tables_title": "Keine Tabellen",
                "no_tables_msg": "Keine normalen SQLite-Tabellen gefunden.", "load_table_err": "Tabelle konnte nicht geladen werden",
                "filter_placeholder": "Filtern", "rows_visible": "{visible} von {total} Zeilen sichtbar",
                "copied_cell": "Zelleninhalt in die Zwischenablage kopiert", "no_rows_sel_title": "Keine Zeilen ausgewählt",
                "no_rows_sel_msg": "Bitte mindestens eine Zeile auswählen.", "no_cols_sel_title": "Keine Spalten ausgewählt",
                "no_cols_sel_msg": "Bitte mindestens eine Spalte auswählen.", "no_visible_title": "Keine sichtbaren Zeilen",
                "no_visible_msg": "Die ausgewählten Zeilen werden aktuell vom Filter ausgeblendet.",
                "copied_status": "{rows} Zeilen × {cols} Spalten kopiert", "export_success": "Erfolgreich exportiert nach {filename}",
                "info_str": "{rows} Zeilen · {cols} Spalten", "no_db": "Keine Datenbank geöffnet",
                "selection_info": "Zeilen: {rows}   Spalten: {cols}/{total_cols}"
            },
            "EN": {
                "title": "SQLite Viewer", "open_db": "📂 Open Database", "open_sql": "📄 Open SQL Dump",
                "table_lbl": "Table:", "refresh": "⟳ Refresh", "all_rows": "All Rows",
                "all_cols": "All Columns", "copy_sel": "📋 Copy Selection", "export_sel": "📊 Export Selection",
                "ready": "Ready", "db_dialog_title": "Open SQLite Database", "db_types": "SQLite Databases",
                "all_files": "All Files", "sql_dialog_title": "Open SQLite SQL Dump", "sql_types": "SQL Dumps",
                "open_err": "Database could not be opened", "sql_err": "SQL Dump could not be loaded",
                "sql_decode_err": "The SQL dump could not be read as text.", "no_tables_title": "No Tables",
                "no_tables_msg": "No normal SQLite tables found.", "load_table_err": "Table could not be loaded",
                "filter_placeholder": "Filter", "rows_visible": "{visible} of {total} rows visible",
                "copied_cell": "Cell content copied to clipboard", "no_rows_sel_title": "No rows selected",
                "no_rows_sel_msg": "Please select at least one row.", "no_cols_sel_title": "No columns selected",
                "no_cols_sel_msg": "Please select at least one column.", "no_visible_title": "No visible rows",
                "no_visible_msg": "The selected rows are currently hidden by the filter.",
                "copied_status": "{rows} rows × {cols} columns copied", "export_success": "Successfully exported to {filename}",
                "info_str": "{rows} rows · {cols} columns", "no_db": "No database opened",
                "selection_info": "Rows: {rows}   Columns: {cols}/{total_cols}"
            }
        }
        self.resize_column, self.resize_start_x, self.resize_start_width, self.resize_guide = None, None, None, None
        self._build_ui()
        self._apply_theme()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _get_txt(self, key, **kwargs):
        text = self.translations[self.current_lang].get(key, "")
        return text.format(**kwargs) if kwargs else text

    def _build_ui(self):
        self.toolbar = ctk.CTkFrame(self, corner_radius=0)
        self.toolbar.pack(fill="x", side="top")

        self.btn_open_db = ctk.CTkButton(self.toolbar, text=self._get_txt("open_db"), command=self.open_database, fg_color=self.accent_color, hover_color=self.accent_hover)
        self.btn_open_db.pack(side="left", padx=(10, 5), pady=8)

        self.btn_open_sql = ctk.CTkButton(self.toolbar, text=self._get_txt("open_sql"), command=self.open_sql, fg_color=self.accent_color, hover_color=self.accent_hover)
        self.btn_open_sql.pack(side="left", padx=(0, 15), pady=8)

        self.lbl_table = ctk.CTkLabel(self.toolbar, text=self._get_txt("table_lbl"))
        self.lbl_table.pack(side="left", padx=(5, 5))

        self.table_var = tk.StringVar()
        self.table_combo = ctk.CTkComboBox(self.toolbar, variable=self.table_var, state="readonly", width=250, command=self.table_changed)
        self.table_combo.pack(side="left", padx=5, pady=8)

        self.btn_refresh = ctk.CTkButton(self.toolbar, text=self._get_txt("refresh"), command=self.refresh, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color)
        self.btn_refresh.pack(side="left", padx=5, pady=8)

        self.lang_var = tk.StringVar(value="DE")
        self.lang_combo = ctk.CTkComboBox(self.toolbar, values=["DE", "EN"], variable=self.lang_var, state="readonly", width=75, command=self._change_language)
        self.lang_combo.pack(side="right", padx=(5, 15), pady=8)

        self.btn_theme_toggle = ctk.CTkButton(self.toolbar, text="⚬" if ctk.get_appearance_mode() == "Light" else "☀", width=40, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color, command=self.toggle_appearance_mode)
        self.btn_theme_toggle.pack(side="right", padx=5, pady=8)

        self.lbl_info = ctk.CTkLabel(self.toolbar, text="") 
        self.info_var = tk.StringVar(value=self._get_txt("no_db"))
        self.lbl_info.configure(textvariable=self.info_var)
        self.lbl_info.pack(side="right", padx=(10, 10))

        self.selection_bar = ctk.CTkFrame(self, corner_radius=0, height=45)
        self.selection_bar.pack(fill="x", side="top", pady=(2, 0))

        self.rows_toggle = ctk.CTkButton(self.selection_bar, text="☐ " + self._get_txt("all_rows"), command=self.toggle_all_rows, width=120, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=("#b0b0b0", "#555555"))
        self.rows_toggle.pack(side="left", padx=(10, 8), pady=6)

        self.columns_toggle = ctk.CTkButton(self.selection_bar, text="☐ " + self._get_txt("all_cols"), command=self.toggle_all_columns, width=120, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=("#b0b0b0", "#555555"))
        self.columns_toggle.pack(side="left", pady=6)

        self.selection_info = tk.StringVar(value="")
        self.lbl_sel_info = ctk.CTkLabel(self.selection_bar, textvariable=self.selection_info)
        self.lbl_sel_info.pack(side="right", padx=15)

        self.table_frame = ctk.CTkFrame(self, corner_radius=4)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.header = tk.Canvas(self.table_frame, height=self.HEADER_HEIGHT, highlightthickness=0, bd=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.body = tk.Canvas(self.table_frame, highlightthickness=0, bd=0)
        self.body.grid(row=1, column=0, sticky="nsew")

        self.vbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self._vscroll)
        self.vbar.grid(row=1, column=1, sticky="ns")
        self.hbar = ctk.CTkScrollbar(self.table_frame, orientation="horizontal", command=self._hscroll)
        self.hbar.grid(row=2, column=0, sticky="ew")

        self.table_frame.rowconfigure(1, weight=1)
        self.table_frame.columnconfigure(0, weight=1)
        self.body.configure(yscrollcommand=self.vbar.set, xscrollcommand=self._body_xscroll)

        self.header.bind("<ButtonPress-1>", self._header_press)
        self.header.bind("<Button-1>", self._header_click, add="+")
        self.header.bind("<B1-Motion>", self._header_drag)
        self.header.bind("<ButtonRelease-1>", self._header_release)
        self.header.bind("<MouseWheel>", self._wheel)
        self.body.bind("<Button-1>", self._body_click)
        self.body.bind("<Double-1>", self._body_double_click)
        self.body.bind("<MouseWheel>", self._wheel)

        self.status_frame = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color="transparent")
        self.status_frame.pack(fill="x", side="bottom", padx=15, pady=5)

        self.status_var = tk.StringVar(value=self._get_txt("ready"))
        self.lbl_status = ctk.CTkLabel(self.status_frame, textvariable=self.status_var, anchor="w")
        self.lbl_status.pack(side="left", fill="x", expand=True)

        self.btn_export_sel = ctk.CTkButton(self.status_frame, text=self._get_txt("export_sel"), command=self.export_selection, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color, width=140)
        self.btn_export_sel.pack(side="right", padx=(10, 0))

        self.btn_copy_sel = ctk.CTkButton(self.status_frame, text=self._get_txt("copy_sel"), command=self.copy_selection, fg_color=self.accent_color, hover_color=self.accent_hover, width=160)
        self.btn_copy_sel.pack(side="right", padx=(10, 0))

    def toggle_appearance_mode(self):
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("Dark")
            self.btn_theme_toggle.configure(text="☀")
        else:
            ctk.set_appearance_mode("Light")
            self.btn_theme_toggle.configure(text="☾")
        self._apply_theme()

    def _change_language(self, choice):
        self.current_lang = choice
        self.title(self._get_txt("title"))
        self.btn_open_db.configure(text=self._get_txt("open_db"))
        self.btn_open_sql.configure(text=self._get_txt("open_sql"))
        self.lbl_table.configure(text=self._get_txt("table_lbl"))
        self.btn_refresh.configure(text=self._get_txt("refresh"))
        self.btn_copy_sel.configure(text=self._get_txt("copy_sel"))
        self.btn_export_sel.configure(text=self._get_txt("export_sel"))
        if self.rows: self.apply_filters()
        else: self.status_var.set(self._get_txt("ready"))
        self._update_info()
        self._draw_header()

    def _apply_theme(self):
        is_dark = ctk.get_appearance_mode() == "Dark"
        if is_dark:
            self.bg, self.panel, self.fg, self.field, self.filter_field = "#1d1e22", "#2d2f34", "#f5f7fa", "#141517", "#2d2f34"
            self.border, self.header_bg, self.selected_bg, self.placeholder, self.alt_row = "#3f454d", "#25262a", "#004d4d", "#aeb6c1", "#1a1b1e"
        else:
            self.bg, self.panel, self.fg, self.field, self.filter_field = "#f3f3f3", "#ffffff", "#202124", "#ffffff", "#f3f3f3"
            self.border, self.header_bg, self.selected_bg, self.placeholder, self.alt_row = "#d1d1d1", "#f9f9f9", "#ccffff", "#888888", "#f5f6f8"
        self.configure(fg_color=self.bg)
        self.header.configure(bg=self.header_bg, highlightbackground=self.border)
        self.body.configure(bg=self.field, highlightbackground=self.border)
        self._draw_header()
        self._draw_body()

    def open_database(self):
        path = filedialog.askopenfilename(title=self._get_txt("db_dialog_title"), filetypes=[(self._get_txt("db_types"), "*.db *.sqlite *.sqlite3"), (self._get_txt("all_files"), "*.*")])
        if not path: return
        try:
            if self.conn: self.conn.close()
            uri = "file:" + os.path.abspath(path).replace("\\", "/") + "?mode=ro"
            self.conn = sqlite3.connect(uri, uri=True)
            self.db_path = path
            self._load_tables()
            self.status_var.set(f"{os.path.basename(path)}")
        except Exception as exc: messagebox.showerror(self._get_txt("open_err"), str(exc))

    def open_sql(self):
        path = filedialog.askopenfilename(title=self._get_txt("sql_dialog_title"), filetypes=[(self._get_txt("sql_types"), "*.sql"), (self._get_txt("all_files"), "*.*")])
        if not path: return
        try:
            if self.conn: self.conn.close()
            self.conn = sqlite3.connect(":memory:")
            with open(path, "rb") as f: raw = f.read()
            script = None
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                try: script = raw.decode(encoding); break
                except UnicodeDecodeError: pass
            if script is None: raise ValueError(self._get_txt("sql_decode_err"))
            self.conn.executescript(script)
            self.conn.commit()
            self.db_path = path
            self._load_tables()
            self.status_var.set(f"{os.path.basename(path)}")
        except Exception as exc:
            if self.conn: self.conn.close(); self.conn = None
            messagebox.showerror(self._get_txt("sql_err"), str(exc))

    def _load_tables(self):
        cur = self.conn.cursor()
        self.table_names = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name COLLATE NOCASE").fetchall()]
        self.table_combo.configure(values=self.table_names)
        if not self.table_names:
            self.table_var.set(""); self.columns, self.rows, self.filtered_indices = [], [], []
            self._draw_header(); self._draw_body()
            messagebox.showinfo(self._get_txt("no_tables_title"), self._get_txt("no_tables_msg"))
            return
        self.table_combo.set(self.table_names[0])
        self.load_table(self.table_names[0])

    def table_changed(self, choice=None):
        if self.table_var.get(): self.load_table(self.table_var.get())

    def refresh(self):
        if self.conn and self.table_var.get(): self.load_table(self.table_var.get())

    def load_table(self, table_name):
        try:
            qname = '"' + table_name.replace('"', '""') + '"'
            cur = self.conn.cursor()
            info = cur.execute(f"PRAGMA table_info({qname})").fetchall()
            self.columns = [row[1] for row in info]
            self.rows = cur.execute(f"SELECT * FROM {qname}").fetchall()
            self.selected_rows.clear()
            self.selected_columns.clear()
            self.filter_vars = [tk.StringVar(value="") for _ in self.columns]
            self.filter_entries = []
            self.column_widths = {i: self._initial_width(i) for i in range(len(self.columns))}
            self.filtered_indices = list(range(len(self.rows)))
            self._draw_header(); self._draw_body(); self._update_info()
        except Exception as exc: messagebox.showerror(self._get_txt("load_table_err"), str(exc))

    def _initial_width(self, index):
        longest = len(self.columns[index])
        for row in self.rows[:100]:
            longest = max(longest, len("NULL" if row[index] is None else str(row[index])))
        return max(self.MIN_COL_WIDTH, min(self.MAX_COL_WIDTH, longest * 9 + 35))

    def _x_positions(self):
        result, x = [], self.CHECKBOX_WIDTH
        for i in range(len(self.columns)):
            width = self.column_widths.get(i, 120)
            result.append((x, x + width)); x += width
        return result

    def _total_width(self):
        return self.CHECKBOX_WIDTH + sum(self.column_widths.get(i, 120) for i in range(len(self.columns)))

    def _draw_header(self):
        self.header.delete("all")
        for entry in self.filter_entries:
            try: entry.destroy()
            except tk.TclError: pass
        self.filter_entries = []
        if not self.columns:
            self.header.configure(scrollregion=(0, 0, 1, self.HEADER_HEIGHT)); return
        total_width = self._total_width()
        self.header.configure(scrollregion=(0, 0, total_width, self.HEADER_HEIGHT))
        self._draw_header_box(0, self.CHECKBOX_WIDTH, "", None)
        for i, name in enumerate(self.columns):
            x1, x2 = self._x_positions()[i]
            self._draw_header_box(x1, x2 - x1, name, i)

    def _draw_header_box(self, x, width, title, col_index):
        self.header.create_rectangle(x, 0, x + width, self.HEADER_TOP, fill=self.header_bg, outline=self.border)
        if col_index is None: return
        checkbox = "☑" if col_index in self.selected_columns else "☐"
        self.header.create_text(x + self.CHECKBOX_WIDTH / 2, self.HEADER_TOP / 2, text=checkbox, fill=self.accent_color if checkbox == "☑" else self.fg, anchor="center", font=("Segoe UI Symbol", 16), tags=(f"header_col_{col_index}", f"header_cb_{col_index}"))
        self.header.create_text(x + self.CHECKBOX_WIDTH + 6, self.HEADER_TOP / 2, text=title, fill=self.fg, anchor="w", font=("Segoe UI", 11, "bold"))
        self.header.create_rectangle(x, self.HEADER_TOP, x + width, self.HEADER_HEIGHT, fill=self.header_bg, outline=self.border)
        entry = tk.Entry(self.header, relief="flat", bd=0, bg=self.filter_field, fg=self.placeholder, insertbackground=self.fg, selectbackground=self.selected_bg, font=("Segoe UI", 10, "italic"))
        entry.insert(0, self._get_txt("filter_placeholder"))

        def focus_in(_e):
            if entry.get() == self._get_txt("filter_placeholder"): entry.delete(0, "end"); entry.configure(fg=self.fg, font=("Segoe UI", 10, "normal"))
        def focus_out(_e, idx=col_index):
            if not entry.get().strip(): entry.delete(0, "end"); entry.insert(0, self._get_txt("filter_placeholder")); entry.configure(fg=self.placeholder, font=("Segoe UI", 10, "italic")); self.filter_vars[idx].set("")
            else: self.filter_vars[idx].set(entry.get())
            self.apply_filters()
        def key_release(_e, idx=col_index):
            self.filter_vars[idx].set("" if entry.get() == self._get_txt("filter_placeholder") else entry.get())
            self.apply_filters()

        entry.bind("<FocusIn>", focus_in); entry.bind("<FocusOut>", focus_out); entry.bind("<KeyRelease>", key_release)
        entry.bind("<ButtonPress-1>", self._header_press, add="+"); entry.bind("<B1-Motion>", self._header_drag, add="+"); entry.bind("<ButtonRelease-1>", self._header_release, add="+")
        self.header.create_window(x + 5, self.HEADER_TOP + 2, window=entry, width=max(30, width - 10), height=27, anchor="nw")
        self.filter_entries.append(entry)

    def _update_header_checkboxes(self):
        for i in range(len(self.columns)):
            checkbox = "☑" if i in self.selected_columns else "☐"
            tag = f"header_cb_{i}"
            self.header.itemconfig(tag, text=checkbox, fill=self.accent_color if checkbox == "☑" else self.fg)

    def _update_column_selection_highlights(self, col_index):
        total = len(self.filtered_indices)
        batch_size = 50

        def update_batch(start_idx):
            end_idx = min(start_idx + batch_size, total)
            for display_index in range(start_idx, end_idx):
                row_index = self.filtered_indices[display_index]
                row_selected = row_index in self.selected_rows
                col_selected = col_index in self.selected_columns
                fill = self.selected_bg if (row_selected and col_selected) else (self.alt_row if display_index % 2 else self.field)
                self.body.itemconfig(f"cell_{display_index}_{col_index}", fill=fill)
            if end_idx < total:
                self.after(5, lambda: update_batch(end_idx))

        update_batch(0)

    def _draw_body(self):
        self.body.delete("all")
        if not self.columns: self.body.configure(scrollregion=(0, 0, 1, 1)); return
        self.body.configure(scrollregion=(0, 0, self._total_width(), max(1, len(self.filtered_indices) * self.ROW_HEIGHT)))
        for display_index in range(len(self.filtered_indices)): self._draw_single_row_graphics(display_index)

    def _draw_single_row_graphics(self, display_index):
        row_tag = f"drow_{display_index}"
        self.body.delete(row_tag)
        row_index = self.filtered_indices[display_index]
        y1, y2 = display_index * self.ROW_HEIGHT, (display_index + 1) * self.ROW_HEIGHT
        row_selected = row_index in self.selected_rows
        positions = self._x_positions()

        self.body.create_rectangle(0, y1, self.CHECKBOX_WIDTH, y2, fill=self.field, outline=self.border, tags=(row_tag, f"row_cb_{display_index}"))
        checkbox = "☑" if row_selected else "☐"
        self.body.create_text(self.CHECKBOX_WIDTH / 2, (y1 + y2) / 2, text=checkbox, fill=self.accent_color if row_selected else self.fg, anchor="center", font=("Segoe UI Symbol", 18), tags=(row_tag, f"row_cb_txt_{display_index}"))

        row = self.rows[row_index]
        for col_index, (x1, x2) in enumerate(positions):
            fill = self.selected_bg if (row_selected and col_index in self.selected_columns) else (self.alt_row if display_index % 2 else self.field)
            self.body.create_rectangle(x1, y1, x2, y2, fill=fill, outline=self.border, tags=(row_tag, f"cell_{display_index}_{col_index}"))
            val = row[col_index]
            text = "NULL" if val is None else str(val)
            self.body.create_text(x1 + 8, (y1 + y2) / 2, text=text, fill=self.placeholder if val is None else self.fg, anchor="w", font=("Segoe UI", 12, "italic" if val is None else "normal"), tags=(row_tag, f"cell_txt_{display_index}_{col_index}"))

    def apply_filters(self):
        if not self.rows: self.filtered_indices = []; self._draw_body(); return
        needles = [var.get().strip().casefold() for var in self.filter_vars]
        result = []
        for row_index, row in enumerate(self.rows):
            if all(not needle or needle in ("null" if row[c] is None else str(row[c])).casefold() for c, needle in enumerate(needles)):
                result.append(row_index)
        self.filtered_indices = result
        self._draw_body(); self._update_info()

    def _body_click(self, event):
        x, y = self.body.canvasx(event.x), self.body.canvasy(event.y)
        if y < 0: return
        display_index = int(y // self.ROW_HEIGHT)
        if display_index < 0 or display_index >= len(self.filtered_indices): return
        row_index = self.filtered_indices[display_index]
        if x <= self.CHECKBOX_WIDTH:
            if row_index in self.selected_rows: self.selected_rows.remove(row_index)
            else: self.selected_rows.add(row_index)
            self._draw_single_row_graphics(display_index)
            self._update_info()

    def _body_double_click(self, event):
        x, y = self.body.canvasx(event.x), self.body.canvasy(event.y)
        if x <= self.CHECKBOX_WIDTH: return
        display_index = int(y // self.ROW_HEIGHT)
        if display_index < 0 or display_index >= len(self.filtered_indices): return
        row_index = self.filtered_indices[display_index]
        for col_index, (x1, x2) in enumerate(self._x_positions()):
            if x1 <= x < x2:
                val = self.rows[row_index][col_index]
                self.clipboard_clear(); self.clipboard_append("NULL" if val is None else str(val)); self.update()
                self.status_var.set(self._get_txt("copied_cell")); return

    def _header_event_x(self, event): return self.header.canvasx(event.x_root - self.header.winfo_rootx())

    def _header_click(self, event):
        x, y = self._header_event_x(event), self.header.canvasy(event.y)
        if y > self.HEADER_TOP: return
        for index, (x1, x2) in enumerate(self._x_positions()):
            if x1 <= x < min(x1 + self.CHECKBOX_WIDTH, x2):
                if index in self.selected_columns: self.selected_columns.remove(index)
                else: self.selected_columns.add(index)
                self._update_header_checkboxes()
                self._update_column_selection_highlights(index)
                self._update_info()
                return

    def _header_press(self, event):
        x = self._header_event_x(event)
        for index, (_, x2) in enumerate(self._x_positions()):
            if abs(x - x2) <= 7:
                self.resize_column, self.resize_start_x, self.resize_start_width = index, x, self.column_widths[index]
                self.resize_guide = self.header.create_line(x2, 0, x2, self.HEADER_HEIGHT, fill=self.fg, width=2, tags=("resize_guide",))
                self.header.configure(cursor="sb_h_double_arrow"); return
        self.resize_column = None; self.header.configure(cursor="")

    def _header_drag(self, event):
        if self.resize_column is None: return
        x = self._header_event_x(event)
        new_width = max(self.MIN_COL_WIDTH, min(self.MAX_COL_WIDTH, self.resize_start_width + (x - self.resize_start_x)))
        x1, _ = self._x_positions()[self.resize_column]
        self.header.coords(self.resize_guide, x1 + new_width, 0, x1 + new_width, self.HEADER_HEIGHT)

    def _header_release(self, event):
        if self.resize_column is None: return
        x = self._header_event_x(event)
        self.column_widths[self.resize_column] = int(max(self.MIN_COL_WIDTH, min(self.MAX_COL_WIDTH, self.resize_start_width + (x - self.resize_start_x))))
        try: self.header.delete(self.resize_guide)
        except: pass
        self.resize_column, self.resize_start_x, self.resize_start_width, self.resize_guide = None, None, None, None
        self.header.configure(cursor="")
        
        self._draw_header()
        total = len(self.filtered_indices)
        batch_size = 50
        def redraw_batch(start_idx):
            end_idx = min(start_idx + batch_size, total)
            for d_idx in range(start_idx, end_idx):
                self._draw_single_row_graphics(d_idx)
            if end_idx < total:
                self.after(5, lambda: redraw_batch(end_idx))
        redraw_batch(0)

    def _hscroll(self, *args): self.header.xview(*args); self.body.xview(*args)
    def _body_xscroll(self, f, l): self.hbar.set(f, l); self.header.xview_moveto(f)
    def _vscroll(self, *args): self.body.yview(*args)
    def _wheel(self, e):
        if self.body.winfo_height() <= 1: return "break"
        amt = int(-e.delta / 120) if e.delta != 0 else (1 if e.delta < 0 else -1)
        self.body.yview_scroll(amt, "units"); return "break"

    def toggle_all_rows(self):
        visible = set(self.filtered_indices)
        if not visible: return
        if visible.issubset(self.selected_rows): self.selected_rows.difference_update(visible)
        else: self.selected_rows.update(visible)
        self._draw_body(); self._update_info()

    def toggle_all_columns(self):
        all_cols = set(range(len(self.columns)))
        if not all_cols: return
        self.selected_columns = set() if self.selected_columns == all_cols else set(all_cols)
        self._update_header_checkboxes()
        self._draw_body()
        self._update_info()

    def _get_strictly_selected_rows(self):
        return [i for i in self.filtered_indices if i in self.selected_rows]

    def _clipboard_text(self, row_indices):
        selected_cols = sorted(self.selected_columns)
        if not selected_cols: return ""
        lines = ["\t".join(self.columns[col] for col in selected_cols)]
        for r_idx in row_indices:
            lines.append("\t".join("NULL" if self.rows[r_idx][c] is None else str(self.rows[r_idx][c]) for c in selected_cols))
        return "\n".join(lines)

    def copy_selection(self):
        visible_selected = self._get_strictly_selected_rows()
        if not visible_selected: 
            messagebox.showinfo(self._get_txt("no_rows_sel_title"), self._get_txt("no_rows_sel_msg"))
            return
        if not self.selected_columns: 
            messagebox.showinfo(self._get_txt("no_cols_sel_title"), self._get_txt("no_cols_sel_msg"))
            return
        
        clip_data = self._clipboard_text(visible_selected)
        if not clip_data: return
        self.clipboard_clear(); self.clipboard_append(clip_data); self.update()
        self.status_var.set(self._get_txt("copied_status", rows=len(visible_selected), cols=len(self.selected_columns)))

    def export_selection(self):
        visible_selected = self._get_strictly_selected_rows()
        if not visible_selected: 
            messagebox.showinfo(self._get_txt("no_rows_sel_title"), self._get_txt("no_rows_sel_msg"))
            return
        if not self.selected_columns: 
            messagebox.showinfo(self._get_txt("no_cols_sel_title"), self._get_txt("no_cols_sel_msg"))
            return

        path = filedialog.asksaveasfilename(
            title="Exportieren", 
            defaultextension=".csv", 
            filetypes=[("CSV-Datei (*.csv)", "*.csv"), ("Excel-Tabelle (*.xls)", "*.xls")]
        )
        if not path: return

        try:
            selected_cols = sorted(self.selected_columns)
            sep = "\t" if path.lower().endswith(".xls") else ";"

            with open(path, "w", encoding="utf-8-sig") as f:
                header_line = sep.join('="' + str(self.columns[col]).replace('"', '""') + '"' for col in selected_cols)
                f.write(header_line + "\n")

                for r_idx in visible_selected:
                    row_data = self.rows[r_idx]
                    row_cells = []
                    for c in selected_cols:
                        val = row_data[c]
                        cell_str = "NULL" if val is None else str(val)
                        row_cells.append('="' + cell_str.replace('"', '""') + '"')
                    f.write(sep.join(row_cells) + "\n")

            self.status_var.set(self._get_txt("export_success", filename=os.path.basename(path)))
        except Exception as exc: 
            messagebox.showerror("Export Fehler", str(exc))

    def _update_info(self):
        self.selection_info.set(self._get_txt("selection_info", rows=len(self.selected_rows), cols=len(self.selected_columns), total_cols=len(self.columns)))
        visible = set(self.filtered_indices)
        self.rows_toggle.configure(text=("☑ " if (bool(visible) and visible.issubset(self.selected_rows)) else "☐ ") + self._get_txt("all_rows"))
        self.columns_toggle.configure(text=("☑ " if (bool(self.columns) and len(self.selected_columns) == len(self.columns)) else "☐ ") + self._get_txt("all_cols"))
        if self.columns:
            cnt = f"{len(self.rows):,}".replace(",", ".")
            self.status_var.set(self._get_txt("rows_visible", visible=f"{len(self.filtered_indices):,}", total=cnt).replace(",", "."))
            self.info_var.set(self._get_txt("info_str", rows=cnt, cols=len(self.columns)))
        else: self.info_var.set(self._get_txt("no_db"))

    def _close(self):
        try:
            if self.conn: self.conn.close()
        except: pass
        self.destroy()

if __name__ == "__main__":
     SQLiteViewer().mainloop()
