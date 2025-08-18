def setup_chamber():
    while True:
        try:
            live = int(input("Enter starting number of live rounds: "))
            blank = int(input("Enter starting number of blank rounds: "))
            if live >= 0 and blank >= 0 and (live + blank) > 0:
                return live, blank
            else:
                print("Invalid chamber setup. Must have at least 1 round total.")
        except ValueError:
            print("Please enter valid numbers.")

def main():
    print("=== Buckshot Roulette Predictor ===")

    while True:  # master loop (never exits)
        live, blank = setup_chamber()
        round_number = 1
        first_round = True

        while live > 0 and blank > 0:
            print(f"\n--- Round {round_number} ---")
            print(f"Rounds left → Live: {live}, Blank: {blank}")

            prob_live = live / (live + blank)
            prob_blank = blank / (live + blank)

            # Apply first-round swap bias
            if first_round:
                if prob_live > prob_blank:
                    guess = "Blank (First-round swap rule!)"
                else:
                    guess = "Live (First-round swap rule!)"
                first_round = False
            else:
                guess = "Live" if prob_live > prob_blank else "Blank"

            # Show probabilities
            print(f"Chance of Live: {prob_live:.2%}")
            print(f"Chance of Blank: {prob_blank:.2%}")
            print(f"Prediction: {guess}")

            # Ask what actually happened
            actual = input("What was the actual result? (l = live, b = blank, q = reset): ").strip().lower()
            if actual == "l":
                live -= 1
            elif actual == "b":
                blank -= 1
            elif actual == "q":
                print("\nResetting chamber...")
                break  # exits inner loop → resets chamber
            else:
                print("Invalid input, try again (enter 'l', 'b', or 'q').")
                continue

            round_number += 1

        print("\nChamber empty or reset. Starting new game...\n")

if __name__ == "__main__":
    main()