import os
from collections import defaultdict


def parse_deck(deck_text):
    mainboard = defaultdict(int)
    sideboard = defaultdict(int)

    current_section = "main"

    lines = deck_text.splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.lower() == "sideboard":
            current_section = "side"
            continue

        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue

        count, card_name = parts

        if not count.isdigit():
            continue

        count = int(count)

        if current_section == "main":
            mainboard[card_name] += count
        else:
            sideboard[card_name] += count

    return mainboard, sideboard


def analyze_folder():
    base_path = "decks"

    if not os.path.exists(base_path):
        print("No 'decks' folder found.")
        return

    # List subfolders
    folders = [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f))
    ]

    if not folders:
        print("No deck folders found inside 'decks'.")
        return

    print("Available deck folders:")
    for i, folder in enumerate(folders):
        print(f"{i + 1}. {folder}")

    choice = int(input("Choose a folder number to analyze: "))
    chosen_folder = folders[choice - 1]

    folder_path = os.path.join(base_path, chosen_folder)

    deck_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ]

    if not deck_files:
        print("No .txt deck files found in that folder.")
        return

    print(f"\nAnalyzing {len(deck_files)} decks in '{chosen_folder}'...\n")

    num_decks = len(deck_files)

    total_main_counts = defaultdict(int)
    total_side_counts = defaultdict(int)

    decks_with_main = defaultdict(int)
    decks_with_side = defaultdict(int)

    for filename in deck_files:
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            deck_text = f.read()

        mainboard, sideboard = parse_deck(deck_text)

        for card, count in mainboard.items():
            total_main_counts[card] += count
            decks_with_main[card] += 1

        for card, count in sideboard.items():
            total_side_counts[card] += count
            decks_with_side[card] += 1

    print("====== MAINBOARD STATS ======\n")
    for card in sorted(total_main_counts):
        total = total_main_counts[card]
        decks_playing = decks_with_main[card]
        percent = (decks_playing / num_decks) * 100
        average = total / decks_playing

        print(f"{card} appears {average:.2f} copies in {percent:.2f}% of decks")

    print("\n====== SIDEBOARD STATS ======\n")
    for card in sorted(total_side_counts):
        total = total_side_counts[card]
        decks_playing = decks_with_side[card]
        percent = (decks_playing / num_decks) * 100
        average = total / decks_playing

        print(f"{card} appears {average:.2f} copies in {percent:.2f}% of decks")
        
    make_core = input("\nGenerate core deck? (y/n): ").lower()

    if make_core == "y":
        threshold = float(input("Enter percentage threshold (e.g. 100, 80, 70): "))
    
    generate_core_deck(
        total_main_counts, decks_with_main,
        total_side_counts, decks_with_side,
        num_decks,
        threshold
    )


def generate_core_deck(total_main_counts, decks_with_main,
                       total_side_counts, decks_with_side,
                       num_decks, threshold_percent):

    core_main = {}
    core_side = {}

    excluded_main = []
    excluded_side = []

    main_total = 0
    side_total = 0

    threshold_decimal = threshold_percent / 100

    # -------- MAINBOARD --------
    for card in total_main_counts:
        decks_playing = decks_with_main[card]
        percent = decks_playing / num_decks

        if percent >= threshold_decimal:
            average = total_main_counts[card] / decks_playing
            rounded = round(average)

            if main_total + rounded <= 60:
                core_main[card] = rounded
                main_total += rounded
            else:
                excluded_main.append(card)
        else:
            excluded_main.append(card)

    # -------- SIDEBOARD --------
    for card in total_side_counts:
        decks_playing = decks_with_side[card]
        percent = decks_playing / num_decks

        if percent >= threshold_decimal:
            average = total_side_counts[card] / decks_playing
            rounded = round(average)

            if side_total + rounded <= 15:
                core_side[card] = rounded
                side_total += rounded
            else:
                excluded_side.append(card)
        else:
            excluded_side.append(card)

    # -------- PRINT RESULTS --------

    print(f"\n====== GENERATED CORE DECK (≥ {threshold_percent}%) ======\n")

    print("---- MAINBOARD ----\n")
    for card in sorted(core_main):
        print(f"{core_main[card]} {card}")

    print(f"\nMainboard: {main_total}/60 cards")
    print(f"Free mainboard spots: {60 - main_total}")

    print("\n---- SIDEBOARD ----\n")
    for card in sorted(core_side):
        print(f"{core_side[card]} {card}")

    print(f"\nSideboard: {side_total}/15 cards")
    print(f"Free sideboard spots: {15 - side_total}")

    print("\n---- NOT INCLUDED (Mainboard) ----")
    for card in sorted(excluded_main):
        print(card)

    print("\n---- NOT INCLUDED (Sideboard) ----")
    for card in sorted(excluded_side):
        print(card)


if __name__ == "__main__":
    analyze_folder()
