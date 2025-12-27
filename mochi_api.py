#!/usr/bin/env python3
"""
Mochi Cards API integration for creating and managing flashcards.

API Documentation: https://mochi.cards/docs/api/
"""

import argparse
import os
import sys
import requests
from typing import Optional, List, Dict, Any
from base64 import b64encode


class MochiAPI:
    """Client for interacting with the Mochi Cards API."""

    BASE_URL = "https://app.mochi.cards/api/"

    def __init__(self, api_key: Optional[str] = None, default_deck_id: Optional[str] = None):
        """
        Initialize the Mochi API client.

        Args:
            api_key: Mochi API key. If not provided, reads from MOCHI_API_KEY env var.
            default_deck_id: Default deck ID for creating cards. If not provided,
                           reads from MOCHI_DEFAULT_DECK_ID env var.
        """
        self.api_key = api_key or os.environ.get("MOCHI_API_KEY")
        self.default_deck_id = default_deck_id or os.environ.get("MOCHI_DEFAULT_DECK_ID")

        if not self.api_key:
            raise ValueError("MOCHI_API_KEY is required. Set it as env var or pass to constructor.")

        self.session = requests.Session()
        # Mochi uses Basic auth with API key as username, empty password
        auth_string = b64encode(f"{self.api_key}:".encode()).decode()
        self.session.headers.update({
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return {}

    # Card operations
    def create_card(
        self,
        content: str,
        deck_id: Optional[str] = None,
        template_id: Optional[str] = None,
        fields: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        pos: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new card.

        Args:
            content: Card content in markdown format. Use --- to separate front/back.
            deck_id: Deck to add the card to. Uses default if not specified.
            template_id: Optional template ID for the card.
            fields: Optional dict of field IDs to values (for templates).
            tags: Optional list of tags (without # prefix).
            pos: Optional position string for ordering within deck.

        Returns:
            The created card object.
        """
        deck_id = deck_id or self.default_deck_id
        if not deck_id:
            raise ValueError("deck_id is required. Set MOCHI_DEFAULT_DECK_ID or pass deck_id.")

        data = {
            "content": content,
            "deck-id": deck_id
        }

        if template_id:
            data["template-id"] = template_id
        if fields:
            data["fields"] = fields
        if tags:
            data["tags"] = tags
        if pos:
            data["pos"] = pos

        return self._request("POST", "cards/", json=data)

    def create_basic_card(self, front: str, back: str, deck_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Create a basic front/back card.

        Args:
            front: Front side content (question).
            back: Back side content (answer).
            deck_id: Deck to add the card to.
            **kwargs: Additional arguments passed to create_card.

        Returns:
            The created card object.
        """
        # Mochi uses --- to separate front and back
        content = f"{front}\n---\n{back}"
        return self.create_card(content, deck_id=deck_id, **kwargs)

    def get_card(self, card_id: str) -> Dict[str, Any]:
        """Get a card by ID."""
        return self._request("GET", f"cards/{card_id}")

    def update_card(self, card_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a card.

        Args:
            card_id: The card ID to update.
            **kwargs: Fields to update (content, deck-id, template-id, fields, tags, pos).
        """
        # Convert underscores to hyphens for API compatibility
        data = {k.replace("_", "-"): v for k, v in kwargs.items()}
        return self._request("POST", f"cards/{card_id}", json=data)

    def delete_card(self, card_id: str) -> None:
        """Delete a card."""
        self._request("DELETE", f"cards/{card_id}")

    def list_cards(self, deck_id: Optional[str] = None, bookmark: Optional[str] = None) -> Dict[str, Any]:
        """
        List cards, optionally filtered by deck.

        Args:
            deck_id: Optional deck ID to filter by.
            bookmark: Optional pagination bookmark.

        Returns:
            Dict with 'docs' (list of cards) and 'bookmark' (for pagination).
        """
        params = {}
        if deck_id:
            params["deck-id"] = deck_id
        if bookmark:
            params["bookmark"] = bookmark
        return self._request("GET", "cards/", params=params)

    # Deck operations
    def list_decks(self, bookmark: Optional[str] = None) -> Dict[str, Any]:
        """List all decks."""
        params = {}
        if bookmark:
            params["bookmark"] = bookmark
        return self._request("GET", "decks/", params=params)

    def get_deck(self, deck_id: str) -> Dict[str, Any]:
        """Get a deck by ID."""
        return self._request("GET", f"decks/{deck_id}")

    def create_deck(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new deck."""
        data = {"name": name}
        if parent_id:
            data["parent-id"] = parent_id
        return self._request("POST", "decks/", json=data)

    def update_deck(self, deck_id: str, **kwargs) -> Dict[str, Any]:
        """Update a deck."""
        data = {k.replace("_", "-"): v for k, v in kwargs.items()}
        return self._request("POST", f"decks/{deck_id}", json=data)

    def delete_deck(self, deck_id: str) -> None:
        """Delete a deck."""
        self._request("DELETE", f"decks/{deck_id}")

    # Template operations
    def list_templates(self, bookmark: Optional[str] = None) -> Dict[str, Any]:
        """List all templates."""
        params = {}
        if bookmark:
            params["bookmark"] = bookmark
        return self._request("GET", "templates/", params=params)

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a template by ID."""
        return self._request("GET", f"templates/{template_id}")

    # Due cards
    def get_due_cards(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get cards that are due for review.

        Args:
            date: Optional date string (YYYY-MM-DD). Defaults to today.
        """
        params = {}
        if date:
            params["date"] = date
        return self._request("GET", "due/", params=params)

    def close(self):
        """Close the session."""
        self.session.close()


def create_cards_from_list(cards: List[tuple], deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to create multiple cards from a list of (front, back) tuples.

    Args:
        cards: List of (front, back) tuples.
        deck_id: Deck to add cards to.

    Returns:
        List of created card objects.
    """
    mochi = MochiAPI()
    created = []

    for front, back in cards:
        try:
            card = mochi.create_basic_card(front, back, deck_id=deck_id)
            created.append(card)
            print(f"Created card: {front[:50]}...")
        except Exception as e:
            print(f"Failed to create card '{front[:30]}...': {e}")

    mochi.close()
    return created


def get_all_cards(mochi: MochiAPI, deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all cards, handling pagination."""
    all_cards = []
    bookmark = None
    while True:
        result = mochi.list_cards(deck_id=deck_id, bookmark=bookmark)
        all_cards.extend(result.get("docs", []))
        bookmark = result.get("bookmark")
        if not bookmark:
            break
    return all_cards


def get_all_decks(mochi: MochiAPI) -> List[Dict[str, Any]]:
    """Fetch all decks, handling pagination."""
    all_decks = []
    bookmark = None
    while True:
        result = mochi.list_decks(bookmark=bookmark)
        all_decks.extend(result.get("docs", []))
        bookmark = result.get("bookmark")
        if not bookmark:
            break
    return all_decks


def cmd_decks(args):
    """List all decks."""
    mochi = MochiAPI()
    decks = get_all_decks(mochi)

    if not decks:
        print("No decks found.")
        return

    print(f"Found {len(decks)} deck(s):\n")
    for deck in decks:
        card_count = deck.get("cards-count", "?")
        print(f"  {deck.get('name')}")
        print(f"    ID: {deck.get('id')}")
        print(f"    Cards: {card_count}")
        if deck.get("parent-id"):
            print(f"    Parent: {deck.get('parent-id')}")
        print()

    mochi.close()


def cmd_cards(args):
    """List cards in a deck."""
    mochi = MochiAPI()
    deck_id = args.deck_id or mochi.default_deck_id

    if not deck_id:
        print("Error: No deck specified. Use --deck-id or set MOCHI_DEFAULT_DECK_ID")
        sys.exit(1)

    cards = get_all_cards(mochi, deck_id=deck_id)

    if not cards:
        print(f"No cards found in deck {deck_id}")
        return

    print(f"Found {len(cards)} card(s):\n")
    for i, card in enumerate(cards, 1):
        content = card.get("content", "")
        # Split on --- to get front/back
        parts = content.split("---", 1)
        front = parts[0].strip()[:60]
        if len(parts[0].strip()) > 60:
            front += "..."

        print(f"{i}. {front}")
        print(f"   ID: {card.get('id')}")
        if card.get("tags"):
            print(f"   Tags: {', '.join(card.get('tags', []))}")
        print()

    mochi.close()


def cmd_add_deck(args):
    """Create a new deck."""
    mochi = MochiAPI()
    deck = mochi.create_deck(args.name, parent_id=args.parent)
    print(f"Created deck: {deck.get('name')}")
    print(f"ID: {deck.get('id')}")
    mochi.close()


def cmd_add_card(args):
    """Create a new card."""
    mochi = MochiAPI()
    deck_id = args.deck_id or mochi.default_deck_id

    if not deck_id:
        print("Error: No deck specified. Use --deck-id or set MOCHI_DEFAULT_DECK_ID")
        sys.exit(1)

    tags = args.tags.split(",") if args.tags else None

    card = mochi.create_basic_card(
        front=args.front,
        back=args.back,
        deck_id=deck_id,
        tags=tags
    )
    print(f"Created card: {card.get('id')}")
    mochi.close()


def cmd_view(args):
    """View a specific card."""
    mochi = MochiAPI()
    card = mochi.get_card(args.card_id)

    print(f"Card ID: {card.get('id')}")
    print(f"Deck ID: {card.get('deck-id')}")
    if card.get("tags"):
        print(f"Tags: {', '.join(card.get('tags', []))}")
    print(f"\n--- Content ---\n{card.get('content', '')}\n")

    mochi.close()


def cmd_due(args):
    """Show cards due for review."""
    mochi = MochiAPI()
    result = mochi.get_due_cards(date=args.date)
    cards = result.get("cards", [])

    if not cards:
        print("No cards due for review!")
        return

    print(f"{len(cards)} card(s) due:\n")
    for card in cards:
        content = card.get("content", "")
        front = content.split("---", 1)[0].strip()[:50]
        print(f"  - {front}...")
        print(f"    ID: {card.get('id')}")

    mochi.close()


def main():
    parser = argparse.ArgumentParser(
        description="Mochi Cards CLI - Manage your flashcards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s decks                     List all decks
  %(prog)s cards                     List cards in default deck
  %(prog)s cards --deck-id ABC123    List cards in specific deck
  %(prog)s add-deck "My New Deck"    Create a new deck
  %(prog)s add-card "Q" "A"          Add a card to default deck
  %(prog)s view CARD_ID              View a specific card
  %(prog)s due                       Show cards due today

Environment variables:
  MOCHI_API_KEY          Your Mochi API key (required)
  MOCHI_DEFAULT_DECK_ID  Default deck for card operations
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # decks command
    decks_parser = subparsers.add_parser("decks", help="List all decks")
    decks_parser.set_defaults(func=cmd_decks)

    # cards command
    cards_parser = subparsers.add_parser("cards", help="List cards in a deck")
    cards_parser.add_argument("--deck-id", "-d", help="Deck ID (uses default if not set)")
    cards_parser.set_defaults(func=cmd_cards)

    # add-deck command
    add_deck_parser = subparsers.add_parser("add-deck", help="Create a new deck")
    add_deck_parser.add_argument("name", help="Name for the new deck")
    add_deck_parser.add_argument("--parent", "-p", help="Parent deck ID")
    add_deck_parser.set_defaults(func=cmd_add_deck)

    # add-card command
    add_card_parser = subparsers.add_parser("add-card", help="Create a new card")
    add_card_parser.add_argument("front", help="Front side (question)")
    add_card_parser.add_argument("back", help="Back side (answer)")
    add_card_parser.add_argument("--deck-id", "-d", help="Deck ID (uses default if not set)")
    add_card_parser.add_argument("--tags", "-t", help="Comma-separated tags")
    add_card_parser.set_defaults(func=cmd_add_card)

    # view command
    view_parser = subparsers.add_parser("view", help="View a specific card")
    view_parser.add_argument("card_id", help="Card ID to view")
    view_parser.set_defaults(func=cmd_view)

    # due command
    due_parser = subparsers.add_parser("due", help="Show cards due for review")
    due_parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    due_parser.set_defaults(func=cmd_due)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
