#!/usr/bin/env python3

import json
import os
import sys
import random
import time
from datetime import datetime

# Try to import genanki
try:
    import genanki
except ImportError:
    print("Error: genanki is not installed.")
    print("Please install it with: pip3 install genanki")
    sys.exit(1)

def load_owl_cards():
    """Load cards from owl_created_cards/new_cards.json"""
    cards_file = os.path.join(os.path.dirname(__file__), 'owl_created_cards', 'new_cards.json')
    
    if not os.path.exists(cards_file):
        print(f"No cards found at {cards_file}")
        return None
    
    with open(cards_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_anki_package(cards_data):
    """Create an APKG file from the cards data"""
    
    # Create a unique model ID based on timestamp
    model_id = int(time.time() * 1000)
    
    # Define the note model (Basic model with Front/Back fields)
    basic_model = genanki.Model(
        model_id,
        'Owl Cards Basic Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ])
    
    # Define the cloze model
    cloze_model = genanki.Model(
        model_id + 1,
        'Owl Cards Cloze Model',
        fields=[
            {'name': 'Text'},
            {'name': 'Extra'},
        ],
        templates=[
            {
                'name': 'Cloze',
                'qfmt': '{{cloze:Text}}',
                'afmt': '{{cloze:Text}}<br>{{Extra}}',
            },
        ],
        model_type=genanki.Model.CLOZE)
    
    # Group cards by deck
    decks = {}
    
    for card in cards_data.get('cards', []):
        deck_name = card.get('deck', 'Default')
        
        if deck_name not in decks:
            # Create a unique deck ID
            deck_id = int(time.time() * 1000) + len(decks)
            decks[deck_name] = genanki.Deck(deck_id, deck_name)
        
        deck = decks[deck_name]
        
        # Create the note based on card type
        if card.get('type') == 'BasicCard':
            fields = card.get('fields', {})
            note = genanki.Note(
                model=basic_model,
                fields=[
                    fields.get('front', ''),
                    fields.get('back', '')
                ],
                tags=card.get('tags', [])
            )
            deck.add_note(note)
            
        elif card.get('type') == 'ClozeCard':
            fields = card.get('fields', {})
            text = fields.get('text', '')
            
            # Convert Owl's {{cloze}} format to Anki's {{c1::cloze}} format
            cloze_num = 1
            while '{{' in text and '}}' in text:
                text = text.replace('{{', f'{{{{c{cloze_num}::', 1)
                text = text.replace('}}', '}}', 1)
                cloze_num += 1
            
            note = genanki.Note(
                model=cloze_model,
                fields=[text, ''],
                tags=card.get('tags', [])
            )
            deck.add_note(note)
    
    # Create the package
    package = genanki.Package(list(decks.values()))
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'owl_cards_export_{timestamp}.apkg'
    
    # Save the package
    package.write_to_file(filename)
    
    return filename, decks

def main():
    print("Loading cards from owl_created_cards...")
    cards_data = load_owl_cards()
    
    if not cards_data:
        print("No cards to export.")
        return
    
    total_cards = len(cards_data.get('cards', []))
    print(f"Found {total_cards} cards to export")
    
    if total_cards == 0:
        print("No cards to export.")
        return
    
    print("\nCreating Anki package...")
    filename, decks = create_anki_package(cards_data)
    
    print(f"\n✓ Successfully created: {filename}")
    print(f"\nExported {len(decks)} deck(s):")
    for deck_name, deck in decks.items():
        print(f"  - {deck_name}: {len(deck.notes)} cards")
    
    print(f"\nYou can now import '{filename}' into Anki!")

if __name__ == "__main__":
    main()