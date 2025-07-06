#!/usr/bin/env python3
from datetime import datetime

def parse_lyrics_to_cards(lyrics_text):
    """Parse lyrics text where each line contains front and back separated by 4 spaces."""
    cards = []
    lines = lyrics_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Split by 4 or more spaces
        parts = [part.strip() for part in line.split('    ')]
        
        if len(parts) >= 2:
            # Take the first part as front and the rest joined as back
            front = parts[0]
            back = '    '.join(parts[1:])
            
            if front and back:
                cards.append((front, back))
    
    return cards

def export_to_anki_format(cards, output_file):
    """Export cards to Anki's import format (tab-separated)."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write each card with tab separation
            for front, back in cards:
                # Escape any existing tabs in the content
                front = front.replace('\t', ' ')
                back = back.replace('\t', ' ')
                f.write(f'{front}\t{back}\n')
        return True
    except Exception as e:
        print(f"Error exporting cards: {str(e)}")
        return False

def main():
    lyrics = """So, here's a story from A to Z    You wanna get with me, you gotta listen carefully
You wanna get with me, you gotta listen carefully    We got Em in the place who likes it in your face
We got Em in the place who likes it in your face    You got G like MC who likes it on a
You got G like MC who likes it on a    Easy V doesn't come for free, she's a real lady
Easy V doesn't come for free, she's a real lady    And as for me, ha you'll see
And as for me, ha you'll see    Slam your body down and wind it all around
Slam your body down and wind it all around    Slam your body down and wind it all around"""
    
    # Parse the lyrics into cards
    cards = parse_lyrics_to_cards(lyrics)
    
    print(f"Parsed {len(cards)} cards from lyrics:\n")
    
    # Display the cards
    for i, (front, back) in enumerate(cards, 1):
        print(f"Card {i}:")
        print(f"  Front: {front}")
        print(f"  Back: {back}")
        print()
    
    # Export to Anki format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"spice_girls_lyrics_{timestamp}.txt"
    
    if export_to_anki_format(cards, output_file):
        print(f"\nCards exported to {output_file}")
        print("\nTo import these cards into Anki:")
        print("1. Open Anki")
        print("2. Click File -> Import")
        print(f"3. Select the file: {output_file}")
        print("4. Make sure 'Basic' is selected as the note type")
        print("5. Make sure 'Tab' is selected as the field separator")
        print("6. Click Import")
    else:
        print("\nFailed to export cards.")

if __name__ == "__main__":
    main()