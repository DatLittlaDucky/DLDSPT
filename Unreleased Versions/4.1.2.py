#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DLDSPT — DatLittlaDucky's Python Tooling
Version: 4.1.2 (stabilized)

This file fixes indentation, import paths, error handling, and UX nits
from the pasted script so it actually runs cross‑platform.
"""
import os
import sys
import runpy
import traceback
import webbrowser
import time
from datetime import datetime
import ast

APP_NAME = "DLDSPT"
APP_FULL_NAME = "DatLittlaDucky's Python Tooling"
DLDSPT_VERSION = "4.1.2"
DISCORD_LINK = "https://discord.gg/JhwNVrb7Kf"

last_ran_mod = None
LOG_FILE = "dldsptrun.log"


# ----------------------------- utils ---------------------------------
def clear_console() -> None:
    """Clear screen on Windows/macOS/Linux; ignore failures (e.g., IDEs)."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def find_mods_folder() -> str | None:
    """Return absolute path to ./Mods if it exists, else None."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    return mods_path if os.path.isdir(mods_path) else None


def _real_path_for_entry(path: str) -> str:
    """If path is a dir, return its __main__.py; else return the file."""
    return path if os.path.isfile(path) else os.path.join(path, "__main__.py")


def get_total_mods_size(entries: list[str]) -> int:
    total = 0
    for f in entries:
        real_path = _real_path_for_entry(f)
        if os.path.exists(real_path):
            total += os.path.getsize(real_path)
    return total // 1024  # KB


def list_mods(mods_path: str, sort_by: str = "name") -> list[str]:
    files: list[str] = []
    for entry in os.listdir(mods_path):
        full_path = os.path.join(mods_path, entry)
        if entry.endswith(".py") and os.path.isfile(full_path):
            files.append(full_path)
        elif entry.endswith(".dkl") and os.path.isfile(full_path):
            files.append(full_path)
        elif os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "__main__.py")):
            files.append(full_path)

    if sort_by == "name":
        return sorted(files, key=lambda f: os.path.basename(f).lower())

    elif sort_by == "date":
        def get_mtime(f: str) -> float:
            return os.path.getmtime(_real_path_for_entry(f))
        return sorted(files, key=get_mtime, reverse=True)

    elif sort_by == "size":
        def get_size(f: str) -> int:
            return os.path.getsize(_real_path_for_entry(f))
        return sorted(files, key=get_size, reverse=True)

    # fallback (shouldn't happen)
    return files


def format_name(path: str) -> str:
    name = os.path.basename(path)
    if os.path.isdir(path):
        name = os.path.basename(path) + " [DIR]"
    elif name.endswith(".py"):
        name = name[:-3] + " [Python]"
    elif name.endswith(".dkl"):
        name = name[:-4] + " [Ducky]"
    return name.replace("-", " ").replace("_", " ")


def get_file_info(path: str) -> str:
    real_path = _real_path_for_entry(path)
    try:
        size = os.path.getsize(real_path)
        mtime = os.path.getmtime(real_path)
        return f"{size // 1024}KB, {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}"
    except OSError:
        return "N/A"


def log_run(mod_name: str, error: str | None = None) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - Running mod: {mod_name}\n")
            if error:
                f.write(f"ERROR:\n{error}\n")
            f.write("\n")
    except Exception:
        # Don't explode if logging fails
        pass


# ----------------------- duckylang integration ------------------------

def _import_duckylang():
    """Import duckylang from either top-level or Mods package.
    Returns the module or raises ImportError.
    """
    try:
        # Prefer top-level (per update #23)
        import duckylang  # type: ignore
        return duckylang
    except Exception:
        pass
    # Fallback to Mods.duckylang
    try:
        import importlib
        return importlib.import_module("Mods.duckylang")  # type: ignore
    except Exception as e:
        raise ImportError(
            "Could not import 'duckylang'. Place 'duckylang.py' next to this file "
            "or as Mods/duckylang.py."
        ) from e


def run_duckylang_script(mods_path: str | None, modname: str | None = None, script_path: str | None = None) -> None:
    if script_path:
        # Directly run the given .dkl file
        try:
            duckylang = _import_duckylang()
            duckylang.run_duckylang(script_path)
        except Exception as e:
            print("Error running DuckyLang:", e)
        input("Press Enter to return to DLDSPT Menu...")
        return

    # Interactive prompt path
    print("\n--- DuckyLang ---")
    if not modname:
        modname = input("Enter DuckyLang mod name (without .dkl): ").strip()
    if not mods_path:
        print("❌ Mods folder not found; cannot locate the .dkl file.")
        input("Press Enter to return to DLDSPT Menu...")
        return

    script_path = os.path.join(mods_path, f"{modname}.dkl")
    if not os.path.isfile(script_path):
        print(f"❌ DuckyLang mod '{modname}' not found at {script_path}.")
        input("Press Enter to return to DLDSPT Menu...")
        return

    try:
        duckylang = _import_duckylang()
        duckylang.run_duckylang(script_path)
    except Exception as e:
        print("Error running DuckyLang:", e)
    input("Press Enter to return to DLDSPT Menu...")


# ------------------------- python runner ------------------------------

def run_script(path: str) -> None:
    global last_ran_mod
    mod_name = format_name(path)
    last_ran_mod = mod_name
    print(f"\n--- Running {mod_name} ---\n")

    # If it's a .dkl file, run via DuckyLang
    if os.path.isfile(path) and path.endswith(".dkl"):
        run_duckylang_script(None, None, script_path=path)
        return

    try:
        if os.path.isdir(path):
            runpy.run_path(os.path.join(path, "__main__.py"), run_name="__main__")
        else:
            runpy.run_path(path, run_name="__main__")
        log_run(mod_name)
    except SystemExit:
        # allow scripts to call sys.exit without dumping a traceback
        log_run(mod_name)
    except Exception:
        error_info = traceback.format_exc()
        print("\n⚠️ Error occurred while running the mod:\n")
        print(error_info)
        log_run(mod_name, error_info)
        print("\nPlease report this issue in the Discord server or contact the mod author.")
        print(f"Discord Link: {DISCORD_LINK}")
    finally:
        print("\n--- Script finished ---")
        input("Press Enter to return to DLDSPT Menu...")


# ----------------------- descriptions / metadata ----------------------

def get_mod_description(path: str) -> str:
    """Return module docstring or first comment line from a file/dir."""
    real_path = _real_path_for_entry(path)
    try:
        with open(real_path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            # Try to parse and extract docstring (best effort)
            node = ast.parse(source)
            doc = ast.get_docstring(node)
            if doc:
                return doc.strip()
        except Exception:
            pass
        # Fallback: first line comment
        for line in source.splitlines():
            s = line.strip()
            if s.startswith("#") and len(s) > 1:
                return s[1:].strip()
    except Exception:
        pass
    return ""


# ------------------------------ menu ---------------------------------

def display_menu(py_files: list[str], filter_text: str | None = None, sort_by: str = "name") -> None:
    clear_console()
    print(f"== {APP_NAME} v{DLDSPT_VERSION} ==")
    print(f"{APP_FULL_NAME}")
    print("-" * (len(APP_FULL_NAME) + 2))
    print(f"Available Mods: {len(py_files)}")
    print(f"Total Mods Size: {get_total_mods_size(py_files)}KB")
    print(f"Sort By: {sort_by.capitalize()}")
    if last_ran_mod:
        print(f"Last Ran Mod: {last_ran_mod}")
    print()

    filtered_files = py_files
    if filter_text:
        filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
        print(f"Filter: '{filter_text}' ({len(filtered_files)} mods shown)")

    for i, f in enumerate(filtered_files, 1):
        info = get_file_info(f)
        desc = get_mod_description(f)
        print(f"{i}. {format_name(f)} ({info})")
        if desc:
            print(f"  ↳ {desc}")

    print("\nr. Reload mod list")
    print("d. Open Discord server link")
    print("q. Quit")
    print("\ns. Search/filter mods")
    print("sort. Change sort order (name/date/size)")
    print("ducky [modname]. Run a DuckyLang mod from Mods folder (e.g. ducky test)")
    print("Type 'ducks' for a surprise 🦆")
    print("Type 'updates' to view the update log")


def show_update_log() -> None:
    print("\n--- Updates ---\n")
    print("1. this is unreleased")
    print("\n--- End of Updates ---")
    input("Press Enter to continue...")


# ------------------------------- main --------------------------------

def main() -> None:
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found.")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Expected at: {os.path.join(base_dir, 'Mods')}")
        return

    sort_by = "name"
    py_files = list_mods(mods_path, sort_by)
    filter_text: str | None = None

    while True:
        display_menu(py_files, filter_text, sort_by)
        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'q':
            confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
            if confirm == 'y':
                print("Bye!")
                break
            else:
                continue

        elif choice == 'r':
            py_files = list_mods(mods_path, sort_by)
            filter_text = None
            continue

        elif choice == 'd':
            print(f"Opening Discord: {DISCORD_LINK}")
            try:
                webbrowser.open(DISCORD_LINK)
            except Exception:
                print("Couldn't open a browser here.")
            input("Press Enter to continue...")
            continue

        elif choice == 'ducks':
            print("Opening ducks on Google... 🦆")
            try:
                webbrowser.open("https://www.google.com/search?q=ducks")
            except Exception:
                print("Couldn't open a browser here.")
            input("Press Enter to continue...")
            continue

        elif choice == 'updates':
            show_update_log()
            continue

        elif choice == 's':
            filter_text = input("Enter search/filter text: ").strip()
            continue

        elif choice == 'sort':
            sort_input = input("Sort by (name/date/size): ").strip().lower()
            if sort_input in ("name", "date", "size"):
                sort_by = sort_input
                py_files = list_mods(mods_path, sort_by)
            else:
                print("❌ Invalid sort option.")
                input("Press Enter to continue...")
            continue

        elif choice.startswith('ducky'):
            parts = choice.split()
            if len(parts) == 2:
                run_duckylang_script(mods_path, parts[1])
            else:
                run_duckylang_script(mods_path)
            continue

        elif not choice.isdigit():
            print("❌ Invalid input.")
            input("Press Enter to continue...")
            continue

        # Numeric choice
        filtered_files = py_files
        if filter_text:
            filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
        idx = int(choice)
        if 1 <= idx <= len(filtered_files):
            run_script(filtered_files[idx - 1])
        else:
            print("❌ Number out of range.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    # CLI support: run script directly if filename is given
    if len(sys.argv) > 1:
        run_script(sys.argv[1])
    else:
        main()

# This is line ~340 in the fixed version.