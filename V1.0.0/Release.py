# Release 1.0.0

import os
import sys
import subprocess

def find_mods_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    if os.path.isdir(mods_path):
        return mods_path
    else:
        return None

def list_python_files(mods_path):
    files = []
    for f in os.listdir(mods_path):
        if f.endswith(".py") and os.path.isfile(os.path.join(mods_path, f)):
            files.append(f)
    return files

def format_name(filename):
    name = filename[:-3]
    name = name.replace("-", " ").replace("_", " ")
    return name

def open_file(path):
    if sys.platform.startswith('win'):
        os.startfile(path)
    elif sys.platform.startswith('darwin'):
        subprocess.call(('open', path))
    else:
        subprocess.call(('xdg-open', path))

def main():
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found in current directory.")
        return

    py_files = list_python_files(mods_path)
    if not py_files:
        print("No Python files found in Mods folder.")
        return

    while True:
        print("\nSelect a mod to open:")
        for i, f in enumerate(py_files, 1):
            print(f"{i}. {format_name(f)}")

        choice = input("Enter number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            print("Exiting.")
            break
        if not choice.isdigit():
            print("Please enter a valid number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(py_files):
            file_to_open = os.path.join(mods_path, py_files[idx-1])
            print(f"Opening {file_to_open}...")
            subprocess.run([sys.executable, file_to_open])
            input("Press Enter to continue...")
        else:
            print("Number out of range.")

if __name__ == "__main__":
    main()