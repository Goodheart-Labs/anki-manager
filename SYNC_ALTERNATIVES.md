# Anki Deck Sync Alternatives

Here are two alternative approaches to the CrowdAnki + AnkiConnect workflow for syncing deck changes and collaborative editing:

## Alternative 1: Cloud-Based Webhook Sync

### Overview
Use GitHub Actions/Webhooks + cloud storage to automatically process and sync deck changes without requiring local services.

### Architecture
```
GitHub Repo → GitHub Actions → Cloud Storage → Anki Mobile/Desktop
     ↑                                              ↓
     └──────────── Edit via Claude ←────────────────┘
```

### One-time Setup
1. **Create GitHub repository** with your deck files
2. **Set up GitHub Actions workflow** that triggers on push:
   ```yaml
   name: Sync Anki Deck
   on:
     push:
       branches: [main]
   
   jobs:
     sync:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Process deck changes
           run: python process_deck.py
         - name: Upload to cloud
           run: |
             # Upload to Dropbox/Google Drive/S3
             # Generate shareable .apkg file
   ```

3. **Install AnkiWeb Sync Enhanced** (hypothetical add-on) that:
   - Monitors a cloud folder for .apkg files
   - Auto-imports on detection
   - Maintains version history

### Edit & Review Workflow
1. **Claude edits cards** via GitHub web interface or API:
   ```python
   # Claude can directly edit via GitHub API
   gh.edit_file("decks/my_deck.json", new_content)
   gh.create_pull_request("Claude's suggested edits")
   ```

2. **Review changes** in GitHub PR interface
3. **Merge triggers sync** - GitHub Action builds .apkg and uploads
4. **Anki auto-imports** from cloud folder

### Advantages
- No local services needed
- Works with AnkiMobile/AnkiDroid
- Built-in version control and rollback
- Can preview changes before syncing

### Implementation Code
```python
# process_deck.py (runs in GitHub Actions)
import json
from anki_export import DeckExporter

def process_deck_changes():
    # Load deck from JSON/CSV
    with open('deck.json', 'r') as f:
        deck_data = json.load(f)
    
    # Convert to .apkg format
    exporter = DeckExporter()
    apkg_path = exporter.export(deck_data)
    
    # Upload to cloud storage
    upload_to_cloud(apkg_path)
    
    # Notify Anki clients via webhook
    notify_anki_clients({
        'deck_id': deck_data['id'],
        'version': deck_data['version'],
        'download_url': get_download_url(apkg_path)
    })
```

---

## Alternative 2: Direct Database Sync with SQLite

### Overview
Directly manipulate Anki's SQLite database for instant, seamless syncing without import/export steps.

### Architecture
```
Git Repo → Local Sync Service → Anki SQLite DB
    ↑              ↓                    ↓
    └─── Claude Edits ←──── Read Current State
```

### One-time Setup
1. **Install custom Anki add-on** that exposes deck state:
   ```python
   # anki_git_sync addon
   from aqt import mw
   from anki.hooks import addHook
   
   class GitSyncAddon:
       def __init__(self):
           self.watch_repo = "~/anki-decks-repo"
           self.start_file_watcher()
       
       def on_file_change(self, filepath):
           # Detect changes in git repo
           self.sync_to_anki()
   ```

2. **Initialize deck repository** with bidirectional sync:
   ```bash
   git clone https://github.com/you/anki-decks
   cd anki-decks
   python init_sync.py --collection ~/.local/share/Anki2/User1
   ```

### Edit & Review Workflow
1. **Claude connects via SSH/API** to edit deck files:
   ```python
   # Direct database queries for card analysis
   cards = anki_db.query("""
       SELECT id, flds, tags FROM notes 
       WHERE tags LIKE '%needs-review%'
   """)
   
   # Make improvements
   for card in cards:
       improved = claude_improve_card(card)
       deck_repo.update_card(card.id, improved)
   ```

2. **Real-time preview** of changes:
   ```python
   # Live preview server
   @app.route('/preview/<card_id>')
   def preview_card(card_id):
       before = current_deck.get_card(card_id)
       after = proposed_changes.get_card(card_id)
       return render_diff(before, after)
   ```

3. **Atomic commits** with instant sync:
   ```python
   def apply_changes(changes):
       with anki_db.transaction():
           for change in changes:
               if change.type == 'edit':
                   update_note(change.note_id, change.fields)
               elif change.type == 'add':
                   add_note(change.deck_id, change.fields)
       
       git_commit(f"Applied {len(changes)} changes")
   ```

### Advantages
- Instant syncing (no import/export)
- Preserves all metadata (scheduling, reviews, etc.)
- Can read current card states for better edits
- Supports complex operations (moving cards, merging decks)

### Implementation Code
```python
# anki_db_sync.py
import sqlite3
from pathlib import Path
import json

class AnkiDatabaseSync:
    def __init__(self, collection_path):
        self.db = sqlite3.connect(collection_path)
        self.init_triggers()
    
    def init_triggers(self):
        """Create triggers to log changes"""
        self.db.execute("""
            CREATE TRIGGER IF NOT EXISTS note_changes
            AFTER UPDATE ON notes
            BEGIN
                INSERT INTO sync_log (action, note_id, timestamp)
                VALUES ('update', NEW.id, strftime('%s', 'now'));
            END;
        """)
    
    def export_deck_to_json(self, deck_name):
        """Export deck to Git-friendly format"""
        cards = self.db.execute("""
            SELECT n.id, n.flds, n.tags, c.due, c.ivl
            FROM notes n
            JOIN cards c ON c.nid = n.id
            JOIN decks d ON c.did = d.id
            WHERE d.name = ?
        """, (deck_name,)).fetchall()
        
        return {
            'deck_name': deck_name,
            'cards': [self._card_to_dict(c) for c in cards]
        }
    
    def import_changes_from_json(self, json_path):
        """Apply changes from Git repository"""
        with open(json_path) as f:
            changes = json.load(f)
        
        with self.db:  # Transaction
            for change in changes['cards']:
                if change.get('action') == 'edit':
                    self._update_note(change)
                elif change.get('action') == 'add':
                    self._add_note(change)
    
    def _update_note(self, change):
        fields = '\x1f'.join(change['fields'])
        self.db.execute(
            "UPDATE notes SET flds = ?, mod = ? WHERE id = ?",
            (fields, int(time.time()), change['id'])
        )
```

---

## Comparison Table

| Feature | CrowdAnki + AnkiConnect | Cloud Webhook | Direct DB Sync |
|---------|------------------------|---------------|----------------|
| Setup Complexity | Medium | Low | High |
| Sync Speed | Fast | Medium | Instant |
| Mobile Support | Limited | Full | Desktop only |
| Preserves Scheduling | No | No | Yes |
| Rollback Support | Git-based | Git + versions | Git + DB backups |
| Claude Integration | Via files | Via API | Direct queries |
| Real-time Preview | No | Yes | Yes |

## Recommended Approach

For your use case (Claude editing + auto-sync), I recommend **Alternative 1 (Cloud Webhook)** because:
- Works with all Anki clients (mobile included)
- Easier to set up and maintain
- Natural GitHub integration for Claude edits
- Built-in review process via PRs

Would you like me to implement a proof-of-concept for either approach?