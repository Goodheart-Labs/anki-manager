#!/usr/bin/env python3
"""Add French vocabulary cards from notes."""

from mochi_api import MochiAPI

DECK_ID = "5LvMpMNe"  # French deck

cards = [
    ("la viande", "meat (f)"),
    ("le mari", "husband (m)"),
    ("le porc", "pork (m)"),
    ("ne...plus", "not anymore"),
    ("les sacs de courses", "shopping bags (m)"),
    ("sert", "serves (from servir)"),
    ("propose", "offer"),
    ("laisser tomber", "forget it / drop it"),
    ("les haricots noirs", "black beans (m)"),
    ("végétal", "plant-based"),
    ("en veut", "wants some (tu en veux? = do you want some?)"),
    ("le Kenya", "Kenya (m)"),
    ("je devrais", "I should (from devoir)"),
    ("le coup de pied", "kick - literally 'blow of foot' (m)"),
    ("mauvais / mauvaise", "bad (m/f)"),
    ("les chaussures", "shoes (f)"),
]

if __name__ == "__main__":
    mochi = MochiAPI()

    print(f"Adding {len(cards)} cards to deck {DECK_ID}...\n")

    for front, back in cards:
        try:
            card = mochi.create_basic_card(front, back, deck_id=DECK_ID)
            print(f"✓ {front}")
        except Exception as e:
            print(f"✗ {front}: {e}")

    mochi.close()
    print("\nDone!")
