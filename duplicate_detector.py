#!/usr/bin/env python3
"""
Detect and remove duplicate cards from Anki decks.
Identifies duplicates based on various criteria and suggests removals.
"""

import json
import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import difflib

class DuplicateDetector:
    """Detect and handle duplicate cards in Anki decks."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.duplicates = []
        self.stats = {
            'total_cards': 0,
            'exact_duplicates': 0,
            'similar_duplicates': 0,
            'reverse_duplicates': 0
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation at end
        text = text.rstrip('.,!?;:')
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def find_duplicates(self, cards: List[Dict]) -> Dict:
        """Find all types of duplicates in the deck."""
        self.stats['total_cards'] = len(cards)
        duplicates = {
            'exact': [],
            'similar': [],
            'reverse': [],
            'substring': []
        }
        
        # Group by normalized front text
        front_groups = defaultdict(list)
        for i, card in enumerate(cards):
            front = card.get('fields', {}).get('Front', '') if 'fields' in card else card.get('front', '')
            front_norm = self.normalize_text(front)
            if front_norm:
                front_groups[front_norm].append((i, card))
        
        # Find exact duplicates
        for front_norm, group in front_groups.items():
            if len(group) > 1:
                duplicates['exact'].append({
                    'type': 'exact_front',
                    'cards': [{'index': idx, 'card': card} for idx, card in group],
                    'reason': f'Identical front text: "{front_norm}"'
                })
                self.stats['exact_duplicates'] += len(group) - 1
        
        # Find similar and reverse duplicates
        cards_list = list(enumerate(cards))
        for i, (idx1, card1) in enumerate(cards_list):
            front1 = card1.get('fields', {}).get('Front', '') if 'fields' in card1 else card1.get('front', '')
            back1 = card1.get('fields', {}).get('Back', '') if 'fields' in card1 else card1.get('back', '')
            
            for idx2, card2 in cards_list[i+1:]:
                front2 = card2.get('fields', {}).get('Front', '') if 'fields' in card2 else card2.get('front', '')
                back2 = card2.get('fields', {}).get('Back', '') if 'fields' in card2 else card2.get('back', '')
                
                # Check for reverse duplicates (front1 = back2, back1 = front2)
                if (self.normalize_text(front1) == self.normalize_text(back2) and 
                    self.normalize_text(back1) == self.normalize_text(front2)):
                    duplicates['reverse'].append({
                        'type': 'reverse',
                        'cards': [
                            {'index': idx1, 'card': card1},
                            {'index': idx2, 'card': card2}
                        ],
                        'reason': 'Cards are reverses of each other'
                    })
                    self.stats['reverse_duplicates'] += 1
                
                # Check for similar cards (high similarity but not exact)
                elif front1 and front2:
                    similarity = self.calculate_similarity(front1, front2)
                    if similarity >= self.similarity_threshold and similarity < 1.0:
                        duplicates['similar'].append({
                            'type': 'similar',
                            'cards': [
                                {'index': idx1, 'card': card1},
                                {'index': idx2, 'card': card2}
                            ],
                            'similarity': similarity,
                            'reason': f'Similar front text ({similarity:.0%} match)'
                        })
                        self.stats['similar_duplicates'] += 1
                
                # Check for substring duplicates
                if len(front1) > 10 and len(front2) > 10:
                    if front1 in front2:
                        duplicates['substring'].append({
                            'type': 'substring',
                            'cards': [
                                {'index': idx1, 'card': card1, 'role': 'contained'},
                                {'index': idx2, 'card': card2, 'role': 'container'}
                            ],
                            'reason': f'First card is contained in second'
                        })
                    elif front2 in front1:
                        duplicates['substring'].append({
                            'type': 'substring',
                            'cards': [
                                {'index': idx1, 'card': card1, 'role': 'container'},
                                {'index': idx2, 'card': card2, 'role': 'contained'}
                            ],
                            'reason': f'Second card is contained in first'
                        })
        
        return duplicates
    
    def generate_removal_suggestions(self, duplicates: Dict) -> List[Dict]:
        """Generate suggestions for which duplicates to remove."""
        suggestions = []
        cards_to_remove = set()
        
        # Handle exact duplicates - keep the first one
        for dup_group in duplicates['exact']:
            cards = dup_group['cards']
            # Keep the first card, suggest removing the rest
            for card_info in cards[1:]:
                if card_info['index'] not in cards_to_remove:
                    cards_to_remove.add(card_info['index'])
                    suggestions.append({
                        'action': 'remove',
                        'index': card_info['index'],
                        'reason': dup_group['reason'],
                        'duplicate_of': cards[0]['index']
                    })
        
        # Handle reverse duplicates - suggest keeping one or merging
        for dup_group in duplicates['reverse']:
            cards = dup_group['cards']
            if cards[0]['index'] not in cards_to_remove and cards[1]['index'] not in cards_to_remove:
                suggestions.append({
                    'action': 'merge_reverse',
                    'indices': [cards[0]['index'], cards[1]['index']],
                    'reason': 'These cards are reverses - consider keeping both or creating a reversible card type'
                })
        
        # Handle similar duplicates - require manual review
        for dup_group in duplicates['similar']:
            cards = dup_group['cards']
            if cards[0]['index'] not in cards_to_remove and cards[1]['index'] not in cards_to_remove:
                suggestions.append({
                    'action': 'review',
                    'indices': [cards[0]['index'], cards[1]['index']],
                    'similarity': dup_group['similarity'],
                    'reason': dup_group['reason'],
                    'suggestion': 'Manual review needed - cards are similar but not identical'
                })
        
        # Handle substring duplicates
        for dup_group in duplicates['substring']:
            cards = dup_group['cards']
            contained_idx = next(c['index'] for c in cards if c['role'] == 'contained')
            if contained_idx not in cards_to_remove:
                suggestions.append({
                    'action': 'review',
                    'indices': [c['index'] for c in cards],
                    'reason': dup_group['reason'],
                    'suggestion': 'Consider removing the shorter card or combining them'
                })
        
        return suggestions
    
    def apply_removals(self, cards: List[Dict], suggestions: List[Dict]) -> List[Dict]:
        """Apply removal suggestions to create a cleaned deck."""
        # Get indices to remove
        indices_to_remove = set()
        for suggestion in suggestions:
            if suggestion['action'] == 'remove':
                indices_to_remove.add(suggestion['index'])
        
        # Create new card list without duplicates
        cleaned_cards = []
        for i, card in enumerate(cards):
            if i not in indices_to_remove:
                cleaned_cards.append(card)
        
        return cleaned_cards
    
    def generate_report(self, duplicates: Dict, suggestions: List[Dict]) -> str:
        """Generate a human-readable report of duplicates found."""
        report = []
        report.append("# Duplicate Detection Report\n")
        report.append(f"Total cards analyzed: {self.stats['total_cards']}")
        report.append(f"Exact duplicates found: {self.stats['exact_duplicates']}")
        report.append(f"Similar cards found: {self.stats['similar_duplicates']}")
        report.append(f"Reverse pairs found: {self.stats['reverse_duplicates']}\n")
        
        # Removal suggestions
        remove_count = sum(1 for s in suggestions if s['action'] == 'remove')
        review_count = sum(1 for s in suggestions if s['action'] == 'review')
        
        report.append(f"## Suggested Actions")
        report.append(f"- Cards to remove: {remove_count}")
        report.append(f"- Cards to review: {review_count}\n")
        
        # Detail exact duplicates
        if duplicates['exact']:
            report.append("## Exact Duplicates")
            for i, dup in enumerate(duplicates['exact'][:10]):  # Show first 10
                front = dup['cards'][0]['card'].get('fields', {}).get('Front', '')[:50]
                report.append(f"{i+1}. '{front}...' appears {len(dup['cards'])} times")
            if len(duplicates['exact']) > 10:
                report.append(f"... and {len(duplicates['exact']) - 10} more groups\n")
        
        # Detail similar cards
        if duplicates['similar']:
            report.append("\n## Similar Cards (Manual Review Needed)")
            for i, dup in enumerate(duplicates['similar'][:5]):  # Show first 5
                card1 = dup['cards'][0]['card']
                card2 = dup['cards'][1]['card']
                front1 = card1.get('fields', {}).get('Front', '')[:40]
                front2 = card2.get('fields', {}).get('Front', '')[:40]
                report.append(f"{i+1}. {dup['similarity']:.0%} similar:")
                report.append(f"   - '{front1}...'")
                report.append(f"   - '{front2}...'")
            if len(duplicates['similar']) > 5:
                report.append(f"... and {len(duplicates['similar']) - 5} more pairs\n")
        
        return '\n'.join(report)


def process_deck_for_duplicates(deck_path: str, output_path: str = None):
    """Process a deck JSON file and remove duplicates."""
    # Load deck
    with open(deck_path, 'r') as f:
        deck_data = json.load(f)
    
    # Extract cards (handle both notes and cards format)
    if 'cards' in deck_data:
        cards = deck_data['cards']
    elif 'notes' in deck_data:
        cards = deck_data['notes']
    else:
        raise ValueError("No cards or notes found in deck")
    
    # Detect duplicates
    detector = DuplicateDetector()
    duplicates = detector.find_duplicates(cards)
    suggestions = detector.generate_removal_suggestions(duplicates)
    
    # Generate report
    report = detector.generate_report(duplicates, suggestions)
    print(report)
    
    # Save report
    report_path = output_path or deck_path.replace('.json', '_duplicate_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Create cleaned deck
    cleaned_cards = detector.apply_removals(cards, suggestions)
    
    # Save cleaned deck
    cleaned_deck = deck_data.copy()
    if 'cards' in cleaned_deck:
        cleaned_deck['cards'] = cleaned_cards
    else:
        cleaned_deck['notes'] = cleaned_cards
    
    cleaned_path = deck_path.replace('.json', '_cleaned.json')
    with open(cleaned_path, 'w') as f:
        json.dump(cleaned_deck, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    print(f"Cleaned deck saved to: {cleaned_path}")
    print(f"Removed {len(cards) - len(cleaned_cards)} duplicate cards")
    
    # Save removal suggestions for review
    suggestions_path = deck_path.replace('.json', '_suggestions.json')
    with open(suggestions_path, 'w') as f:
        json.dump({
            'suggestions': suggestions,
            'duplicates': duplicates,
            'stats': detector.stats
        }, f, indent=2)
    print(f"Detailed suggestions saved to: {suggestions_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python duplicate_detector.py <deck.json>")
        sys.exit(1)
    
    process_deck_for_duplicates(sys.argv[1])