#!/usr/bin/env python3
from datetime import datetime
from typing import List, Tuple, Optional
import re
import os
from text_to_anki import TextToAnki

class AnkiConverter:
    """Enhanced converter that includes validation and organized exports."""
    
    def __init__(self, export_dir: str = "anki_exports"):
        self.export_dir = export_dir
        self.text_converter = TextToAnki()
        self.ensure_export_dir()
    
    def ensure_export_dir(self):
        """Create export directory if it doesn't exist."""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def validate_cards(self, cards: List[Tuple[str, str]]) -> Tuple[bool, List[str]]:
        """Basic validation of cards."""
        errors = []
        
        for i, (front, back) in enumerate(cards, 1):
            if not front or not front.strip():
                errors.append(f"Card {i}: Empty front")
            if not back or not back.strip():
                errors.append(f"Card {i}: Empty back")
            if len(front) > 131072:
                errors.append(f"Card {i}: Front exceeds max length")
            if len(back) > 131072:
                errors.append(f"Card {i}: Back exceeds max length")
            if '\x00' in front or '\x00' in back:
                errors.append(f"Card {i}: Contains null bytes")
        
        return len(errors) == 0, errors
    
    def convert_text(self, text: str, title: str, parse_method: str = "line_by_line") -> str:
        """Convert text to Anki cards with validation."""
        # Parse based on method
        if parse_method == "line_by_line":
            cards = self.text_converter.parse_line_by_line(text)
        elif parse_method == "delimiter":
            cards = self.text_converter.parse_with_delimiter(text)
        elif parse_method == "verse":
            cards = self.text_converter.parse_verse_by_verse(text)
        elif parse_method == "cloze":
            cards = self.text_converter.parse_cloze_deletion(text)
        elif parse_method == "numbered":
            cards = self.text_converter.parse_numbered_list(text)
        elif parse_method == "qa":
            cards = self.text_converter.parse_qa_format(text)
        else:
            raise ValueError(f"Unknown parse method: {parse_method}")
        
        print(f"\nParsed {len(cards)} cards from '{title}'")
        
        # Validate cards
        is_valid, errors = self.validate_cards(cards)
        
        if errors:
            print("\nValidation errors found:")
            for error in errors:
                print(f"  - {error}")
            
            if not is_valid:
                raise ValueError("Cards failed validation")
        else:
            print("✓ All cards passed validation")
        
        # Display sample cards
        print("\nSample cards:")
        for i, (front, back) in enumerate(cards[:3], 1):
            print(f"Card {i}:")
            print(f"  Front: {front[:50]}{'...' if len(front) > 50 else ''}")
            print(f"  Back: {back[:50]}{'...' if len(back) > 50 else ''}")
        
        if len(cards) > 3:
            print(f"... and {len(cards) - 3} more cards")
        
        # Export to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = os.path.join(self.export_dir, f"{safe_title}_{timestamp}.txt")
        
        exported_file = self.text_converter.export_to_anki(cards, filename)
        
        print(f"\n✓ Cards exported to: {exported_file}")
        print("\nTo import into Anki:")
        print("1. Open Anki")
        print("2. Click File → Import")
        print(f"3. Navigate to: {os.path.abspath(exported_file)}")
        print("4. Select 'Basic' as the note type")
        print("5. Ensure 'Tab' is the field separator")
        print("6. Click Import")
        
        return exported_file


def convert_antony_speech():
    """Convert Mark Antony's speech to Anki cards."""
    speech = """Friends, Romans, countrymen, lend me your ears;
I come to bury Caesar, not to praise him.
The evil that men do lives after them;
The good is oft interred with their bones;
So let it be with Caesar. The noble Brutus
Hath told you Caesar was ambitious:
If it were so, it was a grievous fault,
And grievously hath Caesar answer'd it.
Here, under leave of Brutus and the rest–
For Brutus is an honourable man;
So are they all, all honourable men–
Come I to speak in Caesar's funeral.
He was my friend, faithful and just to me:
But Brutus says he was ambitious;
And Brutus is an honourable man.
He hath brought many captives home to Rome
Whose ransoms did the general coffers fill:
Did this in Caesar seem ambitious?
When that the poor have cried, Caesar hath wept:
Ambition should be made of sterner stuff:
Yet Brutus says he was ambitious;
And Brutus is an honourable man.
You all did see that on the Lupercal
I thrice presented him a kingly crown,
Which he did thrice refuse: was this ambition?
Yet Brutus says he was ambitious;
And, sure, he is an honourable man.
I speak not to disprove what Brutus spoke,
But here I am to speak what I do know.
You all did love him once, not without cause:
What cause withholds you then, to mourn for him?
O judgment! thou art fled to brutish beasts,
And men have lost their reason. Bear with me;
My heart is in the coffin there with Caesar,
And I must pause till it come back to me."""
    
    converter = AnkiConverter()
    converter.convert_text(speech, "Mark Antony Speech", "line_by_line")


if __name__ == "__main__":
    convert_antony_speech()