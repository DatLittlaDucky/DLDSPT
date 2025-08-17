# calculator

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

def calculator():
    print("Simple Calculator")
    try:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))
        print("Choose operation:")
        print("1. Add (+)")
        print("2. Subtract (-)")
        print("3. Multiply (*)")
        print("4. Divide (/)")
        choice = input("Enter choice (1/2/3/4): ")

        if choice == '1':
            result = add(a, b)
            op = '+'
        elif choice == '2':
            result = subtract(a, b)
            op = '-'
        elif choice == '3':
            result = multiply(a, b)
            op = '*'
        elif choice == '4':
            result = divide(a, b)
            op = '/'
        else:
            print("Invalid choice")
            return

        print(f"{a} {op} {b} = {result}")

    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    calculator()