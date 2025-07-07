#!/usr/bin/env python3
"""
Claude-friendly deck editor that can be used to review and improve Anki cards.
This integrates with any of the sync methods to enable AI-assisted card editing.
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class ClaudeDeckEditor:
    """Tools for Claude to analyze and improve Anki decks."""
    
    def __init__(self, deck_path: str):
        self.deck_path = deck_path
        self.load_deck()
    
    def load_deck(self):
        """Load deck from JSON format."""
        with open(self.deck_path, 'r') as f:
            self.deck = json.load(f)
    
    def analyze_card_quality(self, card: Dict) -> Dict[str, any]:
        """Analyze a card and suggest improvements."""
        analysis = {
            'id': card.get('id'),
            'issues': [],
            'suggestions': [],
            'quality_score': 100
        }
        
        front = card.get('front', '')
        back = card.get('back', '')
        
        # Check for common issues
        if len(front) < 5:
            analysis['issues'].append('Front side too short')
            analysis['quality_score'] -= 20
        
        if len(back) < 3:
            analysis['issues'].append('Back side too short')
            analysis['quality_score'] -= 20
        
        if front.lower() in back.lower() or back.lower() in front.lower():
            analysis['issues'].append('Answer visible in question')
            analysis['quality_score'] -= 30
        
        if '?' not in front and not front.startswith(('What', 'How', 'Why', 'When', 'Where', 'Who')):
            analysis['suggestions'].append('Consider phrasing as a question')
            analysis['quality_score'] -= 10
        
        if len(front) > 200:
            analysis['suggestions'].append('Consider breaking into multiple cards')
            analysis['quality_score'] -= 15
        
        # Check for formatting issues
        if re.search(r'<[^>]+>', front) or re.search(r'<[^>]+>', back):
            analysis['suggestions'].append('Contains HTML - ensure formatting is intentional')
        
        return analysis
    
    def suggest_improvements(self, card: Dict) -> Dict:
        """Generate improved version of a card."""
        improved = card.copy()
        analysis = self.analyze_card_quality(card)
        
        # Apply automatic improvements
        if 'Front side too short' in analysis['issues']:
            # Try to expand the question
            improved['front'] = self._expand_question(card['front'])
        
        if 'Answer visible in question' in analysis['issues']:
            # Remove answer from question
            improved['front'] = self._remove_answer_hints(card['front'], card['back'])
        
        improved['_metadata'] = {
            'original_quality': analysis['quality_score'],
            'improvement_notes': analysis['suggestions'],
            'edited_by': 'Claude',
            'edit_timestamp': datetime.now().isoformat()
        }
        
        return improved
    
    def _expand_question(self, question: str) -> str:
        """Expand a short question to be more clear."""
        if not question.endswith('?'):
            question += '?'
        
        # Simple expansion rules
        expansions = {
            'Capital': 'What is the capital of',
            'Population': 'What is the population of',
            'Year': 'In what year did',
            'Author': 'Who is the author of',
            'Meaning': 'What is the meaning of'
        }
        
        for short, expanded in expansions.items():
            if question.startswith(short):
                return question.replace(short, expanded, 1)
        
        return question
    
    def _remove_answer_hints(self, question: str, answer: str) -> str:
        """Remove answer hints from question."""
        # Simple approach - remove parenthetical hints
        question = re.sub(r'\([^)]*' + re.escape(answer) + r'[^)]*\)', '', question)
        question = re.sub(r'\s+', ' ', question).strip()
        return question
    
    def batch_analyze_deck(self) -> Dict:
        """Analyze entire deck and generate report."""
        report = {
            'total_cards': len(self.deck.get('cards', [])),
            'cards_needing_improvement': 0,
            'average_quality': 0,
            'common_issues': {},
            'suggested_actions': []
        }
        
        total_score = 0
        issue_counts = {}
        
        for card in self.deck.get('cards', []):
            analysis = self.analyze_card_quality(card)
            total_score += analysis['quality_score']
            
            if analysis['quality_score'] < 80:
                report['cards_needing_improvement'] += 1
            
            for issue in analysis['issues']:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        if report['total_cards'] > 0:
            report['average_quality'] = total_score / report['total_cards']
        
        report['common_issues'] = issue_counts
        
        # Generate suggested actions
        if report['average_quality'] < 70:
            report['suggested_actions'].append('Deck needs significant improvement')
        
        if issue_counts.get('Answer visible in question', 0) > 5:
            report['suggested_actions'].append('Review cards for answer leakage')
        
        return report
    
    def export_improvements(self, output_path: str):
        """Export improved deck to file."""
        improved_deck = {
            'name': self.deck.get('name', 'Improved Deck'),
            'cards': [],
            'metadata': {
                'improved_by': 'Claude',
                'improvement_date': datetime.now().isoformat(),
                'original_card_count': len(self.deck.get('cards', [])),
            }
        }
        
        for card in self.deck.get('cards', []):
            improved_card = self.suggest_improvements(card)
            improved_deck['cards'].append(improved_card)
        
        with open(output_path, 'w') as f:
            json.dump(improved_deck, f, indent=2)
        
        return output_path


def create_deck_improvement_pr(deck_url: str, improvements: Dict) -> str:
    """
    Create a GitHub PR with Claude's suggested improvements.
    This would be called by Claude when editing decks.
    """
    # This is a template for how Claude would submit improvements
    pr_body = f"""
## Deck Improvement Suggestions

I've analyzed the deck and found several areas for improvement:

### Summary
- **Cards analyzed**: {improvements['total_cards']}
- **Cards needing improvement**: {improvements['cards_needing_improvement']}
- **Average quality score**: {improvements['average_quality']:.1f}/100

### Common Issues Found
{chr(10).join(f"- {issue}: {count} cards" for issue, count in improvements['common_issues'].items())}

### Suggested Actions
{chr(10).join(f"- {action}" for action in improvements['suggested_actions'])}

### Changes Made
- Expanded short questions for clarity
- Removed answer hints from questions
- Improved formatting consistency
- Added question marks where appropriate

Please review the changes and merge if they look good!
"""
    
    return pr_body


if __name__ == "__main__":
    # Example usage
    editor = ClaudeDeckEditor("example_deck.json")
    report = editor.batch_analyze_deck()
    print(json.dumps(report, indent=2))
    
    # Export improvements
    editor.export_improvements("improved_deck.json")