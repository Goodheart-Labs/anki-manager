#!/usr/bin/env python3
"""
Validate that only tags were changed in a deck JSON file.
Compares original and modified deck files to ensure content integrity.
"""

import json
import sys
from typing import Dict, List, Tuple
from collections import defaultdict

def extract_card_content(note: Dict) -> Tuple[str, ...]:
    """Extract the core content of a card (fields and guid)."""
    fields = tuple(note.get('fields', []))
    guid = note.get('guid', '')
    return (guid, fields)

def extract_all_cards(deck_data: Dict, path: str = "") -> List[Tuple[str, Dict]]:
    """Recursively extract all cards from deck and subdecks."""
    all_cards = []
    
    current_path = path + "/" + deck_data.get('name', '') if path else deck_data.get('name', 'Root')
    
    # Get notes from current deck
    for note in deck_data.get('notes', []):
        all_cards.append((current_path, note))
    
    # Recursively get notes from children
    for child in deck_data.get('children', []):
        all_cards.extend(extract_all_cards(child, current_path))
    
    return all_cards

def validate_tag_only_changes(original_file: str, modified_file: str) -> Dict:
    """
    Validate that only tags were changed between two deck files.
    Returns a report of changes.
    """
    # Load both files
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(modified_file, 'r', encoding='utf-8') as f:
        modified_data = json.load(f)
    
    # Extract all cards
    original_cards = extract_all_cards(original_data)
    modified_cards = extract_all_cards(modified_data)
    
    # Create lookup maps by GUID
    original_by_guid = {}
    for path, note in original_cards:
        guid = note.get('guid', '')
        if guid:
            original_by_guid[guid] = (path, note)
    
    modified_by_guid = {}
    for path, note in modified_cards:
        guid = note.get('guid', '')
        if guid:
            modified_by_guid[guid] = (path, note)
    
    # Track changes
    report = {
        'total_cards_original': len(original_cards),
        'total_cards_modified': len(modified_cards),
        'cards_added': [],
        'cards_removed': [],
        'content_changed': [],
        'tags_changed': [],
        'validation_passed': True
    }
    
    # Check for added/removed cards
    original_guids = set(original_by_guid.keys())
    modified_guids = set(modified_by_guid.keys())
    
    added_guids = modified_guids - original_guids
    removed_guids = original_guids - modified_guids
    
    for guid in added_guids:
        path, note = modified_by_guid[guid]
        report['cards_added'].append({
            'guid': guid,
            'path': path,
            'front': note.get('fields', [''])[0][:50] + '...'
        })
        report['validation_passed'] = False
    
    for guid in removed_guids:
        path, note = original_by_guid[guid]
        report['cards_removed'].append({
            'guid': guid,
            'path': path,
            'front': note.get('fields', [''])[0][:50] + '...'
        })
        report['validation_passed'] = False
    
    # Check existing cards for changes
    for guid in original_guids & modified_guids:
        orig_path, orig_note = original_by_guid[guid]
        mod_path, mod_note = modified_by_guid[guid]
        
        # Check if content changed
        orig_fields = orig_note.get('fields', [])
        mod_fields = mod_note.get('fields', [])
        
        if orig_fields != mod_fields:
            report['content_changed'].append({
                'guid': guid,
                'path': orig_path,
                'original_front': orig_fields[0][:50] + '...' if orig_fields else '',
                'modified_front': mod_fields[0][:50] + '...' if mod_fields else '',
                'field_changes': len([i for i, (o, m) in enumerate(zip(orig_fields, mod_fields)) if o != m])
            })
            report['validation_passed'] = False
        
        # Check if only tags changed
        orig_tags = set(orig_note.get('tags', []))
        mod_tags = set(mod_note.get('tags', []))
        
        if orig_tags != mod_tags:
            added_tags = mod_tags - orig_tags
            removed_tags = orig_tags - mod_tags
            
            report['tags_changed'].append({
                'guid': guid,
                'path': orig_path,
                'front': orig_fields[0][:50] + '...' if orig_fields else '',
                'tags_added': list(added_tags),
                'tags_removed': list(removed_tags),
                'original_tags': list(orig_tags),
                'modified_tags': list(mod_tags)
            })
    
    return report

def print_report(report: Dict):
    """Print a human-readable validation report."""
    print("=" * 80)
    print("TAG VALIDATION REPORT")
    print("=" * 80)
    print(f"\nTotal cards in original: {report['total_cards_original']}")
    print(f"Total cards in modified: {report['total_cards_modified']}")
    
    if report['validation_passed']:
        print("\n✅ VALIDATION PASSED: Only tags were changed!")
    else:
        print("\n❌ VALIDATION FAILED: Non-tag changes detected!")
    
    if report['cards_added']:
        print(f"\n⚠️  {len(report['cards_added'])} cards were ADDED:")
        for card in report['cards_added'][:5]:
            print(f"  - {card['guid']}: {card['front']}")
    
    if report['cards_removed']:
        print(f"\n⚠️  {len(report['cards_removed'])} cards were REMOVED:")
        for card in report['cards_removed'][:5]:
            print(f"  - {card['guid']}: {card['front']}")
    
    if report['content_changed']:
        print(f"\n⚠️  {len(report['content_changed'])} cards had CONTENT CHANGES:")
        for card in report['content_changed'][:5]:
            print(f"  - {card['guid']}: {card['field_changes']} fields changed")
    
    if report['tags_changed']:
        print(f"\n✓ {len(report['tags_changed'])} cards had tag changes:")
        
        # Group by tag patterns
        tag_patterns = defaultdict(list)
        for change in report['tags_changed']:
            pattern = f"Added: {', '.join(sorted(change['tags_added']))}"
            if change['tags_removed']:
                pattern += f" | Removed: {', '.join(sorted(change['tags_removed']))}"
            tag_patterns[pattern].append(change)
        
        for pattern, changes in sorted(tag_patterns.items(), key=lambda x: -len(x[1])):
            print(f"\n  {pattern} ({len(changes)} cards):")
            for change in changes[:3]:
                print(f"    - {change['front']}")
            if len(changes) > 3:
                print(f"    ... and {len(changes) - 3} more")
    
    # Save detailed report
    report_file = 'tag_validation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_tag_changes.py <original.json> <modified.json>")
        print("\nExample:")
        print("  python validate_tag_changes.py deck_backup.json deck.json")
        sys.exit(1)
    
    original_file = sys.argv[1]
    modified_file = sys.argv[2]
    
    try:
        report = validate_tag_only_changes(original_file, modified_file)
        print_report(report)
        
        # Exit with appropriate code
        sys.exit(0 if report['validation_passed'] else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)