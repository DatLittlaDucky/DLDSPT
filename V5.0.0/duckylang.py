"""
DuckyLang - Simple language for everyone!
Commands:
    set <var> <value>
    add <var> <value>
    sub <var> <value>
    mul <var> <value>
    div <var> <value>
    print <var/text>
    input <var>
    if <var> <op> <value> then <command>
    while <var> <op> <value> do <command>
    sleep <seconds>
    random <var> <min> <max>
    len <var> <text>
    concat <var> <text1> <text2>
    exit
Example:
    set x 5
    add x 2
    print x
    if x > 5 then print Big!
    while x < 10 do add x 1
    print x
    sleep 1
    exit
"""

import time
import random

def parse_val(val, vars):
    try:
        return int(val)
    except ValueError:
        return vars.get(val, val)

def eval_cond(a, op, b):
    if op == "==": return a == b
    if op == "!=": return a != b
    if op == ">": return a > b
    if op == "<": return a < b
    if op == ">=": return a >= b
    if op == "<=": return a <= b
    return False

def run_duckylang(filename):
    vars = {}
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    i = 0
    while i < len(lines):
        line = lines[i]
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd == "set" and len(args) == 2:
            vars[args[0]] = parse_val(args[1], vars)
        elif cmd == "add" and len(args) == 2:
            vars[args[0]] = vars.get(args[0], 0) + parse_val(args[1], vars)
        elif cmd == "sub" and len(args) == 2:
            vars[args[0]] = vars.get(args[0], 0) - parse_val(args[1], vars)
        elif cmd == "mul" and len(args) == 2:
            vars[args[0]] = vars.get(args[0], 0) * parse_val(args[1], vars)
        elif cmd == "div" and len(args) == 2:
            try:
                vars[args[0]] = vars.get(args[0], 0) // parse_val(args[1], vars)
            except ZeroDivisionError:
                print("Division by zero!")
        elif cmd == "print" and args:
            if args[0] in vars:
                print(vars[args[0]])
            else:
                print(" ".join(args))
        elif cmd == "input" and args:
            val = input(f"Enter value for {args[0]}: ")
            vars[args[0]] = parse_val(val, vars)
        elif cmd == "if" and "then" in args:
            idx_then = args.index("then")
            var, op, value = args[0], args[1], parse_val(args[2], vars)
            cond = eval_cond(vars.get(var, 0), op, value)
            if cond:
                sub_cmd = " ".join(args[idx_then+1:])
                lines.insert(i+1, sub_cmd)
        elif cmd == "while" and "do" in args:
            idx_do = args.index("do")
            var, op, value = args[0], args[1], parse_val(args[2], vars)
            cond = eval_cond(vars.get(var, 0), op, value)
            if cond:
                sub_cmd = " ".join(args[idx_do+1:])
                lines.insert(i+1, f"while {var} {op} {value} do {' '.join(args[idx_do+1:])}")
                lines.insert(i+1, sub_cmd)
        elif cmd == "sleep" and args:
            try:
                time.sleep(float(args[0]))
            except Exception:
                pass
        elif cmd == "random" and len(args) == 3:
            try:
                vars[args[0]] = random.randint(int(args[1]), int(args[2]))
            except Exception:
                pass
        elif cmd == "len" and len(args) == 2:
            vars[args[0]] = len(args[1])
        elif cmd == "concat" and len(args) == 3:
            vars[args[0]] = str(args[1]) + str(args[2])
        elif cmd == "exit":
            break
        i += 1
    input("Press Enter to return to DLDSPT Menu...")  # Added at end of script

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_duckylang(sys.argv[1])
    else:
        print("Usage: python duckylang.py <script.dkl>")
