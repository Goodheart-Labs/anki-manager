# Anki Conversion Notes

## How to Handle Text-to-Anki Conversions

### Key Principles
1. **Always validate cards** before exporting to catch issues early
2. **Organize exports** in a dedicated folder to avoid clutter
3. **Provide multiple parsing methods** for different text formats
4. **Show samples** so users can verify the conversion looks correct
5. **Give clear import instructions** specific to the export format

### Common Text Formats to Handle

1. **Line-by-line** (poems, speeches, songs)
   - Each line becomes front, next line becomes back
   - Creates a chain for memorization

2. **Delimiter-based** (lyrics with spacing, CSV data)
   - Front and back separated by consistent delimiter (tabs, multiple spaces, etc)
   - Good for pre-formatted flashcard data

3. **Verse/Paragraph** (longer texts)
   - Blank lines separate cards
   - Each paragraph/verse becomes a complete card

4. **Cloze deletion** (fill-in-the-blank)
   - Text with {bracketed} words to hide
   - Creates multiple cards from single sentence

5. **Q&A format** (study guides, FAQs)
   - Questions and answers clearly marked
   - Handles multi-line answers

### Validation Checklist
- [ ] No empty fronts or backs
- [ ] No fields exceeding 131KB (Anki's limit)
- [ ] No null bytes or control characters
- [ ] Valid UTF-8 encoding
- [ ] Proper escaping of delimiters

### File Organization
```
anki-manager/
├── anki_converter.py      # Main conversion tool
├── text_to_anki.py        # Core parsing functions
├── anki_validator.py      # Original validator (needs html5lib)
└── anki_exports/          # All exported files go here
    ├── Mark_Antony_Speech_20250706_005656.txt
    ├── yeats_second_coming_20250706_003519.txt
    └── spice_girls_lyrics_20250705_235801.txt
```

### Usage Examples

```python
# Basic usage
converter = AnkiConverter()
converter.convert_text(text, "Title", "line_by_line")

# With custom delimiter
converter.convert_text(text, "Title", "delimiter")

# For Q&A format
converter.convert_text(qa_text, "Study Guide", "qa")
```

### Import Instructions Template
1. Open Anki
2. Click File → Import
3. Navigate to the exported file
4. Select 'Basic' as the note type
5. Ensure correct field separator (Tab/Comma)
6. Click Import

### Future Improvements
- Add support for multi-field cards (more than front/back)
- Handle media files (images, audio)
- Support for tags and deck assignment
- Batch processing of multiple texts
- Integration with Anki's API for direct import