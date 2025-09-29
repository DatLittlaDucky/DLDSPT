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
    print("=== Buckshot Roulette Predictor with Logging ===")
    total_rounds_played = 0
    total_correct_guesses = 0

    while True:  # master loop (never exits)
        live, blank = setup_chamber()
        round_number = 1
        first_round = True
        chamber_log = []  # log for this chamber

        while live > 0 and blank > 0:
            print(f"\n--- Round {round_number} ---")
            print(f"Rounds left → Live: {live}, Blank: {blank}")

            prob_live = live / (live + blank)
            prob_blank = blank / (live + blank)

            # Apply first-round swap bias
            if first_round:
                if prob_live > prob_blank:
                    guess = "Blank"
                else:
                    guess = "Live"
                first_round = False
            else:
                guess = "Live" if prob_live > prob_blank else "Blank"

            # Show probabilities
            print(f"Chance of Live: {prob_live:.2%}")
            print(f"Chance of Blank: {prob_blank:.2%}")
            print(f"Prediction: {guess}")

            # Ask what actually happened
            actual = input("Actual result? (l = live, b = blank, q = reset): ").strip().lower()
            if actual == "l":
                actual_result = "Live"
                live -= 1
            elif actual == "b":
                actual_result = "Blank"
                blank -= 1
            elif actual == "q":
                print("\nResetting chamber...")
                break
            else:
                print("Invalid input, try again (enter 'l', 'b', or 'q').")
                continue

            # Logging
            correct = guess == actual_result
            chamber_log.append((round_number, guess, actual_result, correct))
            total_rounds_played += 1
            if correct:
                total_correct_guesses += 1

            round_number += 1

        # Chamber finished or reset — print summary
        if chamber_log:
            print("\n--- Chamber Summary ---")
            for rn, g, a, c in chamber_log:
                mark = "✅" if c else "❌"
                print(f"Round {rn}: Predicted {g}, Actual {a} {mark}")
            accuracy = (sum(c for _, _, _, c in chamber_log) / len(chamber_log)) * 100
            print(f"Chamber Accuracy: {accuracy:.2f}%")
            if total_rounds_played > 0:
                overall_acc = (total_correct_guesses / total_rounds_played) * 100
                print(f"Overall Accuracy Across All Games: {overall_acc:.2f}%")

        print("\nStarting new chamber...\n")

if __name__ == "__main__":
    main()