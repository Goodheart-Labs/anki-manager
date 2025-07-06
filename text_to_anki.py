#!/usr/bin/env python3
from datetime import datetime
from typing import List, Tuple, Optional
import re

class TextToAnki:
    """Convert various text formats to Anki flashcards."""
    
    def __init__(self):
        self.cards = []
    
    def parse_line_by_line(self, text: str) -> List[Tuple[str, str]]:
        """Parse text where each line becomes front of card, next line is back."""
        cards = []
        lines = []
        
        # Collect all non-empty lines
        for line in text.strip().split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
        
        # Create cards where each line leads to the next
        for i in range(len(lines) - 1):
            cards.append((lines[i], lines[i + 1]))
        
        return cards
    
    def parse_with_delimiter(self, text: str, delimiter: str = "    ") -> List[Tuple[str, str]]:
        """Parse text where front and back are separated by delimiter on same line."""
        cards = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = [part.strip() for part in line.split(delimiter)]
            
            if len(parts) >= 2:
                front = parts[0]
                back = delimiter.join(parts[1:])
                
                if front and back:
                    cards.append((front, back))
        
        return cards
    
    def parse_verse_by_verse(self, text: str) -> List[Tuple[str, str]]:
        """Parse text where blank lines separate verses, each verse becomes a card."""
        cards = []
        verses = text.strip().split('\n\n')
        
        for i in range(len(verses) - 1):
            if verses[i].strip() and verses[i + 1].strip():
                cards.append((verses[i].strip(), verses[i + 1].strip()))
        
        return cards
    
    def parse_cloze_deletion(self, text: str, pattern: str = r'\{(.+?)\}') -> List[Tuple[str, str]]:
        """Create cloze deletion cards from text with {bracketed} words."""
        cards = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            matches = re.findall(pattern, line)
            if matches:
                for match in matches:
                    # Create card with cloze
                    front = line.replace(f'{{{match}}}', '[...]')
                    back = match
                    cards.append((front, back))
        
        return cards
    
    def parse_numbered_list(self, text: str) -> List[Tuple[str, str]]:
        """Parse numbered list where number is front, content is back."""
        cards = []
        pattern = r'^(\d+\.?\s*)(.*)'
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            match = re.match(pattern, line)
            if match:
                number = match.group(1).strip()
                content = match.group(2).strip()
                if content:
                    cards.append((number.rstrip('.'), content))
        
        return cards
    
    def parse_qa_format(self, text: str) -> List[Tuple[str, str]]:
        """Parse Q&A format (Q: question, A: answer)."""
        cards = []
        lines = text.strip().split('\n')
        
        current_q = None
        current_a = []
        
        for line in lines:
            line = line.strip()
            
            if line.lower().startswith('q:') or line.lower().startswith('question:'):
                # Save previous Q&A if exists
                if current_q and current_a:
                    cards.append((current_q, '\n'.join(current_a)))
                
                # Start new question
                current_q = line.split(':', 1)[1].strip()
                current_a = []
            
            elif line.lower().startswith('a:') or line.lower().startswith('answer:'):
                current_a.append(line.split(':', 1)[1].strip())
            
            elif current_a and line:
                # Continue answer on next line
                current_a.append(line)
        
        # Don't forget last Q&A
        if current_q and current_a:
            cards.append((current_q, '\n'.join(current_a)))
        
        return cards
    
    def export_to_anki(self, cards: List[Tuple[str, str]], filename: Optional[str] = None, 
                       format: str = 'tab') -> str:
        """Export cards to Anki-compatible format."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anki_cards_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if format == 'csv':
                    # CSV format with quotes
                    f.write("#separator:comma\n")
                    f.write("#html:true\n")
                    f.write("#columns:front,back\n\n")
                    
                    for front, back in cards:
                        # Escape quotes
                        front = front.replace('"', '""')
                        back = back.replace('"', '""')
                        f.write(f'"{front}","{back}"\n')
                else:
                    # Default tab-separated format
                    for front, back in cards:
                        # Replace tabs with spaces
                        front = front.replace('\t', ' ')
                        back = back.replace('\t', ' ')
                        f.write(f'{front}\t{back}\n')
            
            return filename
        except Exception as e:
            raise Exception(f"Error exporting cards: {str(e)}")


def main():
    """Example usage of TextToAnki."""
    converter = TextToAnki()
    
    # Example text
    example_poem = """Roses are red
Violets are blue
Sugar is sweet
And so are you"""
    
    print("Text to Anki Converter")
    print("=" * 50)
    
    # Demonstrate different parsing methods
    print("\n1. Line-by-line parsing:")
    cards = converter.parse_line_by_line(example_poem)
    for i, (front, back) in enumerate(cards[:2], 1):
        print(f"   Card {i}: '{front}' → '{back}'")
    
    # Example with delimiter
    example_delimited = """Front 1    Back 1
Front 2    Back 2"""
    
    print("\n2. Delimiter parsing:")
    cards = converter.parse_with_delimiter(example_delimited)
    for i, (front, back) in enumerate(cards, 1):
        print(f"   Card {i}: '{front}' → '{back}'")
    
    # Example with cloze
    example_cloze = "The {capital} of France is {Paris}."
    
    print("\n3. Cloze deletion parsing:")
    cards = converter.parse_cloze_deletion(example_cloze)
    for i, (front, back) in enumerate(cards, 1):
        print(f"   Card {i}: '{front}' → '{back}'")
    
    print("\nUse the TextToAnki class methods to convert your text!")

if __name__ == "__main__":
    main()