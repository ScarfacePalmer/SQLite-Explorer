
# SQLite-Explorer

An SQLite database and SQL dump explorer developed with Python, CustomTkinter, and SQLite.

---

## Features

* **Open Databases & SQL Dumps**: Supports standard SQLite files (`.db`, `.sqlite`, `.sqlite3`) in read-only mode as well as `.sql` dumps (automatically loaded into an in-memory database).
* **Dynamic Column and Row Selection**: 
  * Select individual rows or columns via click / checkbox.
  * Global toggles ("All Rows" / "All Columns") to quickly mark the entire dataset.
* **Real-time Filters & Search**: 
  * Column-specific filters to search individual data fields directly.
  * Global search bar for the entire dataset.
* **Convenient Data Interaction**:
  * **Copy**: Double-clicking a cell copies its content directly to the clipboard.
  * **Export**: Flexibly export selected data as CSV, an Excel-compatible table (`.xls`), or a new SQLite database (`.db`).
* **UI**: **German (DE)** / **English (EN)** and **Light** / **Dark** mode via dropdown.

---

## Controls

* **Double-click on a cell**: Copies the respective cell content to the clipboard.
* **Column Header**: 
  * Click to select the column for export/copying.
  * Filter in one or more columns.
  * Drag the edge of the column header to adjust the column width.

---

## Requirements

* Python
* CustomTkinter, Pillow
```bash
pip install customtkinter pillow
```

### Run as Python Script
```bash
python sql-explorer.py
```


---

## License
This project is open source and licensed under the MIT License.

Developed by **https://buymeacoffee.com/scarfacepalmer**

---
---


# SQLite-Explorer

Ein SQLite-Datenbank- und SQL-Dump-Explorer, entwickelt mit Python, CustomTkinter und SQLite.

---

## Funktionen

* **Datenbanken & SQL-Dumps öffnen**: Unterstützt Standard-SQLite-Dateien (`.db`, `.sqlite`, `.sqlite3`) im Read-Only-Modus sowie `.sql`-Dumps (wird automatisch in eine In-Memory-Datenbank geladen).
* **Dynamische Spalten- und Zeilenauswahl**: 
  * Einzelne Zeilen oder Spalten per Klick / Checkbox auswählen.
  * Globale Umschalter („Alle Zeilen“ / „Alle Spalten“) zum schnellen Markieren des gesamten Bestands.
* **Echtzeit-Filter & Suche**: 
  * Spaltenspezifische Filter zum direkten Durchsuchen einzelner Datenfelder.
  * Globale Suchleiste für das gesamte Dataset.
* **Komfortable Dateninteraktion**:
  * **Kopieren**: Per Doppelklick auf eine Zelle wird der Inhalt direkt in die Zwischenablage kopiert.
  * **Export**: Exportiere ausgewählte Daten flexibel als CSV, Excel-kompatible Tabelle (`.xls`) oder neue SQLite-Datenbank (`.db`).
* **UI**: **Deutsch (DE)** / **Englisch (EN)** und **Light** / **Dark** -Mode per Dropdown.

---

## Steuerung

* **Doppelklick auf eine Zelle**: Kopiert den jeweiligen Zellinhalt in die Zwischenablage.
* **Spalten-Header**: 
  * Anklicken, um die Spalte für Export/Kopieren zu markieren.
  * Filtern in einer oder mehreren Spalten.
  * Am Rand des Spaltenkopfes ziehen, um die Spaltenbreite anzupassen.

---

## Voraussetzungen

* Python
* CustomTkinter, Pillow
```bash
pip install customtkinter pillow
```

### Ausführen als Python-Skript
```bash
python sql-explorer.py
```


---

## Lizenz
Dieses Projekt ist Open Source und steht unter der MIT-Lizenz.

Entwickelt von **https://buymeacoffee.com/scarfacepalmer**
