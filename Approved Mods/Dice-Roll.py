import random

print("Welcome to the Dice Roll Game!")
def roll_dice(max):
    result = random.randint(1, max)
    print(f"You rolled a {result} on a {max}-sided die.")

sides = int(input("how many sides do you want? --> "))

roll_dice(sides)