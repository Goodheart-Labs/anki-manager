#!/usr/bin/env python3
"""
Simple duplicate detector for CrowdAnki format decks.
Just detects and reports duplicates without modifications.
"""

import json
import re
from collections import defaultdict
from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    """Remove HTML tags from text."""
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

def normalize_text(text):
    """Normalize text for comparison."""
    # Strip HTML
    text = strip_html(text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.rstrip('.,!?;:')
    return text

def extract_all_notes(deck_data, deck_path=""):
    """Recursively extract all notes from deck and subdecks."""
    all_notes = []
    
    current_path = deck_path + "/" + deck_data.get('name', '') if deck_path else deck_data.get('name', 'Root')
    
    # Get notes from current deck
    for note in deck_data.get('notes', []):
        all_notes.append((current_path, note))
    
    # Recursively get notes from children
    for child in deck_data.get('children', []):
        all_notes.extend(extract_all_notes(child, current_path))
    
    return all_notes

def detect_duplicates(deck_path):
    """Detect duplicates in a CrowdAnki deck."""
    # Load deck
    with open(deck_path, 'r', encoding='utf-8') as f:
        deck_data = json.load(f)
    
    # Extract all notes
    all_notes = extract_all_notes(deck_data)
    print(f"Total notes found: {len(all_notes)}")
    
    # Group by normalized front text
    duplicates = defaultdict(list)
    
    for deck_path, note in all_notes:
        if note.get('fields') and len(note['fields']) > 0:
            front = note['fields'][0]
            front_norm = normalize_text(front)
            
            if front_norm:  # Skip empty cards
                duplicates[front_norm].append({
                    'deck': deck_path,
                    'front': front,
                    'back': note['fields'][1] if len(note['fields']) > 1 else '',
                    'tags': note.get('tags', []),
                    'guid': note.get('guid', '')
                })
    
    # Find and report duplicates
    duplicate_groups = []
    for front_norm, notes in duplicates.items():
        if len(notes) > 1:
            duplicate_groups.append({
                'normalized': front_norm,
                'count': len(notes),
                'notes': notes
            })
    
    # Sort by count (most duplicates first)
    duplicate_groups.sort(key=lambda x: x['count'], reverse=True)
    
    # Print report
    print(f"\nFound {len(duplicate_groups)} groups of duplicates")
    print(f"Total duplicate cards: {sum(g['count'] - 1 for g in duplicate_groups)}")
    
    print("\n" + "="*80)
    print("DUPLICATE REPORT")
    print("="*80 + "\n")
    
    for i, group in enumerate(duplicate_groups, 1):
        front_preview = strip_html(group['notes'][0]['front'])[:80]
        print(f"{i}. \"{front_preview}...\" - {group['count']} copies")
        
        for note in group['notes']:
            tags = ', '.join(note['tags']) if note['tags'] else 'no tags'
            print(f"   - In: {note['deck']} [{tags}]")
        print()
        
        if i >= 20 and len(duplicate_groups) > 20:
            print(f"... and {len(duplicate_groups) - 20} more groups of duplicates")
            break
    
    # Save detailed report
    import os
    report_filename = os.path.basename(deck_path).replace('.json', '_duplicates.json')
    report_path = os.path.join(os.path.dirname(deck_path), report_filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_notes': len(all_notes),
            'duplicate_groups': len(duplicate_groups),
            'total_duplicates': sum(g['count'] - 1 for g in duplicate_groups),
            'duplicates': duplicate_groups
        }, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python detect_duplicates.py <deck.json>")
        sys.exit(1)
    
    detect_duplicates(sys.argv[1])