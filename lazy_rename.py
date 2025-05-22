import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import json

CONFIG_FILE = "config.json"
LOG_FILE = "lazy_rename.log"
MAX_FOLDER_ROWS = 10

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def rename_files():
    """Renames files in selected folders based on user settings."""
    try:
        digits_to_trim = int(trim_entry.get())
        logging.info(f"Renaming files with digits_to_trim: {digits_to_trim}")
    except ValueError:
        messagebox.showerror("Error", "Digits to trim must be a number.")
        logging.error("Invalid input for digits to trim.")
        return

    folders = []

    if mode.get() == "manual":
        for entry_row in folder_entries:
            if entry_row["visible"]:
                path = entry_row["entry"].get().strip()
                if os.path.isdir(path):
                    folders.append(path)
                    logging.info(f"Added folder: {path}")

    elif mode.get() == "subfolders":
        if folder_entries[0]["visible"]:
            parent_path = folder_entries[0]["entry"].get().strip()
            if os.path.isdir(parent_path):
                for name in os.listdir(parent_path):
                    subfolder = os.path.join(parent_path, name)
                    if os.path.isdir(subfolder):
                        folders.append(subfolder)
                        logging.info(f"Added subfolder: {subfolder}")

    if not folders:
        messagebox.showerror("Error", "No valid folders selected.")
        logging.warning("No valid folders were selected for renaming.")
        return

    total_renamed = 0

    for folder in folders:
        logging.info(f"Processing folder: {folder}")
        files_renamed_in_folder = 0
        files = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))

        counter = 1  # Start counter at 1 for each folder
        for fname in files:
            name, ext = os.path.splitext(fname)
            if len(name) < digits_to_trim:
                logging.debug(f"Skipping file {fname}: Name too short.")
                continue

            base = name[:-digits_to_trim]
            new_name = f"{base}.{str(counter).zfill(4)}{ext}"
            dst = os.path.join(folder, new_name)
            src = os.path.join(folder, fname)

            try:
                os.rename(src, dst)
                total_renamed += 1
                files_renamed_in_folder += 1
                logging.debug(f"Renamed {fname} to {new_name}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not rename {fname}: {e}")
                logging.error(f"Could not rename {fname}: {e}")
                break  # Stop processing if a rename fails
            counter += 1  # Increment counter for the next file
        logging.info(f"Renamed {files_renamed_in_folder} file(s) in folder: {folder}")

    messagebox.showinfo("Done", f"Renamed {total_renamed} file(s).")
    logging.info(f"Total files renamed: {total_renamed}")


def browse_folder(entry):
    """Opens a folder selection dialog and updates the entry field."""
    folder = filedialog.askdirectory()
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)
        logging.info(f"Folder selected: {folder}")


def create_folder_row(folder_frame):
    """Creates a single row for folder selection."""
    row = ttk.Frame(folder_frame, padding=(5, 2))
    entry = ttk.Entry(row, width=50, style="EntryStyle.TEntry")  # Apply style
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    browse_button = ttk.Button(row, text="...", command=lambda: browse_folder(entry),
                            style="BrowseButtonStyle.TButton")  # Apply style
    browse_button.pack(side=tk.LEFT, padx=(0, 5))
    remove_button = ttk.Button(row, text="X", command=lambda: remove_folder_row(row),
                            style="RemoveButtonStyle.TButton")  # Apply style
    remove_button.pack(side=tk.LEFT)

    row.pack(anchor="w", pady=2, fill=tk.X)
    return {
        "row": row,
        "entry": entry,
        "browse_button": browse_button,
        "remove_button": remove_button,
        "visible": False
    }


def show_folder_rows(folder_entries, num_rows):
    """Shows the specified number of folder rows and hides the rest."""
    for i, entry_row in enumerate(folder_entries):
        if i < num_rows:
            entry_row["row"].pack(anchor="w", pady=2, fill=tk.X)
            entry_row["visible"] = True
        else:
            entry_row["row"].pack_forget()
            entry_row["visible"] = False
    logging.debug(f"Showing {num_rows} folder rows.")


def add_folder_row_to_gui(folder_frame, folder_entries):
    """Adds a new row for folder selection."""
    for entry_row in folder_entries:
        if not entry_row["visible"]:
            entry_row["row"].pack(anchor="w", pady=2, fill=tk.X)
            entry_row["visible"] = True
            logging.debug("Showing an existing folder row.")
            return
    logging.warning("Maximum number of folder rows reached.")
    messagebox.showwarning("Warning", "Maximum number of folder rows reached.")


def remove_folder_row(row_to_remove):
    """Removes a folder selection row."""
    for entry_row in folder_entries:
        if entry_row["row"] == row_to_remove:
            entry_row["row"].pack_forget()
            entry_row["visible"] = False
            entry_row["entry"].delete(0, tk.END)
            logging.debug("Hiding a folder row.")
            break


def switch_mode(mode, folder_entries, folder_frame):
    """Switches between manual folder selection and subfolder processing mode."""
    if mode.get() == "manual":
        show_folder_rows(folder_entries, 1)
        logging.info("Switched to manual folder selection mode.")
    else:
        show_folder_rows(folder_entries, 1)
        logging.info("Switched to subfolders processing mode.")


def save_config(mode, folder_entries, trim_entry):
    """Saves the current settings to a JSON file."""
    config = {
        "mode": mode.get(),
        "folders": [entry_row["entry"].get() for entry_row in folder_entries if entry_row["visible"]],
        "digits_to_trim": trim_entry.get()
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        logging.info("Config saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config: {e}")
        logging.error(f"Error saving config: {e}")


def load_config(mode, folder_entries, folder_frame, trim_entry):
    """Loads settings from a JSON file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        mode.set(config.get("mode", "manual"))
        switch_mode(mode, folder_entries, folder_frame)
        saved_folders = config.get("folders", [])
        for i, path in enumerate(saved_folders):
            if i < len(folder_entries):
                folder_entries[i]["entry"].insert(0, path)
                show_folder_rows(folder_entries, i + 1)
        trim_entry.delete(0, tk.END)
        trim_entry.insert(0, config.get("digits_to_trim", "4"))
        logging.info("Config loaded successfully.")
    except FileNotFoundError:
        logging.info("Config file not found. Using default settings.")
        pass
    except Exception as e:
        messagebox.showerror("Error", f"Could not load config: {e}")
        logging.error(f"Error loading config: {e}")


def on_closing(root, mode, folder_entries, trim_entry):
    """Handles the window closing event."""
    save_config(mode, folder_entries, trim_entry)
    root.destroy()
    logging.info("Application closed.")


if __name__ == "__main__":
    # --- GUI SETUP ---
    root = tk.Tk()
    root.title("Lazy Rename")
    root.resizable(False, False)

    # Apply a themed style (if available)
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except tk.TclError:
        logging.warning("Could not set 'clam' theme. Using default.")

    # Define styles
    style.configure("LabelStyle.TLabel", font=("TkDefaultFont", 10))
    style.configure("EntryStyle.TEntry", font=("TkFixedFont", 10))
    style.configure("BrowseButtonStyle.TButton", font=("TkDefaultFont", 9))
    style.configure("RemoveButtonStyle.TButton", font=("TkDefaultFont", 9))
    style.configure("TRadiobutton", font=("TkDefaultFont", 10))  # Style for Radiobuttons

    mode = tk.StringVar(value="manual")
    folder_entries = []

    # Mode selection frame
    mode_frame = ttk.Frame(root, padding=10)
    mode_frame.pack(anchor="w", fill=tk.X)

    ttk.Label(mode_frame, text="Mode:", style="LabelStyle.TLabel").pack(side=tk.LEFT, padx=(0, 10))
    ttk.Radiobutton(mode_frame, text="Select folders manually", variable=mode, value="manual",
                    command=lambda: switch_mode(mode, folder_entries, folder_frame),
                    style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 10))
    ttk.Radiobutton(mode_frame, text="Process all subfolders", variable=mode, value="subfolders",
                    command=lambda: switch_mode(mode, folder_entries, folder_frame),
                    style="TRadiobutton").pack(side=tk.LEFT)

    # Folder frame
    folder_frame = ttk.Frame(root, padding=10)
    folder_frame.pack(fill=tk.X, expand=True)

    # Create all folder rows initially but hide them
    for _ in range(MAX_FOLDER_ROWS):
        folder_entries.append(create_folder_row(folder_frame))

    show_folder_rows(folder_entries, 1)
    add_folder_button = ttk.Button(root, text="+ Add folder",
                                command=lambda: add_folder_row_to_gui(folder_frame, folder_entries),
                                style="BrowseButtonStyle.TButton")
    add_folder_button.pack(anchor="w", padx=10, pady=(0, 10))

    # Trim frame
    trim_frame = ttk.Frame(root, padding=10)
    trim_frame.pack(anchor="w", fill=tk.X)

    ttk.Label(trim_frame, text="Digits to trim:", style="LabelStyle.TLabel").pack(side=tk.LEFT, padx=(0, 10))
    trim_entry = ttk.Entry(trim_frame, width=5, style="EntryStyle.TEntry")
    trim_entry.insert(0, "4")
    trim_entry.pack(side=tk.LEFT, padx=(0, 10))

    # Rename button
    rename_button = ttk.Button(root, text="Rename files", command=rename_files,
                            style="BrowseButtonStyle.TButton")
    rename_button.pack(pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, mode, folder_entries, trim_entry))

    load_config(mode, folder_entries, folder_frame, trim_entry)

    root.mainloop()