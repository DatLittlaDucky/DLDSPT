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
    # New commands:
    upper <var> <text>
    lower <var> <text>
    title <var> <text>
    reverse <var> <text>
    split <var> <text> <sep>
    join <var> <listvar> <sep>
    list <var> <item1> <item2> ...
    append <listvar> <item>
    pop <listvar>
    get <var> <listvar> <index>
    setitem <listvar> <index> <value>
    find <var> <text> <substr>
    replace <var> <text> <old> <new>
    count <var> <text> <substr>
    range <var> <start> <end>
    sum <var> <listvar>
    max <var> <listvar>
    min <var> <listvar>
    sort <listvar>
    shuffle <listvar>
    dict <var> <key1> <val1> <key2> <val2> ...
    getkey <var> <dictvar> <key>
    setkey <dictvar> <key> <value>
    keys <var> <dictvar>
    values <var> <dictvar>
    delkey <dictvar> <key>
    # File commands:
    read <var> <filename>
    write <filename> <text>
    appendfile <filename> <text>
    exists <var> <filename>
    # Math:
    pow <var> <base> <exp>
    sqrt <var> <value>
    abs <var> <value>
    mod <var> <a> <b>
    # System:
    system <command>
    # Logic:
    not <var> <value>
    and <var> <a> <b>
    or <var> <a> <b>
    # Misc:
    inputint <var>
    inputfloat <var>
    inputstr <var>
    # More can be added!
Example:
    set x 5
    add x 2
    print x
    upper y hello
    print y
    list l 1 2 3
    append l 4
    print l
    dict d a 1 b 2
    getkey v d a
    print v
    exit
"""

import time
import random
import math
import os

def parse_val(val, vars):
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
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
            vars[args[0]] = len(str(args[1]))
        elif cmd == "concat" and len(args) == 3:
            vars[args[0]] = str(args[1]) + str(args[2])
        # --- New commands ---
        elif cmd == "upper" and len(args) == 2:
            vars[args[0]] = str(parse_val(args[1], vars)).upper()
        elif cmd == "lower" and len(args) == 2:
            vars[args[0]] = str(parse_val(args[1], vars)).lower()
        elif cmd == "title" and len(args) == 2:
            vars[args[0]] = str(parse_val(args[1], vars)).title()
        elif cmd == "reverse" and len(args) == 2:
            vars[args[0]] = str(parse_val(args[1], vars))[::-1]
        elif cmd == "split" and len(args) == 3:
            vars[args[0]] = str(parse_val(args[1], vars)).split(args[2])
        elif cmd == "join" and len(args) == 3:
            v = vars.get(args[1], [])
            if isinstance(v, list):
                vars[args[0]] = str(args[2]).join(map(str, v))
        elif cmd == "list" and len(args) >= 2:
            vars[args[0]] = [parse_val(a, vars) for a in args[1:]]
        elif cmd == "append" and len(args) == 2:
            v = vars.get(args[0], [])
            if isinstance(v, list):
                v.append(parse_val(args[1], vars))
                vars[args[0]] = v
        elif cmd == "pop" and len(args) == 1:
            v = vars.get(args[0], [])
            if isinstance(v, list) and v:
                v.pop()
                vars[args[0]] = v
        elif cmd == "get" and len(args) == 3:
            v = vars.get(args[1], [])
            idx = int(parse_val(args[2], vars))
            if isinstance(v, list) and 0 <= idx < len(v):
                vars[args[0]] = v[idx]
        elif cmd == "setitem" and len(args) == 3:
            v = vars.get(args[0], [])
            idx = int(parse_val(args[1], vars))
            if isinstance(v, list) and 0 <= idx < len(v):
                v[idx] = parse_val(args[2], vars)
                vars[args[0]] = v
        elif cmd == "find" and len(args) == 3:
            vars[args[0]] = str(parse_val(args[1], vars)).find(args[2])
        elif cmd == "replace" and len(args) == 4:
            vars[args[0]] = str(parse_val(args[1], vars)).replace(args[2], args[3])
        elif cmd == "count" and len(args) == 3:
            vars[args[0]] = str(parse_val(args[1], vars)).count(args[2])
        elif cmd == "range" and len(args) == 3:
            start = int(parse_val(args[1], vars))
            end = int(parse_val(args[2], vars))
            vars[args[0]] = list(range(start, end))
        elif cmd == "sum" and len(args) == 2:
            v = vars.get(args[1], [])
            if isinstance(v, list):
                vars[args[0]] = sum(map(float, v))
        elif cmd == "max" and len(args) == 2:
            v = vars.get(args[1], [])
            if isinstance(v, list) and v:
                vars[args[0]] = max(v)
        elif cmd == "min" and len(args) == 2:
            v = vars.get(args[1], [])
            if isinstance(v, list) and v:
                vars[args[0]] = min(v)
        elif cmd == "sort" and len(args) == 1:
            v = vars.get(args[0], [])
            if isinstance(v, list):
                v.sort()
                vars[args[0]] = v
        elif cmd == "shuffle" and len(args) == 1:
            v = vars.get(args[0], [])
            if isinstance(v, list):
                random.shuffle(v)
                vars[args[0]] = v
        elif cmd == "dict" and len(args) >= 3 and len(args) % 2 == 1:
            d = {}
            for k, v in zip(args[1::2], args[2::2]):
                d[k] = parse_val(v, vars)
            vars[args[0]] = d
        elif cmd == "getkey" and len(args) == 3:
            d = vars.get(args[1], {})
            if isinstance(d, dict):
                vars[args[0]] = d.get(args[2], None)
        elif cmd == "setkey" and len(args) == 3:
            d = vars.get(args[0], {})
            if isinstance(d, dict):
                d[args[1]] = parse_val(args[2], vars)
                vars[args[0]] = d
        elif cmd == "keys" and len(args) == 2:
            d = vars.get(args[1], {})
            if isinstance(d, dict):
                vars[args[0]] = list(d.keys())
        elif cmd == "values" and len(args) == 2:
            d = vars.get(args[1], {})
            if isinstance(d, dict):
                vars[args[0]] = list(d.values())
        elif cmd == "delkey" and len(args) == 2:
            d = vars.get(args[0], {})
            if isinstance(d, dict) and args[1] in d:
                del d[args[1]]
                vars[args[0]] = d
        elif cmd == "read" and len(args) == 2:
            try:
                with open(args[1], "r", encoding="utf-8") as f:
                    vars[args[0]] = f.read()
            except Exception:
                vars[args[0]] = ""
        elif cmd == "write" and len(args) == 2:
            try:
                with open(args[0], "w", encoding="utf-8") as f:
                    f.write(str(parse_val(args[1], vars)))
            except Exception:
                pass
        elif cmd == "appendfile" and len(args) == 2:
            try:
                with open(args[0], "a", encoding="utf-8") as f:
                    f.write(str(parse_val(args[1], vars)))
            except Exception:
                pass
        elif cmd == "exists" and len(args) == 2:
            vars[args[0]] = os.path.exists(args[1])
        elif cmd == "pow" and len(args) == 3:
            try:
                vars[args[0]] = math.pow(float(parse_val(args[1], vars)), float(parse_val(args[2], vars)))
            except Exception:
                vars[args[0]] = 0
        elif cmd == "sqrt" and len(args) == 2:
            try:
                vars[args[0]] = math.sqrt(float(parse_val(args[1], vars)))
            except Exception:
                vars[args[0]] = 0
        elif cmd == "abs" and len(args) == 2:
            try:
                vars[args[0]] = abs(float(parse_val(args[1], vars)))
            except Exception:
                vars[args[0]] = 0
        elif cmd == "mod" and len(args) == 3:
            try:
                vars[args[0]] = float(parse_val(args[1], vars)) % float(parse_val(args[2], vars))
            except Exception:
                vars[args[0]] = 0
        elif cmd == "system" and args:
            os.system(" ".join(args))
        elif cmd == "not" and len(args) == 2:
            vars[args[0]] = not bool(parse_val(args[1], vars))
        elif cmd == "and" and len(args) == 3:
            vars[args[0]] = bool(parse_val(args[1], vars)) and bool(parse_val(args[2], vars))
        elif cmd == "or" and len(args) == 3:
            vars[args[0]] = bool(parse_val(args[1], vars)) or bool(parse_val(args[2], vars))
        elif cmd == "inputint" and len(args) == 1:
            try:
                vars[args[0]] = int(input(f"Enter integer for {args[0]}: "))
            except Exception:
                vars[args[0]] = 0
        elif cmd == "inputfloat" and len(args) == 1:
            try:
                vars[args[0]] = float(input(f"Enter float for {args[0]}: "))
            except Exception:
                vars[args[0]] = 0.0
        elif cmd == "inputstr" and len(args) == 1:
            vars[args[0]] = input(f"Enter string for {args[0]}: ")
        elif cmd == "exit":
            break
        i += 1
    input("Press Enter to return to DLDSPT Menu...")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_duckylang(sys.argv[1])
    else:
        print("Usage: python duckylang.py <script.dkl>")
