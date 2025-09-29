# DLDSPT v5.0.0 - extended (full script with extra file-type support) Released on 2025-08-27 12:00AM
import os
import sys
import runpy
import traceback
import webbrowser
import time
import subprocess
import json
from datetime import datetime

# GUI imports used only when opening guest HTML/JS
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl
    HAVE_QT = True
except Exception:
    HAVE_QT = False

# Try to import requests (used for version check)
try:
    import requests
    HAVE_REQUESTS = True
except Exception:
    HAVE_REQUESTS = False

# --- App metadata (place near top to avoid ordering issues) ---
DLDSPT_VERSION = "5.0.0"
APP_NAME = "DLDSPT"
APP_FULL_NAME = "Dat Littla Ducky's Python Tooling"
DISCORD_LINK = "https://discord.gg/JhwNVrb7Kf"
CONFIG_FILE = "config.json"
LOG_FILE = "dldsptrun.log"
RECENT_MODS_FILE = "recent_mods.json"

# --- Rich optional UI ---
USE_RICH = False
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    USE_RICH = True
except Exception:
    # Try to install rich if missing (best-effort; silent fallback)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        USE_RICH = True
    except Exception:
        USE_RICH = False

last_ran_mod = None
last_ran_path = None

# Supported extensions list
SUPPORTED_EXTENSIONS = [
    ".py", ".dkl", ".html", ".js", ".json", ".txt",
    ".csv", ".yaml", ".yml", ".ini", ".xml", ".toml",
    ".md", ".css", ".pdf", ".zip", ".mod", ".asset"
]
# Runnable set
RUNNABLE_EXTENSIONS = {".py", ".dkl", ".html", ".js"}
# View-only (open with system)
VIEW_ONLY_EXTENSIONS = set(SUPPORTED_EXTENSIONS) - RUNNABLE_EXTENSIONS

# ----------------- Safety wrappers -----------------
def find_mods_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path = os.path.join(base_dir, "Mods")
    return mods_path if os.path.isdir(mods_path) else None

def safe_open(filepath, mode="r", encoding=None):
    # Only allow access to files in Mods folder or config/log files
    allowed = os.path.abspath(filepath).startswith(os.path.abspath(find_mods_folder() or "")) \
        or os.path.basename(filepath) in [LOG_FILE, CONFIG_FILE]
    if not allowed:
        resp = input(f"Warning: Attempt to access '{filepath}'. Allow? (y/n): ").strip().lower()
        if resp != "y":
            raise PermissionError("File access denied by user.")
    return open(filepath, mode, encoding=encoding)

def safe_system(cmd):
    # Only allow safe commands, prompt for anything else
    safe_cmds = ["cls", "clear"]
    if cmd not in safe_cmds:
        resp = input(f"Warning: Attempt to run system command '{cmd}'. Allow? (y/n): ").strip().lower()
        if resp != "y":
            raise PermissionError("System command denied by user.")
    os.system(cmd)

# ----------------- Utilities -----------------
def clear_console():
    try:
        safe_system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass

def get_total_mods_size(py_files):
    total = 0
    for f in py_files:
        real_path = f if os.path.isfile(f) else os.path.join(f, "__main__.py")
        try:
            total += os.path.getsize(real_path)
        except Exception:
            pass
    return total // 1024  # KB

def list_mods(mods_path, sort_by="name"):
    files = []
    for entry in os.listdir(mods_path):
        full_path = os.path.join(mods_path, entry)
        if os.path.isdir(full_path):
            # Directory is considered a mod if it contains __main__.py
            if os.path.isfile(os.path.join(full_path, "__main__.py")):
                files.append(full_path)
            else:
                # optionally show zip or other package directories? skip
                continue
        else:
            for ext in SUPPORTED_EXTENSIONS:
                if entry.lower().endswith(ext):
                    files.append(full_path)
                    break
    # Sorting
    if sort_by == "name":
        return sorted(files, key=lambda f: os.path.basename(f).lower())
    elif sort_by == "date":
        def get_mtime(f):
            try:
                if os.path.isdir(f):
                    return os.path.getmtime(os.path.join(f, "__main__.py"))
                else:
                    return os.path.getmtime(f)
            except Exception:
                return 0
        return sorted(files, key=get_mtime, reverse=True)
    elif sort_by == "size":
        def get_size(f):
            try:
                if os.path.isdir(f):
                    return os.path.getsize(os.path.join(f, "__main__.py"))
                else:
                    return os.path.getsize(f)
            except Exception:
                return 0
        return sorted(files, key=get_size, reverse=True)
    elif sort_by == "favourites":
        favs = set(config.get("favourites", []))
        return sorted(files, key=lambda f: (f not in favs, os.path.basename(f).lower()))
    return files

def format_name(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        name = os.path.basename(path) + " [DIR]"
    else:
        lower = name.lower()
        if lower.endswith(".py"):
            name = name[:-3] + " [Python]"
        elif lower.endswith(".dkl"):
            name = name[:-4] + " [Ducky]"
        elif lower.endswith(".html"):
            name = name[:-5] + " [Webpage]"
        elif lower.endswith(".js"):
            name = name[:-3] + " [JavaScript]"
        elif lower.endswith(".json"):
            name = name[:-5] + " [JSON]"
        elif lower.endswith(".txt"):
            name = name[:-4] + " [Text]"
        elif lower.endswith(".csv"):
            name = name[:-4] + " [CSV]"
        elif lower.endswith((".yaml", ".yml")):
            name = os.path.splitext(name)[0] + " [YAML]"
        elif lower.endswith(".ini"):
            name = name[:-4] + " [Config]"
        elif lower.endswith(".xml"):
            name = name[:-4] + " [XML]"
        elif lower.endswith(".toml"):
            name = name[:-5] + " [TOML]"
        elif lower.endswith(".md"):
            name = name[:-3] + " [Markdown]"
        elif lower.endswith(".css"):
            name = name[:-4] + " [CSS]"
        elif lower.endswith(".pdf"):
            name = name[:-4] + " [PDF]"
        elif lower.endswith(".zip"):
            name = name[:-4] + " [ZIP]"
        elif lower.endswith(".mod"):
            name = name[:-4] + " [Mod]"
        elif lower.endswith(".asset"):
            name = name[:-6] + " [Asset]"
    return name.replace("-", " ").replace("_", " ")

def get_file_info(path):
    real_path = path if os.path.isfile(path) else os.path.join(path, "__main__.py")
    try:
        size = os.path.getsize(real_path)
        mtime = os.path.getmtime(real_path)
        return f"{size // 1024}KB, {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception:
        return "-"

def log_run(mod_name, error=None, duration=None, action="run"):
    try:
        with safe_open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {action.capitalize()}: {mod_name}\n")
            if duration is not None:
                f.write(f"Duration: {duration:.2f} seconds\n")
            if error:
                f.write(f"ERROR:\n{error}\n")
            f.write("\n")
    except Exception:
        pass

def add_recent_mod(mod_path):
    try:
        if os.path.isfile(RECENT_MODS_FILE):
            with open(RECENT_MODS_FILE, "r", encoding="utf-8") as f:
                recent = json.load(f)
        else:
            recent = []
        if mod_path in recent:
            recent.remove(mod_path)
        recent.insert(0, mod_path)
        recent = recent[:10]
        with open(RECENT_MODS_FILE, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
    except Exception:
        pass

# ----------------- Description extraction -----------------
def get_mod_description(path):
    real_path = path if os.path.isfile(path) else os.path.join(path, "__main__.py")
    lower = real_path.lower()
    if lower.endswith(".html"):
        return "Webpage"
    elif lower.endswith(".json"):
        return "JSON File"
    elif lower.endswith(".txt"):
        return "Text File"
    elif lower.endswith(".csv"):
        return "Tabular Data (CSV)"
    elif lower.endswith((".yaml", ".yml")):
        return "YAML Configuration"
    elif lower.endswith(".ini"):
        return "INI Config File"
    elif lower.endswith(".xml"):
        return "XML Data File"
    elif lower.endswith(".toml"):
        return "TOML Configuration"
    elif lower.endswith(".md"):
        return "Markdown Notes"
    elif lower.endswith(".css"):
        return "CSS Stylesheet"
    elif lower.endswith(".pdf"):
        return "PDF Document"
    elif lower.endswith(".zip"):
        return "ZIP Archive"
    elif lower.endswith(".mod"):
        return "Custom Mod File"
    elif lower.endswith(".asset"):
        return "Custom Asset File"
    # Fallback: attempt to read docstring/comment for source files
    try:
        if os.path.isfile(real_path) and real_path.lower().endswith((".py", ".dkl", ".js")):
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
        pass
    return ""

# ----------------- Openers/Editors -----------------
def open_with_system_default(path):
    """Open a file with the system default app (cross-platform)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
            return True
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
            return True
        else:
            # Linux / Unix
            subprocess.Popen(["xdg-open", path])
            return True
    except Exception:
        # Fallback to webbrowser
        try:
            webbrowser.open(f"file://{os.path.abspath(path)}")
            return True
        except Exception:
            return False

def open_guest_html(file_path, js_path=None):
    """Open HTML or temporary wrapper using PyQt if available; fallback to system browser."""
    if HAVE_QT:
        app = QApplication.instance() or QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Guest HTML/JS Window")
        # Use config window size
        w, h = config.get("window_size", [800, 600])
        window.resize(w, h)
        webview = QWebEngineView()
        if js_path:
            # Generate temp HTML wrapper for JS mod
            temp_html = os.path.join(os.path.dirname(js_path), "temp_js_wrapper.html")
            with safe_open(temp_html, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html><head><title>JS Mod</title></head>
<body>
<script src="{os.path.basename(js_path)}"></script>
</body></html>""")
            webview.setUrl(QUrl.fromLocalFile(temp_html))
        else:
            webview.setUrl(QUrl.fromLocalFile(file_path))
        window.setCentralWidget(webview)
        window.show()
        # If this script is not running a Qt event loop, exec
        if not QApplication.instance():
            sys.exit(app.exec())
    else:
        # Fallback: open in system browser
        try:
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        except Exception:
            print("Could not open HTML file in browser or PyQt is not available.")

def edit_file_menu_with_path(filepath):
    """Inline editor for .txt and .json, or open external editor for others."""
    mods_path = find_mods_folder()
    allowed = (
        mods_path and os.path.abspath(filepath).startswith(os.path.abspath(mods_path))
    ) or os.path.basename(filepath) in [CONFIG_FILE, LOG_FILE]
    if not allowed or not os.path.isfile(filepath):
        print("File not found or not allowed.")
        input("Press Enter to continue...")
        return

    lower = filepath.lower()
    if lower.endswith(".json") or lower.endswith(".txt"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content_lines = [line.rstrip("\n") for line in f.readlines()]
        except Exception:
            content_lines = []

        while True:
            clear_console()
            print(f"Editing: {filepath}")
            print("-" * 40)
            for i, line in enumerate(content_lines, 1):
                print(f"{i:3}: {line}")
            print("-" * 40)
            print("Actions: [a]ppend  [r]eplace_line  [d]elete_line  [i]nsert_line  [w]rite/save  [q]uit(no save)  [s]ave+quit")
            act = input("Choose action: ").strip().lower()
            if act == "a":
                text = input("Text to append: ")
                content_lines.append(text)
            elif act == "r":
                ln = input("Line number to replace: ").strip()
                try:
                    idx = int(ln) - 1
                    if 0 <= idx < len(content_lines):
                        content_lines[idx] = input("New text: ")
                    else:
                        print("Line out of range.")
                        input("Enter to continue...")
                except Exception:
                    print("Invalid line number.")
                    input("Enter to continue...")
            elif act == "d":
                ln = input("Line number to delete: ").strip()
                try:
                    idx = int(ln) - 1
                    if 0 <= idx < len(content_lines):
                        content_lines.pop(idx)
                    else:
                        print("Line out of range.")
                        input("Enter to continue...")
                except Exception:
                    print("Invalid line number.")
                    input("Enter to continue...")
            elif act == "i":
                ln = input("Insert before line number (or 0 for start): ").strip()
                try:
                    idx = int(ln) - 1
                    text = input("Text to insert: ")
                    if idx < 0:
                        content_lines.insert(0, text)
                    elif idx >= len(content_lines):
                        content_lines.append(text)
                    else:
                        content_lines.insert(idx, text)
                except Exception:
                    print("Invalid input.")
                    input("Enter to continue...")
            elif act == "w" or act == "s":
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("\n".join(content_lines) + ("\n" if content_lines else ""))
                    print("Saved.")
                except Exception as e:
                    print(f"Save failed: {e}")
                if act == "s":
                    input("Press Enter to continue...")
                    return
                input("Press Enter to continue...")
            elif act == "q":
                confirm = input("Quit without saving? (y/n): ").strip().lower()
                if confirm == "y":
                    return
            else:
                print("Unknown action.")
                input("Press Enter to continue...")
        return
    else:
        # For other file types, attempt to open in code editor or system default
        print("Opening external editor for this file...")
        try:
            if sys.platform == "win32":
                from shutil import which
                code_path = which("code") or which("code.cmd") or which("code.exe")
                if code_path:
                    subprocess.Popen([code_path, filepath])
                else:
                    os.startfile(filepath)
            else:
                from shutil import which
                code_path = which("code")
                if code_path:
                    subprocess.Popen([code_path, filepath])
                else:
                    # linux/mac default
                    if sys.platform == "darwin":
                        subprocess.Popen(["open", filepath])
                    else:
                        subprocess.Popen(["xdg-open", filepath])
            print("Editor launched. Save and close the editor when done.")
        except Exception as e:
            print(f"Could not open external editor: {e}")
        input("Press Enter to continue...")
        return

# ----------------- Version check -----------------
def fetch_latest_version():
    if not HAVE_REQUESTS:
        return None
    try:
        resp = requests.get("https://api.github.com/repos/DatLittlaDucky/DLDSPT/releases/latest", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tag = data.get("tag_name", "")
            return tag.lstrip("v")
    except Exception:
        pass
    return None

def version_tuple(v):
    try:
        return tuple(map(int, (v.split("."))))
    except Exception:
        return (0,)

def check_version():
    latest = fetch_latest_version()
    if latest:
        try:
            if version_tuple(DLDSPT_VERSION) < version_tuple(latest):
                print(f"⚠️ You are running DLDSPT v{DLDSPT_VERSION}, but the latest is v{latest}.")
                resp = input("Hey, want to update your version? (y/n): ").strip().lower()
                if resp == "y":
                    print("Visit https://github.com/DatLittlaDucky/DLDSPT to download the latest release.")
                input("Press Enter to continue...")
        except Exception:
            pass

# ----------------- Display Menu -----------------
def display_menu(py_files, filter_text=None, sort_by="name"):
    clear_console()
    check_version()

    if USE_RICH:
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

        console.print("\n[cyan]r[/cyan] Reload mod list")
        console.print("[cyan]d[/cyan] Open Discord server link")
        console.print("[cyan]q[/cyan] Quit")
        console.print("\n[cyan]s[/cyan] Search/filter mods")
        console.print("[cyan]sort[/cyan] Change sort order (name/date/size/favourites)")
        console.print("[cyan]ducky [/cyan] Run a DuckyLang mod")
        console.print("[cyan]edit[/cyan] Edit a file (text or JSON) or open others in editor")
        console.print("[cyan]ducks[/cyan] 🦆 Surprise")
        console.print("[cyan]updates[/cyan] View update log")
        console.print("[cyan]rs[/cyan] Restart DLDSPT")
        console.print("[cyan]fav[/cyan] favourite/unfavourite a mod")
        console.print("[cyan]pin[/cyan] pin/unpin a mod")
    else:
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
        print("sort. Change sort order (name/date/size/favourites)")
        print("ducky [modname]. Run a DuckyLang mod from Mods folder (e.g. ducky test)")
        print("edit. Edit a file (text or JSON) or open others in editor")
        print("Type 'ducks' for a surprise 🦆")
        print("Type 'updates' to view the update log")

    # Pinned / favourites display
    pinned = config.get("pinned", [])
    if pinned:
        print("\nPinned Mods:")
        for p in pinned:
            print(f"★ {format_name(p)}")

    favourites = config.get("favourites", [])
    if favourites:
        print("\nFavourites:")
        for f in favourites:
            print(f"❤ {format_name(f)}")
    print()

# ----------------- Update log -----------------
def show_update_log():
    print("\n--- Updates for 5.0.0 ---\n")
    print("1. Safe File/System Wrappers: Improved safe_open and safe_system for better security and user control.")
    print("2. JS Mod Support: Enhanced .js mod handling and guest window integration.")
    print("3. Per-Mod Logging: Runtime duration and error logs now more robust and detailed.")
    print("4. Config System: config.json now supports more user preferences and persists them reliably.")
    print("5. Version & Security Check: Automatic version check and clearer update instructions.")
    print("6. Expanded File Type Support: Full support for many view-only formats in the menu.")
    print("7. HTML/JS Guest Window: Improved PyQt6 QWebEngineView handling for mod safety.")
    print("8. Improved Menu & Filtering: Faster sorting, filtering, and search for large mod lists.")
    print("9. CLI Enhancements: CLI mod launching now supports all file types and config options.")
    print("10. DuckyLang Integration: DuckyLang mods can be run by number and are easier to manage.")
    print("11. File Editor: Added 'edit' command for editing text and JSON files directly in the tool.")
    print("12. JSON Editor: Edit JSON files with simple key:value lines, including booleans and strings, without raw JSON syntax.")
    print("13. Text Editor: Edit, add, and delete lines in plain text files from the menu.")
    print("\n--- End of Updates ---")
    input("Press Enter to continue...")

# ----------------- Config -----------------
def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Default config
    return {
        "window_size": [800, 600],
        "pinned": [],
        "favourites": [],
        "theme": "light"
    }

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

config = load_config()

# ----------------- Dependency installer -----------------
def install_dependencies():
    dep_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependencies.txt")
    if os.path.isfile(dep_file):
        print("Checking and installing dependencies from dependencies.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", dep_file])
            print("Dependencies installed.")
        except Exception as e:
            print(f"Dependency installation failed: {e}")

# ----------------- Mod helpers -----------------
def show_mod_info(mod_path):
    print(f"\n--- Mod Info ---")
    print(f"Name: {format_name(mod_path)}")
    print(f"Path: {mod_path}")
    print(f"Info: {get_file_info(mod_path)}")
    print(f"Description: {get_mod_description(mod_path)}")
    print("Favourited:", "Yes" if mod_path in config.get("favourites", []) else "No")
    print("Pinned:", "Yes" if mod_path in config.get("pinned", []) else "No")
    input("Press Enter to continue...")

def check_mod_updates(mod_path):
    # Placeholder for mod-specific update checks
    print("Checking for updates for this mod...")
    print("No update info available.")
    input("Press Enter to continue...")

def add_mod_comment(mod_path):
    comments_file = "mod_comments.json"
    try:
        if os.path.isfile(comments_file):
            with open(comments_file, "r", encoding="utf-8") as f:
                comments = json.load(f)
        else:
            comments = {}
        comment = input("Enter your comment for this mod: ").strip()
        comments.setdefault(mod_path, []).append(comment)
        with open(comments_file, "w", encoding="utf-8") as f:
            json.dump(comments, f, indent=2)
        print("Comment added.")
    except Exception:
        print("Failed to add comment.")
    input("Press Enter to continue...")

def add_mod_tag(mod_path):
    tags_file = "mod_tags.json"
    try:
        if os.path.isfile(tags_file):
            with open(tags_file, "r", encoding="utf-8") as f:
                tags = json.load(f)
        else:
            tags = {}
        tag = input("Enter a tag for this mod: ").strip()
        tags.setdefault(mod_path, []).append(tag)
        with open(tags_file, "w", encoding="utf-8") as f:
            json.dump(tags, f, indent=2)
        print("Tag added.")
    except Exception:
        print("Failed to add tag.")
    input("Press Enter to continue...")

def export_config():
    out = input("Enter filename to export config: ").strip()
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print("Config exported.")
    except Exception:
        print("Export failed.")
    input("Press Enter to continue...")

def import_config():
    inp = input("Enter filename to import config: ").strip()
    try:
        with open(inp, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        config.update(cfg)
        save_config(config)
        print("Config imported.")
    except Exception:
        print("Import failed.")
    input("Press Enter to continue...")

def set_theme():
    theme = input("Choose theme (light/dark): ").strip().lower()
    config["theme"] = theme
    save_config(config)
    print("Theme set.")
    input("Press Enter to continue...")

def backup_mods(mods_path):
    import zipfile
    out = input("Enter backup filename (e.g. mods_backup.zip): ").strip()
    try:
        with zipfile.ZipFile(out, "w") as z:
            for root, dirs, files in os.walk(mods_path):
                for file in files:
                    full = os.path.join(root, file)
                    z.write(full, os.path.relpath(full, mods_path))
        print("Backup complete.")
    except Exception:
        print("Backup failed.")
    input("Press Enter to continue...")

def search_mods_by_description(py_files, text):
    return [f for f in py_files if text.lower() in get_mod_description(f).lower()]

def handle_shortcuts(choice):
    if choice == 'ctrl+r':
        return 'r'
    elif choice == 'ctrl+q':
        return 'q'
    return choice

def create_file_menu():
    mods_path = find_mods_folder()
    if not mods_path:
        print("Mods folder not found.")
        input("Press Enter to continue...")
        return

    print("\nCreate New File")
    print("Supported types:")
    print("1. Text File (.txt)")
    print("2. JSON File (.json)")
    print("3. Python Script (.py)")
    print("4. HTML File (.html)")
    print("5. DuckyLang Script (.dkl)")
    print("q. Cancel")
    choice = input("Select file type (1-5): ").strip().lower()
    if choice == "q":
        return

    ext_map = {
        "1": ".txt",
        "2": ".json",
        "3": ".py",
        "4": ".html",
        "5": ".dkl"
    }
    if choice not in ext_map:
        print("Invalid choice.")
        input("Press Enter to continue...")
        return

    filename = input("Enter new filename (without extension): ").strip()
    if not filename:
        print("Filename cannot be empty.")
        input("Press Enter to continue...")
        return

    full_path = os.path.join(mods_path, filename + ext_map[choice])
    if os.path.exists(full_path):
        print("File already exists.")
        input("Press Enter to continue...")
        return

    try:
        if ext_map[choice] == ".txt":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")
        elif ext_map[choice] == ".json":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("{}")
        elif ext_map[choice] == ".py":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("# Python script\n")
        elif ext_map[choice] == ".html":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("<!DOCTYPE html>\n<html>\n<head><title>New HTML</title></head>\n<body>\n</body>\n</html>\n")
        elif ext_map[choice] == ".dkl":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("# DuckyLang script\n")
        print(f"Created file: {full_path}")
    except Exception as e:
        print(f"Failed to create file: {e}")
        input("Press Enter to continue...")
        return

    edit_now = input("Edit this file now? (y/n): ").strip().lower()
    if edit_now == "y":
        edit_file_menu_with_path(full_path)
    else:
        input("Press Enter to continue...")

# ----------------- Running / Opening logic -----------------
def run_duckylang_script(mods_path, modname=None, script_path=None):
    resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources")
    if resources_path not in sys.path:
        sys.path.insert(0, resources_path)
    if script_path:
        try:
            import duckylang
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
        import duckylang
        duckylang.run_duckylang(script_path)
    except Exception as e:
        print("Error running DuckyLang:", e)
        input("Press Enter to return to DLDSPT Menu...")

def run_script(path):
    """Run runnable mods or open view-only files appropriately."""
    global last_ran_mod, last_ran_path
    mod_name = format_name(path)
    last_ran_mod = mod_name
    last_ran_path = path

    print(f"\n--- Running {mod_name} ---\n")
    start_time = time.time()

    # If path exists and is a file:
    if os.path.isfile(path):
        lower = path.lower()
        # DuckyLang
        if lower.endswith(".dkl"):
            run_duckylang_script(None, None, script_path=path)
            duration = time.time() - start_time
            log_run(mod_name, duration=duration)
            add_recent_mod(path)
            input("Press Enter to return to DLDSPT Menu...")
            return
        # HTML file -> open in guest or browser
        elif lower.endswith(".html"):
            try:
                open_guest_html(path)
            except Exception:
                webbrowser.open(f"file://{os.path.abspath(path)}")
            duration = time.time() - start_time
            log_run(mod_name, duration=duration, action="open")
            add_recent_mod(path)
            input("Press Enter to return to DLDSPT Menu...")
            return
        # JS file -> wrap in temp html
        elif lower.endswith(".js"):
            try:
                open_guest_html(None, js_path=path)
            except Exception:
                # fallback: open file in system default
                open_with_system_default(path)
            duration = time.time() - start_time
            log_run(mod_name, duration=duration, action="open")
            add_recent_mod(path)
            input("Press Enter to return to DLDSPT Menu...")
            return
        # Runnable python or other runpy
        elif lower.endswith(".py"):
            try:
                runpy.run_path(path, run_name="__main__")
                duration = time.time() - start_time
                log_run(mod_name, duration=duration)
                add_recent_mod(path)
            except Exception:
                error_info = traceback.format_exc()
                duration = time.time() - start_time
                print("\n⚠️ Error occurred while running the mod:\n")
                print(error_info)
                log_run(mod_name, error_info, duration)
                add_recent_mod(path)
                print("\nPlease report this issue in the Discord server or contact the mod author.")
                print(f"Discord Link: {DISCORD_LINK}")
            input("Press Enter to return to DLDSPT Menu...")
            return

        # Non-runnable / view-only types -> open externally or with inline editor for text-like
        elif any(lower.endswith(ext) for ext in VIEW_ONLY_EXTENSIONS):
            # For text-like files, open inline editor
            if lower.endswith((".txt", ".json")):
                edit_file_menu_with_path(path)
                duration = time.time() - start_time
                log_run(mod_name, duration=duration, action="edit")
                add_recent_mod(path)
                return
            # For other view-only, open with system default
            else:
                opened = open_with_system_default(path)
                if not opened:
                    print("Could not open the file with system default.")
                duration = time.time() - start_time
                log_run(mod_name, duration=duration, action="open")
                add_recent_mod(path)
                input("Press Enter to return to DLDSPT Menu...")
                return

    # If path is a directory, try to run its __main__.py
    if os.path.isdir(path):
        try:
            runpy.run_path(os.path.join(path, "__main__.py"), run_name="__main__")
            duration = time.time() - start_time
            log_run(mod_name, duration=duration)
            add_recent_mod(path)
        except Exception:
            error_info = traceback.format_exc()
            duration = time.time() - start_time
            print("\n⚠️ Error occurred while running the mod:\n")
            print(error_info)
            log_run(mod_name, error_info, duration)
            add_recent_mod(path)
            print("\nPlease report this issue in the Discord server or contact the mod author.")
            print(f"Discord Link: {DISCORD_LINK}")
    else:
        print("❌ File or directory not found.")
    print("\n--- Script finished ---")
    input("Press Enter to return to DLDSPT Menu...")

# ----------------- Main loop -----------------
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
            try:
                webbrowser.open(DISCORD_LINK)
            except Exception:
                print("Could not open browser.")
            input("Press Enter to continue...")
            continue
        elif choice == 'ducks':
            print("Opening ducks on Google... 🦆")
            try:
                webbrowser.open("https://www.google.com/search?q=ducks")
            except Exception:
                print("Could not open browser.")
            input("Press Enter to continue...")
            continue
        elif choice == 'updates':
            show_update_log()
            continue
        elif choice == 'rs':
            if USE_RICH:
                console.print("[cyan]Restarting DLDSPT...[/cyan]")
            else:
                print("Restarting DLDSPT...")
            python = sys.executable
            script = os.path.abspath(__file__)
            try:
                os.execv(python, [python, script] + sys.argv[1:])
            except Exception:
                print("Restart failed.")
                sys.exit(1)
        elif choice == 's':
            filter_text = input("Enter search/filter text: ").strip()
            continue
        elif choice == 'sort':
            sort_input = input("Sort by (name/date/size/favourites): ").strip().lower()
            if sort_input in ("name", "date", "size", "favourites"):
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
        elif choice == 'edit':
            filename = input("Enter filename to edit (full path or name in Mods folder): ").strip()
            mods_path = find_mods_folder()
            if not filename:
                print("No filename entered.")
                input("Press Enter to continue...")
                continue
            if not os.path.isabs(filename):
                if mods_path is not None:
                    filename = os.path.join(mods_path, filename)
                else:
                    print("Mods folder not found.")
                    input("Press Enter to continue...")
                    continue
            edit_file_menu_with_path(filename)
            continue
        elif choice == 'create':
            create_file_menu()
            py_files = list_mods(mods_path, sort_by)
            continue
        elif choice == 'pin':
            idx = input("Enter mod number to pin/unpin: ").strip()
            filtered_files = py_files
            if filter_text:
                filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
            try:
                idx = int(idx)
                if 1 <= idx <= len(filtered_files):
                    mod_path = filtered_files[idx - 1]
                    if mod_path in config.get("pinned", []):
                        config["pinned"].remove(mod_path)
                        print("Unpinned.")
                    else:
                        config.setdefault("pinned", []).append(mod_path)
                        print("Pinned.")
                    save_config(config)
                else:
                    print("❌ Number out of range.")
            except Exception:
                print("❌ Invalid input.")
            input("Press Enter to continue...")
            continue
        elif choice == 'fav':
            idx = input("Enter mod number to favourite/unfavourite: ").strip()
            filtered_files = py_files
            if filter_text:
                filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
            try:
                idx = int(idx)
                if 1 <= idx <= len(filtered_files):
                    mod_path = filtered_files[idx - 1]
                    if mod_path in config.get("favourites", []):
                        config["favourites"].remove(mod_path)
                        print("Unfavourited.")
                    else:
                        config.setdefault("favourites", []).append(mod_path)
                        print("Favourited.")
                    save_config(config)
                else:
                    print("❌ Number out of range.")
            except Exception:
                print("❌ Invalid input.")
            input("Press Enter to continue...")
            continue
        elif choice == 'resize':
            w = input("Enter window width: ").strip()
            h = input("Enter window height: ").strip()
            try:
                config["window_size"] = [int(w), int(h)]
                save_config(config)
                print("Window size updated.")
            except Exception:
                print("❌ Invalid size.")
            input("Press Enter to continue...")
            continue
        elif not choice.isdigit():
            print("❌ Invalid input.")
            input("Press Enter to continue...")
            continue

        # If numeric selection, run the corresponding file
        filtered_files = py_files
        if filter_text:
            filtered_files = [f for f in py_files if filter_text.lower() in format_name(f).lower()]
        try:
            idx = int(choice)
            if 1 <= idx <= len(filtered_files):
                run_script(filtered_files[idx - 1])
            else:
                print("❌ Number out of range.")
                input("Press Enter to continue...")
        except Exception:
            print("❌ Invalid input.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    install_dependencies()
    if len(sys.argv) > 1:
        # If passed a file path as CLI argument, resolve and run/open it
        cli_target = sys.argv[1]
        if not os.path.isabs(cli_target):
            mp = find_mods_folder()
            if mp:
                candidate = os.path.join(mp, cli_target)
                if os.path.exists(candidate):
                    cli_target = candidate
        try:
            run_script(cli_target)
        except Exception as e:
            print(f"Error running mod from CLI: {e}")
    else:
        main()
# Line 1137