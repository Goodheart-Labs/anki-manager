#!/usr/bin/env python3
from typing import List, Tuple, Optional
import re
from html.parser import HTMLParser
from html5lib import parse
import sys
import os
from datetime import datetime

class AnkiCard:
    def __init__(self, front: str, back: str):
        self.front = front.strip()
        self.back = back.strip()

class AnkiValidator:
    def __init__(self):
        self.max_field_length = 131072  # Anki's default maximum field length
        self.html_parser = HTMLParser()
        
    def validate_html(self, text: str) -> List[str]:
        """Validate HTML content in the text."""
        errors = []
        try:
            # Try to parse as HTML to catch malformed HTML
            parse(text)
        except Exception as e:
            errors.append(f"Invalid HTML: {str(e)}")
        return errors

    def check_special_characters(self, text: str) -> List[str]:
        """Check for potentially problematic characters."""
        errors = []
        # Check for null bytes
        if '\x00' in text:
            errors.append("Contains null bytes")
        
        # Check for other potentially problematic characters
        problematic = re.findall(r'[\x00-\x1F\x7F-\x9F]', text)
        if problematic:
            errors.append(f"Contains control characters: {', '.join(hex(ord(c)) for c in problematic)}")
        
        return errors

    def validate_card(self, card: AnkiCard) -> List[str]:
        """Validate a single Anki card."""
        errors = []
        
        # Check field lengths
        if len(card.front) > self.max_field_length:
            errors.append("Front field exceeds maximum length")
        if len(card.back) > self.max_field_length:
            errors.append("Back field exceeds maximum length")
        
        # Check for empty fields
        if not card.front:
            errors.append("Front field is empty")
        if not card.back:
            errors.append("Back field is empty")
        
        # Validate HTML in both fields
        errors.extend(self.validate_html(card.front))
        errors.extend(self.validate_html(card.back))
        
        # Check for special characters
        errors.extend(self.check_special_characters(card.front))
        errors.extend(self.check_special_characters(card.back))
        
        return errors

    def parse_cards(self, text: str) -> List[AnkiCard]:
        """Parse text into AnkiCard objects."""
        cards = []
        current_card = {"front": "", "back": ""}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current_card["front"] and current_card["back"]:
                    cards.append(AnkiCard(current_card["front"], current_card["back"]))
                    current_card = {"front": "", "back": ""}
                continue
                
            # Case-insensitive check for Front: and Back:
            lower_line = line.lower()
            if lower_line.startswith("front:"):
                current_card["front"] = line[6:].strip()
            elif lower_line.startswith("back:"):
                current_card["back"] = line[5:].strip()
        
        # Add the last card if it exists
        if current_card["front"] and current_card["back"]:
            cards.append(AnkiCard(current_card["front"], current_card["back"]))
        
        return cards

    def validate_text(self, text: str) -> Tuple[List[AnkiCard], List[str]]:
        """Validate text containing Anki cards."""
        cards = self.parse_cards(text)
        errors = []
        
        # Validate each card
        for i, card in enumerate(cards, 1):
            card_errors = self.validate_card(card)
            if card_errors:
                errors.append(f"Card {i} has the following issues:")
                errors.extend(f"  - {error}" for error in card_errors)
        
        return cards, errors

    def export_to_anki_format(self, cards: List[AnkiCard], output_file: str) -> bool:
        """Export cards to Anki's import format (comma-separated with quotes)."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write header for Anki import
                f.write("#separator:comma\n")
                f.write("#html:true\n")
                f.write("#columns:front,back\n\n")
                
                # Write each card with quotes
                for card in cards:
                    f.write(f'"{card.front}","{card.back}"\n')
            return True
        except Exception as e:
            print(f"Error exporting cards: {str(e)}")
            return False

def main():
    if len(sys.argv) > 1:
        # Read from file if filename provided
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # Read from stdin
        print("Enter your Anki cards (press Ctrl+D or Ctrl+Z when done):")
        text = sys.stdin.read()
    
    validator = AnkiValidator()
    cards, errors = validator.validate_text(text)
    
    if errors:
        print("\nValidation Errors:")
        for error in errors:
            print(error)
        print(f"\nFound {len(errors)} issues in {len(cards)} cards.")
    else:
        print(f"\nAll {len(cards)} cards are valid!")
        
        # Automatically export valid cards
        if len(cards) > 0:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/data/anki_cards_{timestamp}.txt"
            
            if validator.export_to_anki_format(cards, output_file):
                print(f"\nCards exported to anki_cards_{timestamp}.txt")
                print("\nTo import these cards into Anki:")
                print("1. Open Anki")
                print("2. Click File -> Import")
                print(f"3. Select the file: anki_cards_{timestamp}.txt")
                print("4. Make sure 'Basic' is selected as the note type")
                print("5. Click Import")
            else:
                print("\nFailed to export cards. Please check the error message above.")

if __name__ == "__main__":
    main() 