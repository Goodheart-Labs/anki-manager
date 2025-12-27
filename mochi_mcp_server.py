#!/usr/bin/env python3
"""
MCP Server for Mochi Cards API.

Run this on your machine to give Claude access to your Mochi cards.

Usage:
    python mochi_mcp_server.py

Then add to your Claude config:
    {
        "mcpServers": {
            "mochi": {
                "command": "python",
                "args": ["/path/to/mochi_mcp_server.py"],
                "env": {
                    "MOCHI_API_KEY": "your_api_key",
                    "MOCHI_DEFAULT_DECK_ID": "your_deck_id"
                }
            }
        }
    }
"""

import json
import sys
from mochi_api import MochiAPI, get_all_decks, get_all_cards


def send_response(response):
    """Send JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def handle_request(request):
    """Handle incoming JSON-RPC request."""
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mochi", "version": "1.0.0"}
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "mochi_list_decks",
                        "description": "List all Mochi decks",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "mochi_list_cards",
                        "description": "List cards in a deck",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "deck_id": {"type": "string", "description": "Deck ID (optional, uses default)"}
                            }
                        }
                    },
                    {
                        "name": "mochi_add_card",
                        "description": "Add a new flashcard",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "front": {"type": "string", "description": "Front side (question)"},
                                "back": {"type": "string", "description": "Back side (answer)"},
                                "deck_id": {"type": "string", "description": "Deck ID (optional)"},
                                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"}
                            },
                            "required": ["front", "back"]
                        }
                    },
                    {
                        "name": "mochi_add_deck",
                        "description": "Create a new deck",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Deck name"},
                                "parent_id": {"type": "string", "description": "Parent deck ID (optional)"}
                            },
                            "required": ["name"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            mochi = MochiAPI()
            result = None

            if tool_name == "mochi_list_decks":
                decks = get_all_decks(mochi)
                result = [{"id": d.get("id"), "name": d.get("name"), "cards": d.get("cards-count", 0), "parent": d.get("parent-id")} for d in decks]

            elif tool_name == "mochi_list_cards":
                deck_id = args.get("deck_id") or mochi.default_deck_id
                cards = get_all_cards(mochi, deck_id=deck_id)
                result = []
                for c in cards:
                    content = c.get("content", "")
                    parts = content.split("---", 1)
                    result.append({
                        "id": c.get("id"),
                        "front": parts[0].strip()[:100],
                        "back": parts[1].strip()[:100] if len(parts) > 1 else "",
                        "tags": c.get("tags", [])
                    })

            elif tool_name == "mochi_add_card":
                card = mochi.create_basic_card(
                    front=args["front"],
                    back=args["back"],
                    deck_id=args.get("deck_id"),
                    tags=args.get("tags")
                )
                result = {"id": card.get("id"), "status": "created"}

            elif tool_name == "mochi_add_deck":
                deck = mochi.create_deck(args["name"], parent_id=args.get("parent_id"))
                result = {"id": deck.get("id"), "name": deck.get("name")}

            mochi.close()

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
            }

    elif method == "notifications/initialized":
        return None  # No response needed

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Main loop - read JSON-RPC from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                send_response(response)
        except json.JSONDecodeError:
            send_response({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})


if __name__ == "__main__":
    main()
