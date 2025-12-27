# Mochi Manager

A CLI tool and Python library for managing [Mochi Cards](https://mochi.cards/) flashcards.

## Setup

```bash
pip install requests

# Set your API key (get it from Mochi settings)
export MOCHI_API_KEY="your_api_key_here"
export MOCHI_DEFAULT_DECK_ID="your_deck_id"  # optional
```

## CLI Usage

```bash
# List all decks
python mochi_api.py decks

# List cards in a deck
python mochi_api.py cards
python mochi_api.py cards --deck-id ABC123

# Create a new deck
python mochi_api.py add-deck "French Vocabulary"

# Add a card
python mochi_api.py add-card "Bonjour" "Hello"
python mochi_api.py add-card "Le chat" "The cat" --tags "animals,nouns"

# View a specific card
python mochi_api.py view CARD_ID

# Show cards due for review
python mochi_api.py due
```

## Python API

```python
from mochi_api import MochiAPI

mochi = MochiAPI()

# List decks
decks = mochi.list_decks()

# Create a card
card = mochi.create_basic_card(
    front="What is the capital of France?",
    back="Paris"
)

# Create multiple cards
from mochi_api import create_cards_from_list
cards = [
    ("le pain", "bread"),
    ("le fromage", "cheese"),
]
create_cards_from_list(cards)

# List cards in a deck
cards = mochi.list_cards(deck_id="XYZ123")

mochi.close()
```

## API Methods

| Cards | Decks | Other |
|-------|-------|-------|
| `create_card()` | `list_decks()` | `list_templates()` |
| `create_basic_card()` | `get_deck()` | `get_template()` |
| `get_card()` | `create_deck()` | `get_due_cards()` |
| `update_card()` | `update_deck()` | |
| `delete_card()` | `delete_deck()` | |
| `list_cards()` | | |
