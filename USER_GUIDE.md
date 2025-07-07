# Anki Manager User Guide

This guide covers how to use the Anki Manager repository for converting text to Anki flashcards and managing your deck with Claude Code.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Working with Claude Code](#working-with-claude-code)
- [Core Features](#core-features)
- [Workflow Examples](#workflow-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This repository provides tools to:
1. Convert various text formats (songs, poems, speeches) into Anki flashcards
2. Validate and manage Anki decks
3. Detect duplicates in your decks
4. Sync changes between GitHub and your Anki collection
5. Enable AI-assisted deck editing with Claude

## Quick Start

### Basic Text Conversion

```bash
# Convert a poem or song to Anki format
python anki_converter.py "path/to/text.txt" "My Poem" --method line_by_line

# The output will be saved to:
# anki_exports/my_poem/my_poem.txt
```

### Available Parsing Methods
- `line_by_line`: Each line becomes front, next line becomes back
- `verse`: Preserves multi-line verses as single cards
- `delimiter`: Split by custom delimiter (e.g., "---")
- `cloze`: Create cloze deletion cards
- `qa`: Parse Q&A format

## Working with Claude Code

### Important: First Steps for Claude

**⚠️ CRITICAL FOR CLAUDE**: When a deck file is first provided or placed in the repository:
1. **Immediately create a backup copy** before making any changes:
   ```bash
   cp anki_decks/Root/deck.json anki_decks/Root/deck_original.json
   ```
2. This backup is essential for validating that only tags were changed later
3. Never modify the `deck_original.json` file

### Best Practices for Claude Code Sessions

1. **Provide Clear Context**
   ```
   "I have a deck with music lyrics that has duplicates. 
   Can you help me tag them by song and section?"
   ```

2. **Use Specific File References**
   ```
   "Look at anki_decks/Root/deck.json and find cards 
   from the song 'Next Hype'"
   ```

3. **Request Validation**
   ```
   "After making changes, please validate that only 
   tags were modified using validate_tag_changes.py"
   ```

### Common Claude Code Commands

#### Analyzing Your Deck
```
"Can you analyze my deck and identify:
- Duplicate cards
- Misplaced cards (poker in music deck, etc)
- Cards missing tags"
```

#### Tagging Cards
```
"Please tag all cards from [song name] with:
- Source tag: [song_name]
- Section tags: intro, verse1, verse2, hook, etc
- Content type: lyrics, poetry, facts, poker"
```

#### Creating Conversions
```
"Convert this text to Anki cards:
[paste your text]

Use the line_by_line method where each line 
leads to the next"
```

## Core Features

### 1. Text to Anki Conversion

**Main Tool**: `anki_converter.py`

```python
# Example usage in code
from anki_converter import AnkiConverter

converter = AnkiConverter()
anki_text = converter.convert_text(
    text="Your text here",
    title="My Cards",
    parse_method="line_by_line"
)
```

### 2. Duplicate Detection

**Tool**: `detect_duplicates.py`

```bash
# Detect duplicates in your deck
python detect_duplicates.py anki_decks/Root/deck.json

# Output:
# - Console report showing duplicate groups
# - deck_duplicates.json with detailed findings
```

### 3. Tag Validation

**Tool**: `validate_tag_changes.py`

```bash
# Validate that only tags were changed
python validate_tag_changes.py deck_backup.json deck.json

# Ensures content integrity when editing
```

### 4. Deck Editing

**Tool**: `claude_deck_editor.py`

Features AI-assisted deck editing capabilities:
- Review card quality
- Suggest improvements
- Fix formatting issues
- Add missing information

## Workflow Examples

### Example 1: Converting Song Lyrics

1. Save lyrics to a text file with clear line breaks
2. Run converter:
   ```bash
   python anki_converter.py lyrics.txt "Song Name" --method line_by_line
   ```
3. Import the generated file into Anki

### Example 2: Organizing an Existing Deck

1. Export your deck from Anki using CrowdAnki
2. Place in `anki_decks/` folder
3. Ask Claude to analyze and tag:
   ```
   "Please analyze anki_decks/Root/deck.json and:
   1. Tag all Next Hype lyrics with verse sections
   2. Mark duplicates with DUPLICATE tag
   3. Tag misplaced cards with 'misplaced' tag"
   ```
4. Validate changes:
   ```bash
   python validate_tag_changes.py deck_backup.json deck.json
   ```
5. Re-import to Anki

### Example 3: Batch Processing Multiple Texts

Create a script or ask Claude to help:
```python
# Process multiple files
for file in text_files:
    converter.convert_text(
        text=read_file(file),
        title=extract_title(file),
        parse_method="verse"
    )
```

## Best Practices

### 1. Backup Your Decks
Always create backups before making changes:
```bash
cp anki_decks/Root/deck.json anki_decks/Root/deck_backup_$(date +%Y%m%d).json
```

### 2. Use Consistent Tagging
Recommended tag structure:
- **Source**: `next_hype`, `julius_caesar`, `the_second_coming`
- **Type**: `lyrics`, `poetry`, `facts`, `poker`
- **Section**: `intro`, `verse1`, `verse2`, `hook`, `bridge`
- **Status**: `DUPLICATE`, `misplaced`, `needs_review`

### 3. Validate Before Importing
Always validate changes before importing back to Anki:
```bash
python validate_tag_changes.py original.json modified.json
```

### 4. Use Git for Version Control
```bash
git add -A
git commit -m "Tagged Next Hype lyrics by section"
git push
```

## Troubleshooting

### Common Issues

1. **Unicode/Encoding Errors**
   - Ensure files are UTF-8 encoded
   - Use `errors='ignore'` parameter if needed

2. **Missing Dependencies**
   - Install required packages: `pip install -r requirements.txt`
   - For simple operations, use `simple_lyrics_to_anki.py` (no dependencies)

3. **Large Deck Performance**
   - Process in batches
   - Use specific deck paths instead of root
   - Consider splitting large decks

### Claude Code Tips

1. **Be Specific**: Instead of "fix my deck", say "find duplicates in the Music deck"

2. **Provide Examples**: Show Claude exactly how you want cards formatted

3. **Request Verification**: Ask Claude to show you samples of changes before applying broadly

4. **Use Incremental Changes**: Process one song/section at a time for large decks

## Advanced Usage

### Custom Parsing Functions

Create your own parser in `text_to_anki.py`:
```python
def parse_custom_format(self, text: str) -> List[Tuple[str, str]]:
    """Your custom parsing logic"""
    cards = []
    # Custom parsing logic here
    return cards
```

### Automated Sync with Anki

See `SYNC_ALTERNATIVES.md` for approaches to automatic syncing between GitHub and Anki.

### Extending Validation

Add custom validation rules to `anki_validator.py`:
```python
def validate_custom_rule(self, front: str, back: str) -> List[str]:
    """Your custom validation logic"""
    issues = []
    # Check your rules
    return issues
```

## Summary

This repository provides a comprehensive toolkit for managing Anki decks with text conversion, validation, and AI assistance. The key to success is:

1. Clear communication with Claude about your goals
2. Consistent tagging and organization
3. Regular validation and backups
4. Incremental changes with verification

For additional help, refer to the example scripts in the `examples/` folder or ask Claude for specific guidance on your use case.