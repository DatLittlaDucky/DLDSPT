# Guilty as Sock Sorta..

import random

# Strong-sounding names for "criminals"
criminals = ["Brick Johnson", "Steel McBiceps", "Razor Rick", "Buff Tina", "Sledgehammer Sam"]

# Frail or innocent names for "victims"
victims = ["Tiny Tim", "Grandma May", "Little Lisa", "Shy Steve", "Innocent Ivy"]

# Realistic crimes
crimes = [
    "punched someone for looking at them wrong",
    "stole a car from a school parking lot",
    "broke into a bakery and ate all the donuts",
    "robbed a bank using a fake mustache",
    "threw a chair through a neighbor’s window"
]

# Silly or innocent "non-crimes"
not_crimes = [
    "gave someone too many compliments",
    "wore socks with sandals",
    "ate pizza with a fork",
    "walked backwards in a mall",
    "sneezed too loudly in a library"
]

score = 0

for _ in range(5):  # 5 cases per game
    is_crime = random.choice([True, False])
    criminal = random.choice(criminals)
    victim = random.choice(victims)

    if is_crime:
        act = random.choice(crimes)
        guilty = True
    else:
        act = random.choice(not_crimes)
        guilty = False

    print("\n--- NEW CASE ---")
    print(f"{criminal} was reported by {victim} for the following incident:")
    print(f"{criminal} allegedly {act}.")

    answer = input("Guilty or Not Guilty? (g/n): ").lower()

    if (answer == "g" and guilty) or (answer == "n" and not guilty):
        print("✅ Correct judgment!")
        score += 1
    else:
        print("❌ Wrong judgment!")
        if guilty:
            print("That was an actual crime.")
        else:
            print("That was not a real crime.")

print(f"\nFinal Score: {score}/5")