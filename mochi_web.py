#!/usr/bin/env python3
"""
Simple web UI for adding Mochi cards.

Usage:
    pip install flask
    python mochi_web.py

Then open http://localhost:5555 in your browser.
"""

import os
from flask import Flask, request, jsonify, render_template_string

from mochi_api import MochiAPI, get_all_decks

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mochi Cards</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .card-form {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #555; }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        textarea { min-height: 100px; resize: vertical; }
        button {
            background: #6c5ce7;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover { background: #5b4cdb; }
        .bulk-section { margin-top: 30px; }
        .message {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
        .success { background: #d4edda; color: #155724; display: block; }
        .error { background: #f8d7da; color: #721c24; display: block; }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background: #ddd;
            border: none;
            font-size: 16px;
        }
        .tab.active { background: #6c5ce7; color: white; }
        .tab:first-child { border-radius: 4px 0 0 4px; }
        .tab:last-child { border-radius: 0 4px 4px 0; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .help { color: #888; font-size: 14px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>🍡 Mochi Cards</h1>

    <div id="message" class="message"></div>

    <div class="tabs">
        <button class="tab active" onclick="showTab('single')">Single Card</button>
        <button class="tab" onclick="showTab('bulk')">Bulk Add</button>
    </div>

    <div id="single" class="tab-content active">
        <div class="card-form">
            <label>Deck</label>
            <select id="deck">
                {% for deck in decks %}
                <option value="{{ deck.id }}" {% if deck.id == default_deck %}selected{% endif %}>
                    {{ deck.name }} ({{ deck.cards }} cards)
                </option>
                {% endfor %}
            </select>

            <label>Front (Question)</label>
            <input type="text" id="front" placeholder="le chat">

            <label>Back (Answer)</label>
            <input type="text" id="back" placeholder="the cat (m)">

            <label>Tags (optional, comma-separated)</label>
            <input type="text" id="tags" placeholder="nouns, animals">

            <button onclick="addCard()">Add Card</button>
        </div>
    </div>

    <div id="bulk" class="tab-content">
        <div class="card-form">
            <label>Deck</label>
            <select id="bulk-deck">
                {% for deck in decks %}
                <option value="{{ deck.id }}" {% if deck.id == default_deck %}selected{% endif %}>
                    {{ deck.name }}
                </option>
                {% endfor %}
            </select>

            <label>Cards (one per line: front | back)</label>
            <p class="help">Example:<br>le chat | the cat (m)<br>la maison | the house (f)</p>
            <textarea id="bulk-cards" rows="10" placeholder="le chat | the cat (m)
la maison | the house (f)
le chien | the dog (m)"></textarea>

            <button onclick="addBulkCards()">Add All Cards</button>
        </div>
    </div>

    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab-content#${tab}`).classList.add('active');
            event.target.classList.add('active');
        }

        function showMessage(text, isError) {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = 'message ' + (isError ? 'error' : 'success');
            setTimeout(() => { msg.className = 'message'; }, 3000);
        }

        async function addCard() {
            const front = document.getElementById('front').value;
            const back = document.getElementById('back').value;
            const deck = document.getElementById('deck').value;
            const tags = document.getElementById('tags').value;

            if (!front || !back) {
                showMessage('Please fill in both front and back', true);
                return;
            }

            const resp = await fetch('/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({front, back, deck_id: deck, tags: tags || null})
            });

            const data = await resp.json();
            if (data.success) {
                showMessage('Card added!');
                document.getElementById('front').value = '';
                document.getElementById('back').value = '';
                document.getElementById('tags').value = '';
                document.getElementById('front').focus();
            } else {
                showMessage('Error: ' + data.error, true);
            }
        }

        async function addBulkCards() {
            const text = document.getElementById('bulk-cards').value;
            const deck = document.getElementById('bulk-deck').value;

            const lines = text.trim().split('\\n').filter(l => l.trim());
            if (!lines.length) {
                showMessage('Please enter some cards', true);
                return;
            }

            let added = 0;
            let errors = [];

            for (const line of lines) {
                const parts = line.split('|').map(p => p.trim());
                if (parts.length < 2) {
                    errors.push(line);
                    continue;
                }

                const resp = await fetch('/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({front: parts[0], back: parts[1], deck_id: deck})
                });

                const data = await resp.json();
                if (data.success) added++;
                else errors.push(parts[0]);
            }

            if (errors.length) {
                showMessage(`Added ${added} cards, ${errors.length} failed`, true);
            } else {
                showMessage(`Added ${added} cards!`);
                document.getElementById('bulk-cards').value = '';
            }
        }

        document.getElementById('front').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') document.getElementById('back').focus();
        });
        document.getElementById('back').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addCard();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    mochi = MochiAPI()
    decks = get_all_decks(mochi)
    deck_list = [{"id": d.get("id"), "name": d.get("name"), "cards": d.get("cards-count", 0)} for d in decks]
    mochi.close()

    default_deck = os.environ.get("MOCHI_DEFAULT_DECK_ID", "")
    return render_template_string(HTML_TEMPLATE, decks=deck_list, default_deck=default_deck)


@app.route('/add', methods=['POST'])
def add_card():
    data = request.json
    try:
        mochi = MochiAPI()
        tags = None
        if data.get('tags'):
            tags = [t.strip() for t in data['tags'].split(',')]

        card = mochi.create_basic_card(
            front=data['front'],
            back=data['back'],
            deck_id=data.get('deck_id'),
            tags=tags
        )
        mochi.close()
        return jsonify({"success": True, "id": card.get("id")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    print("\n🍡 Mochi Cards Web UI")
    print("=" * 40)
    print("Open http://localhost:5555 in your browser")
    print("Press Ctrl+C to stop\n")
    app.run(port=5555, debug=False)
