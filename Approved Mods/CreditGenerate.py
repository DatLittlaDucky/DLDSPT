# Credit card and PIN generator

import random

Credit_card_pt1 = random.randint(1000, 9999)
Credit_card_pt2 = random.randint(1000, 9999)
Credit_card_pt3 = random.randint(1000, 9999)
Credit_card_pt4 = random.randint(1000, 9999)
Credit_card = f"{Credit_card_pt1}-{Credit_card_pt2}-{Credit_card_pt3}-{Credit_card_pt4}"
pin_number = random.randint(1000, 9999)

print("Your randomly generated credit card number is:", Credit_card, "and your pin number is:", pin_number)