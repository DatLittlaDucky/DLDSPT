# Version 4.1.4

import os
import sys
import runpy
import traceback
import webbrowser
import time
from datetime import datetime

APP_NAME = "DLDSPT"
APP_FULL_NAME = "DatLittlaDucky's Python Tooling"
DLDSPT_VERSION = "4.1.4"
DISCORD_LINK = "https://discord.gg/JhwNVrb7Kf"

last_ran_mod = None
LOG_FILE = "dldsptrun.log"

# --- Rich support ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    USE_RICH = True
except ImportError:
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        USE_RICH = True
    except Exception:
        USE_RICH = False


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def find_mods_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    return mods_path if os.path.isdir(mods_path) else None


def get_total_mods_size(py_files):
    total = 0
    for f in py_files:
        real_path = f if os.path.isfile(f) else os.path.join(f, "__main__.py")
        total += os.path.getsize(real_path)
    return total // 1024  # KB


def list_mods(mods_path, sort_by="name"):
    files = []
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
        def get_mtime(f):
            if os.path.isfile(f):
                return os.path.getmtime(f)
            else:
                return os.path.getmtime(os.path.join(f, "__main__.py"))
        return sorted(files, key=get_mtime, reverse=True)
    elif sort_by == "size":
        def get_size(f):
            if os.path.isfile(f):
                return os.path.getsize(f)
            else:
                return os.path.getsize(os.path.join(f, "__main__.py"))
        return sorted(files, key=get_size, reverse=True)
    return files


def format_name(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        name = os.path.basename(path) + " [DIR]"
    elif name.endswith(".py"):
        name = name[:-3] + " [Python]"
    elif name.endswith(".dkl"):
        name = name[:-4] + " [Ducky]"
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


def run_duckylang_script(mods_path, modname=None, script_path=None):
    if script_path:
        try:
            import duckylang as duckylang
            duckylang.run_duckylang(script_path)
        except Exception as e:
            print("Error running DuckyLang:", e)
            input("Press Enter to return to DLDSPT Menu...")
        return
    if not modname:
        print("\n--- DuckyLang ---")
        modname = input("Enter DuckyLang mod name (without .dkl): ").strip()
    script_path = os.path.join(mods_path, f"{modname}.dkl")
    if not os.path.isfile(script_path):
        print(f"❌ DuckyLang mod '{modname}' not found at {script_path}.")
        input("Press Enter to return to DLDSPT Menu...")
        return
    try:
        import duckylang as duckylang
        duckylang.run_duckylang(script_path)
    except Exception as e:
        print("Error running DuckyLang:", e)
        input("Press Enter to return to DLDSPT Menu...")


def run_script(path):
    global last_ran_mod
    mod_name = format_name(path)
    last_ran_mod = mod_name

    print(f"\n--- Running {mod_name} ---\n")
    if os.path.isfile(path) and path.endswith(".dkl"):
        run_duckylang_script(None, None, script_path=path)
        return
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
    input("Press Enter to return to DLDSPT Menu...")


def get_mod_description(path):
    real_path = path if os.path.isfile(path) else os.path.join(path, "__main__.py")
    try:
        with open(real_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith('"""') or line.startswith("'''"):
                    doc = line[3:]
                    for docline in f:
                        if docline.strip().endswith('"""') or docline.strip().endswith("'''"):
                            doc += " " + docline.strip()[:-3]
                            break
                        doc += " " + docline.strip()
                    return doc.strip()
                elif line.startswith("#"):
                    return line[1:].strip()
    except Exception:
        return ""
    return ""


def display_menu(py_files, filter_text=None, sort_by="name"):
    clear_console()

    if USE_RICH:
        # Rich fancy menu
        title = Text(f"{APP_NAME} v{DLDSPT_VERSION}", style="bold cyan")
        subtitle = Text(APP_FULL_NAME, style="italic green")
        console.print(Panel(title, expand=False))
        console.print(subtitle)

        console.print(f"[yellow]Available Mods:[/yellow] {len(py_files)}")
        console.print(f"[yellow]Total Mods Size:[/yellow] {get_total_mods_size(py_files)}KB")
        console.print(f"[yellow]Sort By:[/yellow] {sort_by.capitalize()}")
        if last_ran_mod:
            console.print(f"[yellow]Last Ran Mod:[/yellow] {last_ran_mod}")
        console.print()

        filtered_files = py_files
        if filter_text:
            filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
            console.print(f"[bold magenta]Filter: '{filter_text}' ({len(filtered_files)} mods shown)[/bold magenta]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="bold green")
        table.add_column("Info", style="yellow")
        table.add_column("Description", style="italic magenta")

        for i, f in enumerate(filtered_files, 1):
            info = get_file_info(f)
            desc = get_mod_description(f)
            table.add_row(str(i), format_name(f), info, desc or "-")

        console.print(table)

        console.print("\n[cyan]r.[/cyan] Reload mod list")
        console.print("[cyan]d.[/cyan] Open Discord server link")
        console.print("[cyan]q.[/cyan] Quit")
        console.print("\n[cyan]s.[/cyan] Search/filter mods")
        console.print("[cyan]sort.[/cyan] Change sort order (name/date/size)")
        console.print("[cyan]ducky [modname].[/cyan] Run a DuckyLang mod")
        console.print("[cyan]ducks.[/cyan] 🦆 Surprise")
        console.print("[cyan]updates.[/cyan] View update log")

    else:
        # Fallback plain menu
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
                print(f"    ↳ {desc}")
        print("\nr. Reload mod list")
        print("d. Open Discord server link")
        print("q. Quit")
        print("\ns. Search/filter mods")
        print("sort. Change sort order (name/date/size)")
        print("ducky [modname]. Run a DuckyLang mod from Mods folder (e.g. ducky test)")
        print("Type 'ducks' for a surprise 🦆")
        print("Type 'updates' to view the update log")


def show_update_log():
    print("\n--- Updates ---\n")
    print("1. QuackLang Removed until full release ready")
    print("2. Added Updates command")
    print("3. Mod descriptions now shown in menu")
    print("4. Search/filter mods by name")
    print("5. Display total mods size in menu")
    print("6. Sort mods by name, date, or size")
    print("7. Confirmation prompt when quitting")
    print("8. CLI support for running mods directly")
    print("9. Settings menu (planned)")
    print("10. Colored output (planned, now partially implemented with Rich in 4.1.4)")
    print("11. Per-mod error logs (planned)")
    print("12. Show last run time for each mod (planned)")
    print("13. Favorites/pin mods (planned)")
    print("14. Export/import mod list (planned)")
    print("15. Help/About menu (planned)")
    print("16. Recent mods list (planned)")
    print("17. Support for non-Python mods (planned)")
    print("18. Auto-update feature (planned)")
    print("19. DuckyLang mods now show in the mod list and can be run by number")
    print("20. DuckyLang mods display [Ducky] in the list")
    print("21. All scripts and DuckyLang mods show 'Press Enter to return to DLDSPT Menu...' when finished")
    print("22. DuckyLang mods are included in search/filter and sort features")
    print("23. DuckyLang interpreter is now in the main folder, not Mods")
    print("24. You can run DuckyLang mods using 'ducky [modname]' from the menu")
    print("25. Rich UI support added for menus (new in 4.1.4)")
    print("\n--- End of Updates ---")
    input("Press Enter to continue...")


def main():
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found.")
        return

    sort_by = "name"
    py_files = list_mods(mods_path, sort_by)
    filter_text = None

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
            webbrowser.open(DISCORD_LINK)
            input("Press Enter to continue...")
            continue
        elif choice == 'ducks':
            print("Opening ducks on Google... 🦆")
            webbrowser.open("https://www.google.com/search?q=ducks")
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
    if len(sys.argv) > 1:
        run_script(sys.argv[1])
    else:
        main()
# This is line 300+ (Version 4.1.4)