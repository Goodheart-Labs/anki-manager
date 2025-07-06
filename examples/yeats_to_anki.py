#!/usr/bin/env python3
from datetime import datetime

def parse_poem_to_cards(poem_text):
    """Parse poem text into line-by-line cards."""
    cards = []
    lines = []
    
    # First, collect all non-empty lines
    for line in poem_text.strip().split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    
    # Create cards where each line leads to the next
    for i in range(len(lines) - 1):
        front = lines[i]
        back = lines[i + 1]
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
    poem = """Turning and turning in the widening gyre   
The falcon cannot hear the falconer;
Things fall apart; the centre cannot hold;
Mere anarchy is loosed upon the world,
The blood-dimmed tide is loosed, and everywhere   
The ceremony of innocence is drowned;
The best lack all conviction, while the worst   
Are full of passionate intensity.

Surely some revelation is at hand;
Surely the Second Coming is at hand.   
The Second Coming! Hardly are those words out   
When a vast image out of Spiritus Mundi
Troubles my sight: somewhere in sands of the desert   
A shape with lion body and the head of a man,   
A gaze blank and pitiless as the sun,   
Is moving its slow thighs, while all about it   
Reel shadows of the indignant desert birds.   
The darkness drops again; but now I know   
That twenty centuries of stony sleep
Were vexed to nightmare by a rocking cradle,   
And what rough beast, its hour come round at last,   
Slouches towards Bethlehem to be born?"""
    
    # Parse the poem into cards
    cards = parse_poem_to_cards(poem)
    
    print(f"Parsed {len(cards)} cards from Yeats' 'The Second Coming':\n")
    
    # Display first few cards as examples
    for i, (front, back) in enumerate(cards[:5], 1):
        print(f"Card {i}:")
        print(f"  Front: {front}")
        print(f"  Back: {back}")
        print()
    
    if len(cards) > 5:
        print(f"... and {len(cards) - 5} more cards\n")
    
    # Export to Anki format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"yeats_second_coming_{timestamp}.txt"
    
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