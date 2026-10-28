#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class SQLiteViewer(ctk.CTk):
    ROW_HEIGHT = 35  
    HEADER_TOP = 35  # Etwas mehr Platz für die größere Schrift
    HEADER_HEIGHT = 70  # Gesamthöhe des Headers angepasst
    CHECKBOX_WIDTH = 48
    MIN_COL_WIDTH = 85
    MAX_COL_WIDTH = 500

    def __init__(self):
        super().__init__()
        self.title("SQLite-Explorer by ScarfacePalmer")
        self.geometry("1500x880")
        self.minsize(950, 550)

        self.state("zoomed")
        
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "SQLite-Explorer_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Konnte Fenster-Icon nicht laden: {e}")

        self.accent_color = "#008080"
        self.accent_hover = "#006666"

        self.conn, self.db_path = None, None
        self.table_names, self.columns = [], []
        self.total_rows = 0
        self.pk_column = "rowid"
        
        self.selected_row_ids = set()
        self.selected_columns = set()
        self.filter_vars, self.filter_entries, self.column_widths = [], [], {}
        self.is_search_placeholder_active = True

        self.bg, self.panel, self.fg, self.field, self.filter_field = "#1d1e22", "#2d2f34", "#f5f7fa", "#141517", "#2d2f34"
        self.border, self.header_bg, self.selected_bg, self.placeholder, self.alt_row = "#3f454d", "#25262a", "#004d4d", "#aeb6c1", "#1a1b1e"

        self.current_lang = "DE"
        self.translations = {
            "DE": {
                "open_db": "📂 Datenbank öffnen", "open_sql": "📄 SQL-Dump öffnen",
                "table_lbl": "Tabelle:", "refresh": "⟳ Aktualisieren", "all_rows": "Alle Zeilen",
                "all_cols": "Alle Spalten", "copy_sel": "📋 Auswahl kopieren", "export_sel": "📊 Exportieren",
                "ready": "Bereit", "db_dialog_title": "SQLite-Datenbank öffnen", "db_types": "SQLite Datenbanken",
                "all_files": "Alle Dateien", "sql_dialog_title": "SQLite SQL-Dump öffnen", "sql_types": "SQL-Dumps",
                "open_err": "Datenbank konnte nicht geöffnet werden", "sql_err": "SQL-Dump konnte nicht geladen werden",
                "sql_decode_err": "Der SQL-Dump konnte nicht als Text gelesen werden.", "no_tables_title": "Keine Tabellen",
                "no_tables_msg": "Keine normalen SQLite-Tabellen gefunden.", "load_table_err": "Tabelle konnte nicht geladen werden",
                "filter_placeholder": "Filtern", 
                "copied_cell": "Zelleninhalt in die Zwischenablage kopiert", "no_rows_sel_title": "Keine Zeilen ausgewählt",
                "no_rows_sel_msg": "Bitte mindestens eine Zeile auswählen.", "no_cols_sel_title": "Keine Spalten ausgewählt",
                "no_cols_sel_msg": "Bitte mindestens eine Spalte auswählen.", "no_visible_title": "Keine sichtbaren Zeilen",
                "no_visible_msg": "Die ausgewählten Zeilen werden aktuell vom Filter ausgeblendet.",
                "copied_status": "{rows} Zeilen × {cols} Spalten kopiert", "export_success": "Erfolgreich exportiert nach {filename}",
                "info_str": "{rows} Zeilen · {cols} Spalten", "no_db": "Keine Datenbank geöffnet",
                "selection_info": "Zeilen: {rows}   Spalten: {cols}/{total_cols}",
                "status_selection": "Auswahl: {vals} Werte ({rows} Zeilen × {cols} Spalten)",
                "status_ready": "Bereit", "status_nodb": "Keine Datenbank geöffnet",
                "search_ph": "Suche", "reset_filter": "↺ Filter zurücksetzen"
            },
            "EN": {
                "open_db": "📂 Open Database", "open_sql": "📄 Open SQL Dump",
                "table_lbl": "Table:", "refresh": "⟳ Refresh", "all_rows": "All Rows",
                "all_cols": "All Columns", "copy_sel": "📋 Copy Selection", "export_sel": "📊 Export Selection",
                "ready": "Ready", "db_dialog_title": "Open SQLite Database", "db_types": "SQLite Databases",
                "all_files": "All Files", "sql_dialog_title": "Open SQLite SQL Dump", "sql_types": "SQL Dumps",
                "open_err": "Database could not be opened", "sql_err": "SQL Dump could not be loaded",
                "sql_decode_err": "The SQL dump could not be read as text.", "no_tables_title": "No Tables",
                "no_tables_msg": "No normal SQLite tables found.", "load_table_err": "Table could not be loaded",
                "filter_placeholder": "Filter", 
                "copied_cell": "Cell content copied to clipboard", "no_rows_sel_title": "No rows selected",
                "no_rows_sel_msg": "Please select at least one row.", "no_cols_sel_title": "No columns selected",
                "no_cols_sel_msg": "Please select at least one column.", "no_visible_title": "No visible rows",
                "no_visible_msg": "The selected rows are currently hidden by the filter.",
                "copied_status": "{rows} rows × {cols} columns copied", "export_success": "Successfully exported to {filename}",
                "info_str": "{rows} rows · {cols} columns", "no_db": "No database opened",
                "selection_info": "Rows: {rows}   Columns: {cols}/{total_cols}",
                "status_selection": "Selection: {vals} values ({rows} rows × {cols} columns)",
                "status_ready": "Ready", "status_nodb": "No database opened",
                "search_ph": "Search", "reset_filter": "↺ Reset Filter"
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
        self.table_combo = ctk.CTkComboBox(self.toolbar, variable=self.table_var, state="readonly", width=220, command=self.table_changed)
        self.table_combo.pack(side="left", padx=5, pady=8)

        self.btn_refresh = ctk.CTkButton(self.toolbar, text=self._get_txt("refresh"), command=self.refresh, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color)
        self.btn_refresh.pack(side="left", padx=5, pady=8)

        self.lang_var = tk.StringVar(value="DE")
        self.lang_combo = ctk.CTkComboBox(self.toolbar, values=["DE", "EN"], variable=self.lang_var, state="readonly", width=70, command=self._change_language)
        self.lang_combo.pack(side="right", padx=(5, 15), pady=8)

        self.btn_theme_toggle = ctk.CTkButton(self.toolbar, text="⚬" if ctk.get_appearance_mode() == "Light" else "☀", width=40, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color, command=self.toggle_appearance_mode)
        self.btn_theme_toggle.pack(side="right", padx=5, pady=8)

        self.lbl_info = ctk.CTkLabel(self.toolbar, text="") 
        self.info_var = tk.StringVar(value=self._get_txt("no_db"))
        self.lbl_info.configure(textvariable=self.info_var)
        self.lbl_info.pack(side="right", padx=(10, 10))

        self.selection_bar = ctk.CTkFrame(self, corner_radius=0, height=45)
        self.selection_bar.pack(fill="x", side="top", pady=(2, 0))

        self.rows_toggle = ctk.CTkButton(self.selection_bar, text="☐ " + self._get_txt("all_rows"), command=self.toggle_all_rows, width=110, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=("#b0b0b0", "#555555"))
        self.rows_toggle.pack(side="left", padx=(10, 8), pady=6)

        self.columns_toggle = ctk.CTkButton(self.selection_bar, text="☐ " + self._get_txt("all_cols"), command=self.toggle_all_columns, width=110, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=("#b0b0b0", "#555555"))
        self.columns_toggle.pack(side="left", pady=6)

        self.global_search_var = tk.StringVar()
        self.global_search_var.trace_add("write", lambda *args: self._on_search_change())
        self.search_entry = ctk.CTkEntry(self.selection_bar, textvariable=self.global_search_var, width=240)
        self.search_entry.pack(side="left", padx=(15, 5), pady=6)
        
        self.btn_reset_filter = ctk.CTkButton(self.selection_bar, text=self._get_txt("reset_filter"), command=self.reset_all_filters, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=("#b0b0b0", "#555555"), width=130)
        self.btn_reset_filter.pack(side="left", padx=5, pady=6)

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

        self.status_var = tk.StringVar(value=self._get_txt("status_ready"))
        self.lbl_status = ctk.CTkLabel(self.status_frame, textvariable=self.status_var, anchor="w")
        self.lbl_status.pack(side="left", fill="x", expand=True)

        self.btn_export_sel = ctk.CTkButton(self.status_frame, text=self._get_txt("export_sel"), command=self.export_selection, fg_color=("#e0e0e0", "#3a3a3a"), text_color=("#1a1a1a", "#ffffff"), border_width=1, border_color=self.accent_color, width=140)
        self.btn_export_sel.pack(side="right", padx=(10, 0))

        self.btn_copy_sel = ctk.CTkButton(self.status_frame, text=self._get_txt("copy_sel"), command=self.copy_selection, fg_color=self.accent_color, hover_color=self.accent_hover, width=160)
        self.btn_copy_sel.pack(side="right", padx=(10, 0))

        self._apply_search_placeholder()

    def _apply_search_placeholder(self):
        ph = self._get_txt("search_ph")
        self.is_search_placeholder_active = True
        self.global_search_var.set(ph)
        self.search_entry.configure(text_color=self.placeholder, font=("Segoe UI", 11, "italic"))

        def focus_in(e):
            if self.is_search_placeholder_active:
                self.is_search_placeholder_active = False
                self.global_search_var.set("")
                self.search_entry.configure(text_color=self.fg, font=("Segoe UI", 11, "normal"))

        def focus_out(e):
            if not self.global_search_var.get().strip():
                self.is_search_placeholder_active = True
                self.global_search_var.set(self._get_txt("search_ph"))
                self.search_entry.configure(text_color=self.placeholder, font=("Segoe UI", 11, "italic"))

        self.search_entry.bind("<FocusIn>", focus_in, add="+")
        self.search_entry.bind("<FocusOut>", focus_out, add="+")

    def _on_search_change(self):
        if self.is_search_placeholder_active:
            return
        self._refresh_view()

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
        self.btn_open_db.configure(text=self._get_txt("open_db"))
        self.btn_open_sql.configure(text=self._get_txt("open_sql"))
        self.lbl_table.configure(text=self._get_txt("table_lbl"))
        self.btn_refresh.configure(text=self._get_txt("refresh"))
        self.btn_copy_sel.configure(text=self._get_txt("copy_sel"))
        self.btn_export_sel.configure(text=self._get_txt("export_sel"))
        self.btn_reset_filter.configure(text=self._get_txt("reset_filter"))
        
        chk_r = "☑" if self.selected_row_ids else "☐"
        chk_c = "☑" if self.selected_columns else "☐"
        self.rows_toggle.configure(text=chk_r + " " + self._get_txt("all_rows"))
        self.columns_toggle.configure(text=chk_c + " " + self._get_txt("all_cols"))
        
        if self.is_search_placeholder_active:
            self._apply_search_placeholder()

        if self.columns: 
            self._draw_header()
            self._refresh_view()
        else: 
            self.status_var.set(self._get_txt("status_ready"))
        self._update_info()

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
        if self.columns:
            self._draw_header()
        self._redraw_visible_viewport()
        if self.is_search_placeholder_active:
            self.search_entry.configure(text_color=self.placeholder)

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
            self.table_var.set(""); self.columns = []
            self._draw_header(); self._redraw_visible_viewport()
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
            self.current_table = table_name
            qname = '"' + table_name.replace('"', '""') + '"'
            cur = self.conn.cursor()
            
            info = cur.execute(f"PRAGMA table_info({qname})").fetchall()
            self.columns = [row[1] for row in info]
            
            pk_cols = [row[1] for row in info if row[5] > 0]
            self.pk_column = pk_cols[0] if pk_cols else "rowid"

            self.selected_row_ids.clear()
            self.selected_columns.clear()
            self.filter_vars = [tk.StringVar(value="") for _ in self.columns]
            self.filter_entries = []
            
            self._apply_search_placeholder()

            sample_rows = cur.execute(f"SELECT * FROM {qname} LIMIT 50").fetchall()
            self.column_widths = {i: self._initial_width(i, sample_rows) for i in range(len(self.columns))}
            
            self._draw_header()
            self._refresh_view()
        except Exception as exc: 
            messagebox.showerror(self._get_txt("load_table_err"), str(exc))

    def _initial_width(self, index, sample_rows):
        longest = len(self.columns[index])
        for row in sample_rows:
            longest = max(longest, len("NULL" if row[index] is None else str(row[index])))
        return max(self.MIN_COL_WIDTH, min(self.MAX_COL_WIDTH, longest * 9 + 35))

    def reset_all_filters(self):
        self._apply_search_placeholder()
        for var in self.filter_vars:
            var.set("")
        self._draw_header()
        self._refresh_view()

    def _build_query(self, count_only=False):
        qname = '"' + self.current_table.replace('"', '""') + '"'
        clauses = []
        params = []
        
        for i, var in enumerate(self.filter_vars):
            val = var.get().strip()
            if val:
                clauses.append(f'CAST("{self.columns[i]}" AS TEXT) LIKE ?')
                params.append(f"%{val}%")

        if not self.is_search_placeholder_active:
            global_val = self.global_search_var.get().strip()
            if global_val:
                global_clauses = [f'CAST("{col}" AS TEXT) LIKE ?' for col in self.columns]
                clauses.append("(" + " OR ".join(global_clauses) + ")")
                params.extend([f"%{global_val}%"] * len(self.columns))
                
        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        
        if count_only:
            sql = f"SELECT COUNT(*) FROM {qname} {where_sql}"
        else:
            pk_sel = self.pk_column if self.pk_column in self.columns else f'rowid AS "{self.pk_column}"'
            sql = f"SELECT {pk_sel}, * FROM {qname} {where_sql}"
        return sql, params

    def _refresh_view(self):
        if not self.columns: return
        cur = self.conn.cursor()
        count_sql, params = self._build_query(count_only=True)
        self.total_rows = cur.execute(count_sql, params).fetchone()[0]
        
        self._redraw_visible_viewport()
        self._update_info()

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
        
        # Größeres Häkchen / Auswahlbox
        self.header.create_text(x + self.CHECKBOX_WIDTH / 2, self.HEADER_TOP / 2, text=checkbox, fill=self.accent_color if checkbox == "☑" else self.fg, anchor="center", font=("Segoe UI Symbol", 18), tags=(f"header_col_{col_index}", f"header_cb_{col_index}"))
        
        # Größerer Spaltenname (Schriftgröße 13 statt 11, fett)
        self.header.create_text(x + self.CHECKBOX_WIDTH + 6, self.HEADER_TOP / 2, text=title, fill=self.fg, anchor="w", font=("Segoe UI", 13, "bold"))
        
        self.header.create_rectangle(x, self.HEADER_TOP, x + width, self.HEADER_HEIGHT, fill=self.header_bg, outline=self.border)
        
        # Größeres Filter-Eingabefeld (Schriftgröße 12 statt 10)
        entry = tk.Entry(self.header, relief="flat", bd=0, bg=self.filter_field, fg=self.placeholder, insertbackground=self.fg, selectbackground=self.selected_bg, font=("Segoe UI", 12, "italic"))
        
        current_val = self.filter_vars[col_index].get()
        if current_val:
            entry.delete(0, "end")
            entry.insert(0, current_val)
            entry.configure(fg=self.fg, font=("Segoe UI", 12, "normal"))
        else:
            entry.insert(0, self._get_txt("filter_placeholder"))

        def focus_in(_e):
            if entry.get() == self._get_txt("filter_placeholder"): 
                entry.delete(0, "end")
                entry.configure(fg=self.fg, font=("Segoe UI", 12, "normal"))

        def focus_out(_e, idx=col_index):
            if not entry.get().strip() or entry.get() == self._get_txt("filter_placeholder"): 
                entry.delete(0, "end")
                entry.insert(0, self._get_txt("filter_placeholder"))
                entry.configure(fg=self.placeholder, font=("Segoe UI", 12, "italic"))
                self.filter_vars[idx].set("")
            else: 
                self.filter_vars[idx].set(entry.get())
            self._refresh_view()

        def key_release(_e, idx=col_index):
            val = entry.get()
            if val == self._get_txt("filter_placeholder"):
                self.filter_vars[idx].set("")
            else:
                self.filter_vars[idx].set(val)
            self._refresh_view()

        entry.bind("<FocusIn>", focus_in); entry.bind("<FocusOut>", focus_out); entry.bind("<KeyRelease>", key_release)
        entry.bind("<ButtonPress-1>", self._header_press, add="+"); entry.bind("<B1-Motion>", self._header_drag, add="+"); entry.bind("<ButtonRelease-1>", self._header_release, add="+")
        
        # Eingabefeld in der Höhe an die neue Header-Größe angepasst (30px hoch)
        self.header.create_window(x + 5, self.HEADER_TOP + 3, window=entry, width=max(30, width - 10), height=30, anchor="nw")
        self.filter_entries.append(entry)

    def _update_header_checkboxes(self):
        for i in range(len(self.columns)):
            checkbox = "☑" if i in self.selected_columns else "☐"
            tag = f"header_cb_{i}"
            self.header.itemconfig(tag, text=checkbox, fill=self.accent_color if checkbox == "☑" else self.fg)

    def _redraw_visible_viewport(self):
        self.body.delete("all")
        if not self.columns: 
            self.body.configure(scrollregion=(0, 0, 1, 1))
            return

        total_height = max(1, self.total_rows * self.ROW_HEIGHT)
        self.body.configure(scrollregion=(0, 0, self._total_width(), total_height))

        v_top = self.body.canvasy(0)
        v_height = self.body.winfo_height()
        
        start_row = max(0, int(v_top // self.ROW_HEIGHT) - 5)
        end_row = min(self.total_rows, int((v_top + v_height) // self.ROW_HEIGHT) + 10)

        if start_row >= end_row: return

        sql, params = self._build_query(count_only=False)
        sql += f" LIMIT {end_row - start_row} OFFSET {start_row}"
        
        cur = self.conn.cursor()
        rows = cur.execute(sql, params).fetchall()

        positions = self._x_positions()
        for idx, row in enumerate(rows):
            actual_row_idx = start_row + idx
            row_id = row[0]
            row_data = row[1:]
            
            y1 = actual_row_idx * self.ROW_HEIGHT
            y2 = y1 + self.ROW_HEIGHT
            row_tag = f"drow_{actual_row_idx}"
            row_selected = row_id in self.selected_row_ids

            self.body.create_rectangle(0, y1, self.CHECKBOX_WIDTH, y2, fill=self.field, outline=self.border, tags=(row_tag, f"row_cb_{actual_row_idx}"))
            checkbox = "☑" if row_selected else "☐"
            self.body.create_text(self.CHECKBOX_WIDTH / 2, (y1 + y2) / 2, text=checkbox, fill=self.accent_color if row_selected else self.fg, anchor="center", font=("Segoe UI Symbol", 18), tags=(row_tag, f"row_cb_txt_{actual_row_idx}"))

            for col_index, (x1, x2) in enumerate(positions):
                fill = self.selected_bg if (row_selected and col_index in self.selected_columns) else (self.alt_row if actual_row_idx % 2 else self.field)
                self.body.create_rectangle(x1, y1, x2, y2, fill=fill, outline=self.border, tags=(row_tag, f"cell_{actual_row_idx}_{col_index}"))
                val = row_data[col_index]
                text = "NULL" if val is None else str(val)
                self.body.create_text(x1 + 8, (y1 + y2) / 2, text=text, fill=self.placeholder if val is None else self.fg, anchor="w", font=("Segoe UI", 12, "italic" if val is None else "normal"), tags=(row_tag, f"cell_txt_{actual_row_idx}_{col_index}"))

    def _body_click(self, event):
        x, y = self.body.canvasx(event.x), self.body.canvasy(event.y)
        if y < 0: return
        actual_row_idx = int(y // self.ROW_HEIGHT)
        if actual_row_idx < 0 or actual_row_idx >= self.total_rows: return
        
        sql, params = self._build_query(count_only=False)
        sql += f" LIMIT 1 OFFSET {actual_row_idx}"
        cur = self.conn.cursor()
        row = cur.execute(sql, params).fetchone()
        if not row: return
        row_id = row[0]

        if x <= self.CHECKBOX_WIDTH:
            if row_id in self.selected_row_ids: self.selected_row_ids.remove(row_id)
            else: self.selected_row_ids.add(row_id)
            self._redraw_visible_viewport()
            self._update_info()

    def _body_double_click(self, event):
        x, y = self.body.canvasx(event.x), self.body.canvasy(event.y)
        if x <= self.CHECKBOX_WIDTH: return
        actual_row_idx = int(y // self.ROW_HEIGHT)
        if actual_row_idx < 0 or actual_row_idx >= self.total_rows: return
        
        sql, params = self._build_query(count_only=False)
        sql += f" LIMIT 1 OFFSET {actual_row_idx}"
        cur = self.conn.cursor()
        row = cur.execute(sql, params).fetchone()
        if not row: return
        row_data = row[1:]

        for col_index, (x1, x2) in enumerate(self._x_positions()):
            if x1 <= x < x2:
                val = row_data[col_index]
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
                self._redraw_visible_viewport()
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
        self._redraw_visible_viewport()

    def _hscroll(self, *args): self.header.xview(*args); self.body.xview(*args)
    def _body_xscroll(self, f, l): self.hbar.set(f, l); self.header.xview_moveto(f)
    def _vscroll(self, *args): self.body.yview(*args); self._redraw_visible_viewport()
    def _wheel(self, e):
        if self.body.winfo_height() <= 1: return "break"
        amt = int(-e.delta / 120) if e.delta != 0 else (1 if e.delta < 0 else -1)
        self.body.yview_scroll(amt, "units")
        self._redraw_visible_viewport()
        return "break"

    def toggle_all_rows(self):
        if not self.columns: return
        cur = self.conn.cursor()
        pk_sel = self.pk_column if self.pk_column in self.columns else "rowid"
        sql, params = self._build_query(count_only=False)
        sql_ids = f"SELECT {pk_sel} FROM {self.current_table} " + sql.split("FROM")[1]
        all_ids = set(row[0] for row in cur.execute(sql_ids, params).fetchall())

        if all_ids.issubset(self.selected_row_ids):
            self.selected_row_ids.difference_update(all_ids)
            chk = "☐ "
        else:
            self.selected_row_ids.update(all_ids)
            chk = "☑ "
            
        self.rows_toggle.configure(text=chk + self._get_txt("all_rows"))
        self._redraw_visible_viewport()
        self._update_info()

    def toggle_all_columns(self):
        all_cols = set(range(len(self.columns)))
        if not all_cols: return
        if self.selected_columns == all_cols:
            self.selected_columns = set()
            chk = "☐ "
        else:
            self.selected_columns = set(all_cols)
            chk = "☑ "
            
        self.columns_toggle.configure(text=chk + self._get_txt("all_cols"))
        self._update_header_checkboxes()
        self._redraw_visible_viewport()
        self._update_info()

    def _fetch_selected_rows_data(self):
        if not self.selected_row_ids: return []
        cur = self.conn.cursor()
        qname = '"' + self.current_table.replace('"', '""') + '"'
        pk_sel = self.pk_column if self.pk_column in self.columns else "rowid"
        
        id_list = list(self.selected_row_ids)
        all_rows = []
        batch_size = 500  
        
        for i in range(0, len(id_list), batch_size):
            chunk = id_list[i:i + batch_size]
            placeholders = ",".join(["?"] * len(chunk))
            sql = f"SELECT * FROM {qname} WHERE {pk_sel} IN ({placeholders})"
            all_rows.extend(cur.execute(sql, chunk).fetchall())
            
        return all_rows

    def copy_selection(self):
        if not self.selected_row_ids: 
            messagebox.showinfo(self._get_txt("no_rows_sel_title"), self._get_txt("no_rows_sel_msg"))
            return
        if not self.selected_columns: 
            messagebox.showinfo(self._get_txt("no_cols_sel_title"), self._get_txt("no_cols_sel_msg"))
            return
        
        rows = self._fetch_selected_rows_data()
        selected_cols = sorted(self.selected_columns)
        
        lines = ["\t".join(self.columns[col] for col in selected_cols)]
        for row in rows:
            lines.append("\t".join("NULL" if row[col] is None else str(row[col]) for col in selected_cols))
            
        clip_data = "\n".join(lines)
        self.clipboard_clear(); self.clipboard_append(clip_data); self.update()
        self.status_var.set(self._get_txt("copied_status", rows=len(rows), cols=len(selected_cols)))

    def export_selection(self):
        if not self.selected_row_ids: 
            messagebox.showinfo(self._get_txt("no_rows_sel_title"), self._get_txt("no_rows_sel_msg"))
            return
        if not self.selected_columns: 
            messagebox.showinfo(self._get_txt("no_cols_sel_title"), self._get_txt("no_cols_sel_msg"))
            return

        path = filedialog.asksaveasfilename(
            title="Exportieren", 
            defaultextension=".csv", 
            filetypes=[
                ("CSV-Datei (*.csv)", "*.csv"), 
                ("Excel-Tabelle (*.xls)", "*.xls"),
                ("SQLite Datenbank (*.db)", "*.db")
            ]
        )
        if not path: return

        try:
            rows = self._fetch_selected_rows_data()
            selected_cols = sorted(self.selected_columns)
            ext = os.path.splitext(path)[1].lower()

            if ext == ".db":
                if os.path.exists(path):
                    os.remove(path)
                new_conn = sqlite3.connect(path)
                new_cur = new_conn.cursor()
                
                col_defs = []
                for c in selected_cols:
                    col_defs.append(f'"{self.columns[c]}" TEXT')
                new_cur.execute(f'CREATE TABLE "{self.current_table}" ({", ".join(col_defs)});')
                
                placeholders = ",".join(["?"] * len(selected_cols))
                col_names = ",".join([f'"{self.columns[c]}"' for c in selected_cols])
                insert_sql = f'INSERT INTO "{self.current_table}" ({col_names}) VALUES ({placeholders});'
                
                insert_data = []
                for row in rows:
                    insert_data.append(tuple("NULL" if row[c] is None else row[c] for c in selected_cols))
                    if len(insert_data) >= 1000:
                        new_cur.executemany(insert_sql, insert_data)
                        new_conn.commit()
                        insert_data = []
                if insert_data:
                    new_cur.executemany(insert_sql, insert_data)
                    new_conn.commit()
                    
                new_conn.close()
            else:
                sep = "\t" if ext == ".xls" else ";"
                with open(path, "w", encoding="utf-8-sig") as f:
                    header_line = sep.join('="' + str(self.columns[col]).replace('"', '""') + '"' for col in selected_cols)
                    f.write(header_line + "\n")

                    for row in rows:
                        row_cells = []
                        for c in selected_cols:
                            val = row[c]
                            cell_str = "NULL" if val is None else str(val)
                            row_cells.append('="' + cell_str.replace('"', '""') + '"')
                        f.write(sep.join(row_cells) + "\n")

            self.status_var.set(self._get_txt("export_success", filename=os.path.basename(path)))
        except Exception as exc: 
            messagebox.showerror("Export Fehler", str(exc))

    def _update_info(self):
        self.selection_info.set(self._get_txt("selection_info", rows=len(self.selected_row_ids), cols=len(self.selected_columns), total_cols=len(self.columns)))
        if self.columns:
            sel_rows = len(self.selected_row_ids)
            sel_cols = len(self.selected_columns)
            total_selected_values = sel_rows * sel_cols
            
            self.status_var.set(self._get_txt("status_selection", vals=f"{total_selected_values:,}".replace(",", "."), rows=sel_rows, cols=sel_cols))
            
            cnt = f"{self.total_rows:,}".replace(",", ".")
            self.info_var.set(self._get_txt("info_str", rows=cnt, cols=len(self.columns)))
        else: 
            self.status_var.set(self._get_txt("status_ready"))
            self.info_var.set(self._get_txt("no_db"))

    def _close(self):
        try:
            if self.conn: self.conn.close()
        except: pass
        self.destroy()

if __name__ == "__main__":
    try:
        import pyi_splash
        import time
        time.sleep(3)
        pyi_splash.close()
    except ImportError:
        pass  

    SQLiteViewer().mainloop()
