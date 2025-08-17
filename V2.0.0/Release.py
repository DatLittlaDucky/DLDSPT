# Version 2.0.0

import os
import sys
import runpy
import traceback
import webbrowser
from datetime import datetime

APP_NAME = "DLDSPT"
APP_FULL_NAME = "DatLittlaDucky's Python Tooling"
VERSION = "2.0.0"
DISCORD_LINK = "https://discord.gg/TFJdfpmJZ9"

last_ran_mod = None
LOG_FILE = "dldsptrun.log"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_mods_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    return mods_path if os.path.isdir(mods_path) else None

def list_mods(mods_path):
    files = []
    for entry in os.listdir(mods_path):
        full_path = os.path.join(mods_path, entry)
        if entry.endswith(".py") and os.path.isfile(full_path):
            files.append(full_path)
        elif os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "__main__.py")):
            files.append(full_path)
    return sorted(files, key=lambda f: os.path.basename(f).lower())

def format_name(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        name = os.path.basename(path) + " [DIR]"
    else:
        name = name[:-3]
    return name.replace("-", " ").replace("_", " ")

def get_file_info(path):
    real_path = path if os.path.isfile(path) else os.path.join(path, "__main__.py")
    size = os.path.getsize(real_path)
    mtime = os.path.getmtime(real_path)
    return f"{size // 1024}KB, {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}"

def log_run(mod_name, error=None):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - Running mod: {mod_name}\n")
        if error:
            f.write(f"ERROR:\n{error}\n")
        f.write("\n")

def run_script(path):
    global last_ran_mod
    mod_name = format_name(path)
    last_ran_mod = mod_name

    print(f"\n--- Running {mod_name} ---\n")
    try:
        if os.path.isdir(path):
            runpy.run_path(os.path.join(path, "__main__.py"), run_name="__main__")
        else:
            runpy.run_path(path, run_name="__main__")
        log_run(mod_name)
    except Exception:
        error_info = traceback.format_exc()
        print("\n⚠️ Error occurred while running the mod:\n")
        print(error_info)
        log_run(mod_name, error_info)
        print("\nPlease report this issue in the Discord server or contact the mod author.")
        print(f"Discord Link: {DISCORD_LINK}")
    print("\n--- Script finished ---")
    input("Press Enter to return to menu...")

def display_menu(py_files):
    clear_console()
    print(f"== {APP_NAME} v{VERSION} ==")
    print(f"{APP_FULL_NAME}")
    print("-" * (len(APP_FULL_NAME) + 2))
    print(f"Available Mods: {len(py_files)}")
    if last_ran_mod:
        print(f"Last Ran Mod: {last_ran_mod}")
    print()
    for i, f in enumerate(py_files, 1):
        info = get_file_info(f)
        print(f"{i}. {format_name(f)} ({info})")
    print("\nr. Reload mod list")
    print("d. Open Discord server link")
    print("q. Quit")
    print("\nType 'ducks' for a surprise 🦆")

def main():
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found.")
        return

    py_files = list_mods(mods_path)

    while True:
        display_menu(py_files)
        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'q':
            print("Bye!")
            break
        elif choice == 'r':
            py_files = list_mods(mods_path)
            continue
        elif choice == 'd':
            print(f"Opening Discord: {DISCORD_LINK}")
            webbrowser.open(DISCORD_LINK)
            input("Press Enter to continue...")
            continue
        elif choice == 'ducks':
            print("Opening ducks on Google... 🦆")
            webbrowser.open("https://www.google.com/search?q=ducks")
            input("Press Enter to continue...")
            continue
        elif not choice.isdigit():
            print("❌ Invalid input.")
            input("Press Enter to continue...")
            continue

        idx = int(choice)
        if 1 <= idx <= len(py_files):
            run_script(py_files[idx - 1])
        else:
            print("❌ Number out of range.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()