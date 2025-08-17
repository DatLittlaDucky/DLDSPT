# Version 1.2.9

import os
import sys
import runpy

def clear_console():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:
        os.system('clear')

def find_mods_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    return mods_path if os.path.isdir(mods_path) else None

def list_python_files(mods_path):
    return [f for f in os.listdir(mods_path)
            if f.endswith(".py") and os.path.isfile(os.path.join(mods_path, f))]

def format_name(filename):
    return filename[:-3].replace("-", " ").replace("_", " ")

def run_script(file_path):
    print(f"\n--- Running {file_path} ---\n")
    try:
        runpy.run_path(file_path, run_name="__main__")
    except Exception as e:
        print(f"\nError running script:\n{e}")
    print("\n--- Script finished ---")
    input("Press Enter to return to menu...")

def main():
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found.")
        return

    py_files = list_python_files(mods_path)
    if not py_files:
        print("No Python files found.")
        return

    while True:
        clear_console()
        print("Select a mod to run:")
        for i, f in enumerate(py_files, 1):
            print(f"{i}. {format_name(f)}")
        print("q. Quit")

        choice = input("Enter number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            print("Bye!")
            break

        if not choice.isdigit():
            print("Please enter a valid number.")
            input("Press Enter to continue...")
            continue

        idx = int(choice)
        if 1 <= idx <= len(py_files):
            file_to_run = os.path.join(mods_path, py_files[idx - 1])
            run_script(file_to_run)
        else:
            print("Number out of range.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()