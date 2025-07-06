# Anki Manager

A comprehensive toolkit for converting text content (poems, songs, speeches, study materials) into Anki flashcards with built-in validation and multiple parsing methods.

## Features

- **Multiple parsing methods** for different text formats
- **Built-in validation** to ensure cards are Anki-compatible
- **Organized exports** with timestamps and descriptive filenames
- **Support for various content types**: poems, songs, speeches, Q&A, cloze deletions
- **Clean tab-separated output** ready for Anki import

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd anki-manager

# Install dependencies (optional - only needed for HTML validation)
pip install -r requirements.txt
```

## Quick Start

```python
from anki_converter import AnkiConverter

# Create converter instance
converter = AnkiConverter()

# Convert a poem or speech (line-by-line)
text = """To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles"""

converter.convert_text(text, "Hamlet Soliloquy", "line_by_line")
```

## Project Structure

```
anki-manager/
├── anki_converter.py      # Main conversion tool with validation
├── text_to_anki.py        # Core parsing functions
├── anki_validator.py      # Advanced HTML validation (requires html5lib)
├── anki_exports/          # All exported files saved here
├── examples/              # Example scripts for specific use cases
└── ANKI_CONVERSION_NOTES.md  # Detailed technical documentation
```

## Parsing Methods

### 1. Line-by-Line (`line_by_line`)
Perfect for poems, speeches, and songs where you want to memorize the sequence.
- Each line becomes the front of a card
- The next line becomes the back
- Creates a chain for memorization

```python
converter.convert_text(poem_text, "My Poem", "line_by_line")
```

### 2. Delimiter-Based (`delimiter`)
For pre-formatted content where front and back are on the same line.
- Default delimiter is 4 spaces (`    `)
- Can handle CSV-style data

```python
# Format: "Question    Answer"
converter.convert_text(formatted_text, "Q&A Cards", "delimiter")
```

### 3. Verse/Paragraph (`verse`)
For longer texts where blank lines separate content blocks.
- Each paragraph becomes a complete card
- Good for memorizing passages

```python
converter.convert_text(long_text, "Book Passages", "verse")
```

### 4. Cloze Deletion (`cloze`)
For creating fill-in-the-blank cards.
- Words in {brackets} become cloze deletions
- Creates multiple cards from single sentence

```python
text = "The {capital} of {France} is {Paris}."
converter.convert_text(text, "Geography", "cloze")
```

### 5. Q&A Format (`qa`)
For structured question-answer content.
- Recognizes Q:/A: or Question:/Answer: prefixes
- Handles multi-line answers

```python
qa_text = """Q: What is Python?
A: A high-level programming language

Q: Who created Python?
A: Guido van Rossum"""
converter.convert_text(qa_text, "Python FAQ", "qa")
```

## Using the Text-to-Anki Module Directly

For more control, use the `TextToAnki` class:

```python
from text_to_anki import TextToAnki

converter = TextToAnki()

# Parse text into cards
cards = converter.parse_line_by_line(text)

# Export to file
filename = converter.export_to_anki(cards, "my_cards.txt")
```

## Validation

All cards are automatically validated for:
- Empty fields
- Field length limits (131KB max)
- Invalid characters (null bytes, control characters)
- Proper UTF-8 encoding

## Importing into Anki

1. Open Anki
2. Click **File → Import**
3. Navigate to the `anki_exports/` folder
4. Select your exported file
5. Ensure **"Basic"** is selected as the note type
6. Ensure **"Tab"** is selected as the field separator
7. Click **Import**

## Examples

See the `examples/` folder for specific use cases:
- `lyrics_to_anki.py` - Convert song lyrics
- `simple_lyrics_to_anki.py` - Simplified version without dependencies
- `yeats_to_anki.py` - Convert poetry

## Advanced Validator

The `anki_validator.py` script provides additional HTML validation features:

```bash
# Validate a file
python anki_validator.py cards.txt

# Interactive mode
python anki_validator.py
```

Note: This requires `html5lib` to be installed.

## Tips

1. **Check the preview**: Always review the sample cards shown before importing
2. **Use descriptive titles**: Help organize your exports with clear names
3. **Test with small batches**: Try a few cards first before converting large texts
4. **Keep originals**: The original text is preserved - exports are separate files

## Contributing

Feel free to add new parsing methods or improve existing ones. See `ANKI_CONVERSION_NOTES.md` for technical details.