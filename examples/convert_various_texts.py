#!/usr/bin/env python3
"""
Examples of converting various text types to Anki cards.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anki_converter import AnkiConverter

def example_poem():
    """Convert a poem line-by-line."""
    poem = """Roses are red,
Violets are blue,
Sugar is sweet,
And so are you."""
    
    converter = AnkiConverter()
    converter.convert_text(poem, "Simple Poem", "line_by_line")

def example_qa():
    """Convert Q&A format text."""
    qa_text = """Q: What is the capital of France?
A: Paris

Q: What is the largest planet in our solar system?
A: Jupiter

Question: Who wrote Romeo and Juliet?
Answer: William Shakespeare"""
    
    converter = AnkiConverter()
    converter.convert_text(qa_text, "General Knowledge QA", "qa")

def example_cloze():
    """Convert text with cloze deletions."""
    cloze_text = """The {heart} pumps {blood} throughout the body.
The {brain} is the control center of the {nervous system}.
{Photosynthesis} is the process by which plants make {food}."""
    
    converter = AnkiConverter()
    converter.convert_text(cloze_text, "Biology Cloze", "cloze")

def example_delimiter():
    """Convert delimiter-separated cards."""
    delimited = """Hello    Bonjour
Goodbye    Au revoir
Thank you    Merci
Please    S'il vous plaît"""
    
    converter = AnkiConverter()
    converter.convert_text(delimited, "French Vocabulary", "delimiter")

if __name__ == "__main__":
    print("Running Anki conversion examples...\n")
    
    print("1. Converting a simple poem:")
    example_poem()
    
    print("\n" + "="*60 + "\n")
    
    print("2. Converting Q&A format:")
    example_qa()
    
    print("\n" + "="*60 + "\n")
    
    print("3. Converting cloze deletions:")
    example_cloze()
    
    print("\n" + "="*60 + "\n")
    
    print("4. Converting delimiter-separated vocabulary:")
    example_delimiter()