# Version 3.6.8

import os
import sys
import runpy
import traceback
import webbrowser
import re
import time
import random
import ast
from datetime import datetime

APP_NAME = "DLDSPT"
APP_FULL_NAME = "DatLittlaDucky's Python Tooling"
DLDSPT_VERSION = "3.7.5"
QUACKLANG_VERSION = "1.0.0"
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
        elif entry.endswith(".Quack") and os.path.isfile(full_path):
            files.append(full_path)
        elif os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "__main__.py")):
            files.append(full_path)
    return sorted(files, key=lambda f: os.path.basename(f).lower())

def format_name(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        name = os.path.basename(path) + " [DIR]"
    elif name.endswith(".Quack"):
        name = name[:-6] + " [Quack]"
    elif name.endswith(".py"):
        name = name[:-3] + " [Python]"
    else:
        name = name
    return name.replace("-", " ").replace("_", " ")

def get_file_info(path):
    if path.endswith(".Quack"):
        real_path = path
    else:
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

class QuackLang:
    """
    QuackLang: A simple, beginner-friendly scripting language.
    Supports variables, lists, arithmetic, functions, loops, and conditionals.
    """

    def __init__(self):
        # Stores variables, lists, and functions
        self.vars = {}
        self.lists = {}
        self.functions = {}
        self.lines = []
        self.pos = 0
        self.call_stack = []

    def run(self, code):
        """
        Run QuackLang code from a string.
        Ignores blank lines and lines starting with // or # (comments).
        """
        self.lines = [
            line.strip()
            for line in code.splitlines()
            if line.strip() and not line.strip().startswith("//") and not line.strip().startswith("#")
        ]
        self.pos = 0
        while self.pos < len(self.lines):
            self.execute(self.lines[self.pos])
            self.pos += 1

    def run_file(self, filename):
        """Run QuackLang code from a file."""
        try:
            with open(filename, 'r') as f:
                code = f.read()
            self.run(code)
        except FileNotFoundError:
            print(f"File {filename} not found.")

    def execute(self, line):
        """Parse and execute a single line of QuackLang code."""
        if line.lower() in ("help", "?"):
            self.show_help()
        elif line.startswith("show ") or line.startswith("print "):
            self.handle_show(line)
        elif line.startswith("input "):
            self.handle_input(line)
        elif line.startswith("list "):
            self.handle_list(line)
        elif line.startswith("append "):
            self.handle_append(line)
        elif line.startswith(("add ", "sub ", "mul ", "div ")):
            self.handle_arithmetic(line)
        elif line.startswith("if "):
            self.handle_if(line)
        elif line.startswith("loop while "):
            self.handle_loop(line)
        elif line == "end":
            pass
        elif line.startswith("function "):
            self.handle_function_def(line)
        elif line.startswith("call "):
            self.handle_call(line)
        elif line.startswith("rand "):
            self.handle_rand(line)
        elif line == "clear":
            self.handle_clear()
        elif line.startswith("let "):
            self.handle_let(line)
        elif "=" in line:
            self.handle_assign(line)
        else:
            print(f"Unknown command: {line}")

    def show_help(self):
        """Print a summary of QuackLang syntax and features."""
        print("""
QuackLang Help:
---------------
# or // at the start of a line = comment
let x = 5         # or just: x = 5
show x            # print a variable or value
print x           # alias for show
input name        # get user input and store in 'name'
list fruits = ["apple", "banana"]
append fruits "cherry"
show fruits[1]
add x 2           # x = x + 2 (also: sub, mul, div)
if x > 5
  show "big"
end
loop while x > 0
  show x
  sub x 1
end
function greet(person)
  show "Hi, " + person
end
call greet("Duck")
rand r 1 10       # r = random int between 1 and 10
clear             # clear the screen
help or ?         # show this help
""")

    def handle_let(self, line):
        # let var = value
        _, rest = line.split("let ", 1)
        self.handle_assign(rest)

    def handle_show(self, line):
        # Support both 'show' and 'print'
        content = line[5:].strip() if line.startswith("show ") else line[6:].strip()
        try:
            if "[" in content and "]" in content:
                list_name = content[:content.index("[")].strip()
                index_str = content[content.index("[")+1:content.index("]")].strip()
                index = int(self.eval_expression(index_str))
                if list_name in self.lists:
                    if 0 <= index < len(self.lists[list_name]):
                        print(self.lists[list_name][index])
                    else:
                        print(f"Error: Index {index} out of range for list '{list_name}'")
                else:
                    print(f"Error: List '{list_name}' not found")
                return
            val = self.eval_expression(content)
            print(val)
        except Exception as e:
            print(f"Error in show/print: {e}")

    def handle_input(self, line):
        var = line[6:].strip()
        val = input()
        self.vars[var] = val

    def handle_list(self, line):
        m = re.match(r"list (\w+)\s*=\s*\[(.*)\]", line)
        if not m:
            print("Syntax error in list declaration")
            return
        var = m.group(1)
        items = [item.strip().strip('"') for item in m.group(2).split(",") if item.strip()]
        self.lists[var] = items

    def handle_append(self, line):
        m = re.match(r"append (\w+) (.+)", line)
        if not m:
            print("Syntax error in append")
            return
        var = m.group(1)
        val = m.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        if var not in self.lists:
            print(f"Error: List '{var}' not found")
            return
        self.lists[var].append(val)

    def handle_arithmetic(self, line):
        parts = line.split()
        if len(parts) != 3:
            print("Syntax error in arithmetic")
            return
        op, var, val_expr = parts
        if var not in self.vars:
            print(f"Error: Variable '{var}' not found")
            return
        try:
            val = self.eval_expression(val_expr)
            if not isinstance(val, (int, float)):
                print("Error: Arithmetic operations require numeric values")
                return
            if op == "add":
                self.vars[var] += val
            elif op == "sub":
                self.vars[var] -= val
            elif op == "mul":
                self.vars[var] *= val
            elif op == "div":
                if val == 0:
                    print("Error: Division by zero")
                    return
                self.vars[var] /= val
        except Exception as e:
            print(f"Error in arithmetic: {e}")

    def handle_if(self, line):
        cond = line[3:].strip()
        if self.eval_condition(cond):
            self.pos += 1
        else:
            self.skip_block()

    def handle_loop(self, line):
        cond = line[11:].strip()
        start = self.pos + 1
        while self.eval_condition(cond):
            i = start
            while i < len(self.lines):
                if self.lines[i] == "end":
                    break
                self.execute(self.lines[i])
                i += 1
            else:
                break
        self.pos = i

    def handle_function_def(self, line):
        m = re.match(r"function (\w+)\((.*?)\)", line)
        if not m:
            print("Syntax error in function definition")
            return
        fname = m.group(1)
        params = [p.strip() for p in m.group(2).split(",") if p.strip()]
        body = []
        self.pos += 1
        while self.pos < len(self.lines):
            if self.lines[self.pos] == "end":
                break
            body.append(self.lines[self.pos])
            self.pos += 1
        self.functions[fname] = (params, body)

    def handle_call(self, line):
        m = re.match(r"call (\w+)\((.*?)\)", line)
        if not m:
            print("Syntax error in call")
            return
        fname = m.group(1)
        args = [a.strip() for a in m.group(2).split(",") if a.strip()]
        if fname not in self.functions:
            print(f"Error: Function '{fname}' not found")
            return
        params, body = self.functions[fname]
        if len(args) != len(params):
            print(f"Error: Function '{fname}' expects {len(params)} args, got {len(args)}")
            return
        saved_vars = self.vars.copy()
        for p, a in zip(params, args):
            try:
                self.vars[p] = self.eval_expression(a)
            except Exception as e:
                print(f"Error evaluating argument '{a}': {e}")
                self.vars[p] = ""
        for line in body:
            self.execute(line)
        self.vars = saved_vars

    def handle_rand(self, line):
        parts = line.split()
        if len(parts) != 4:
            print("Syntax error in rand")
            return
        _, var, mn_expr, mx_expr = parts
        mn = self.eval_expression(mn_expr)
        mx = self.eval_expression(mx_expr)
        self.vars[var] = random.randint(int(mn), int(mx))

    def handle_clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def handle_assign(self, line):
        if "[" in line and "]" in line.split("=")[0]:
            left, val = line.split("=", 1)
            val = val.strip()
            list_name = left[:left.index("[")].strip()
            index_str = left[left.index("[")+1:left.index("]")].strip()
            try:
                index = int(self.eval_expression(index_str))
                if list_name not in self.lists:
                    print(f"Error: List '{list_name}' not found")
                    return
                val_eval = self.eval_expression(val)
                if index < 0 or index >= len(self.lists[list_name]):
                    print(f"Error: Index {index} out of range for list '{list_name}'")
                    return
                self.lists[list_name][index] = val_eval
            except Exception as e:
                print(f"Error in list index assignment: {e}")
            return
        var, val = line.split("=", 1)
        var = var.strip()
        val = val.strip()
        try:
            self.vars[var] = self.eval_expression(val)
        except Exception as e:
            print(f"Error in assignment: {e}")

    def get_value(self, val):
        if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
            return int(val)
        try:
            return float(val)
        except:
            pass
        if val in self.vars:
            return self.vars[val]
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        return val

    def eval_expression(self, expr):
        class EvalExpr(ast.NodeVisitor):
            def __init__(self, outer):
                self.outer = outer

            def visit_BinOp(self, node):
                left = self.visit(node.left)
                right = self.visit(node.right)
                if isinstance(node.op, ast.Add):
                    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                        return left + right
                    return str(left) + str(right)
                elif isinstance(node.op, ast.Sub):
                    return left - right
                elif isinstance(node.op, ast.Mult):
                    return left * right
                elif isinstance(node.op, ast.Div):
                    return left / right
                else:
                    raise ValueError(f"Unsupported operator {node.op}")

            def visit_Num(self, node):
                return node.n

            def visit_Str(self, node):
                return node.s

            def visit_Constant(self, node):
                return node.value

            def visit_Name(self, node):
                if node.id in self.outer.vars:
                    return self.outer.vars[node.id]
                else:
                    print(f"Error: Variable '{node.id}' not found")
                    return ""
            def visit_UnaryOp(self, node):
                operand = self.visit(node.operand)
                if isinstance(node.op, ast.USub):
                    return -operand
                return operand

            def generic_visit(self, node):
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")

        try:
            tree = ast.parse(expr, mode='eval')
            return EvalExpr(self).visit(tree.body)
        except Exception as e:
            try:
                return self.get_value(expr)
            except:
                raise e

    def eval_condition(self, cond):
        ops = ["==", "!=", ">=", "<=", ">", "<"]
        for op in ops:
            if op in cond:
                left, right = cond.split(op)
                left_val = self.eval_expression(left.strip())
                right_val = self.eval_expression(right.strip())
                # Only compare if types are compatible
                if type(left_val) != type(right_val):
                    try:
                        left_val = float(left_val)
                        right_val = float(right_val)
                    except Exception:
                        print(f"Error: Cannot compare {left_val} ({type(left_val).__name__}) and {right_val} ({type(right_val).__name__})")
                        return False
                if op == "==":
                    return left_val == right_val
                elif op == "!=":
                    return left_val != right_val
                elif op == ">":
                    return left_val > right_val
                elif op == "<":
                    return left_val < right_val
                elif op == ">=":
                    return left_val >= right_val
                elif op == "<=":
                    return left_val <= right_val
        val = self.eval_expression(cond)
        return bool(val)

    def skip_block(self):
        """Skip lines until the end of the current block (until 'end' is found)."""
        indent = 0
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line == "end":
                if indent == 0:
                    break
                indent -= 1
            elif line.endswith(":"):
                indent += 1
            self.pos += 1

def run_quack_file(path):
    global last_ran_mod
    mod_name = format_name(path)
    last_ran_mod = mod_name
    print(f"\n--- Running {mod_name} ---\n")
    try:
        lang = QuackLang()
        lang.run_file(path)
        log_run(mod_name)
    except Exception:
        error_info = traceback.format_exc()
        print("\n⚠️ Error occurred while running the Quack mod:\n")
        print(error_info)
        log_run(mod_name, error_info)
        print("\nPlease report this issue in the Discord server or contact the mod author.")
        print(f"Discord Link: {DISCORD_LINK}")
    print("\n--- Script finished ---")
    input("Press Enter to return to menu...")

def run_script(path):
    if path.endswith(".Quack"):
        run_quack_file(path)
        return
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
    print(f"== {APP_NAME} v{DLDSPT_VERSION} ==")
    print(f"{APP_FULL_NAME}")
    print(f"== QuackLang v{QUACKLANG_VERSION} ==")
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