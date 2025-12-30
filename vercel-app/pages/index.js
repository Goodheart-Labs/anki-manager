import { useState, useRef } from 'react';
import Head from 'next/head';

export default function Home() {
  const [cards, setCards] = useState([]);
  const [decks, setDecks] = useState([]);
  const [selectedDeck, setSelectedDeck] = useState('5LvMpMNe'); // French deck default
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', isError: false });
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  const showMessage = (text, isError = false) => {
    setMessage({ text, isError });
    setTimeout(() => setMessage({ text: '', isError: false }), 4000);
  };

  // Load decks on mount
  useState(() => {
    fetch('/api/mochi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: 'decks/', method: 'GET' })
    })
      .then(r => r.json())
      .then(data => {
        if (data.docs) setDecks(data.docs);
      })
      .catch(() => {});
  }, []);

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target.result);
    reader.readAsDataURL(file);

    // Extract cards
    setLoading(true);
    setCards([]);

    try {
      const base64 = await new Promise((resolve) => {
        const r = new FileReader();
        r.onload = () => resolve(r.result.split(',')[1]);
        r.readAsDataURL(file);
      });

      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: base64,
          mimeType: file.type
        })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setCards(data.cards || []);
      showMessage(`Extracted ${data.cards?.length || 0} cards`);
    } catch (err) {
      showMessage('Error: ' + err.message, true);
    } finally {
      setLoading(false);
    }
  };

  const handleTextExtract = async (text) => {
    if (!text.trim()) return;

    setLoading(true);
    setCards([]);
    setImagePreview(null);

    try {
      const response = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setCards(data.cards || []);
      showMessage(`Extracted ${data.cards?.length || 0} cards`);
    } catch (err) {
      showMessage('Error: ' + err.message, true);
    } finally {
      setLoading(false);
    }
  };

  const updateCard = (index, field, value) => {
    const newCards = [...cards];
    newCards[index][field] = value;
    setCards(newCards);
  };

  const removeCard = (index) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  const addAllCards = async () => {
    if (!cards.length) return;

    setLoading(true);
    let added = 0;

    for (const card of cards) {
      try {
        const response = await fetch('/api/mochi', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            endpoint: 'cards/',
            method: 'POST',
            body: {
              content: `${card.front}\n---\n${card.back}`,
              'deck-id': selectedDeck
            }
          })
        });
        const data = await response.json();
        if (!data.error) added++;
      } catch (err) {}
    }

    showMessage(`Added ${added} of ${cards.length} cards!`);
    if (added === cards.length) {
      setCards([]);
      setImagePreview(null);
    }
    setLoading(false);
  };

  return (
    <>
      <Head>
        <title>Mochi Cards</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="container">
        <h1>🍡 Mochi Cards</h1>

        {message.text && (
          <div className={`message ${message.isError ? 'error' : 'success'}`}>
            {message.text}
          </div>
        )}

        <div className="card">
          <h2>Extract Cards</h2>

          <div className="upload-section">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="upload-btn"
            >
              📷 Upload Image
            </button>

            <span className="or">or</span>

            <textarea
              placeholder="Paste text with vocabulary to extract..."
              onBlur={(e) => handleTextExtract(e.target.value)}
              disabled={loading}
              rows={3}
            />
          </div>

          {imagePreview && (
            <div className="preview">
              <img src={imagePreview} alt="Preview" />
            </div>
          )}

          {loading && <div className="loading">Extracting cards...</div>}
        </div>

        {cards.length > 0 && (
          <div className="card">
            <div className="cards-header">
              <h2>Review Cards ({cards.length})</h2>
              <select
                value={selectedDeck}
                onChange={(e) => setSelectedDeck(e.target.value)}
              >
                {decks.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>

            <div className="cards-list">
              {cards.map((card, i) => (
                <div key={i} className="card-item">
                  <input
                    value={card.front}
                    onChange={(e) => updateCard(i, 'front', e.target.value)}
                    placeholder="Front"
                  />
                  <input
                    value={card.back}
                    onChange={(e) => updateCard(i, 'back', e.target.value)}
                    placeholder="Back"
                  />
                  <button onClick={() => removeCard(i)} className="remove-btn">×</button>
                </div>
              ))}
            </div>

            <button onClick={addAllCards} disabled={loading} className="add-all-btn">
              Add All Cards to Mochi
            </button>
          </div>
        )}
      </div>

      <style jsx global>{`
        * { box-sizing: border-box; }
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #1a1a2e;
          color: #eee;
          margin: 0;
          min-height: 100vh;
        }
        .container {
          max-width: 700px;
          margin: 0 auto;
          padding: 20px;
        }
        h1 { margin-bottom: 24px; }
        h2 { margin: 0 0 16px 0; font-size: 18px; }
        .card {
          background: #16213e;
          padding: 20px;
          border-radius: 12px;
          margin-bottom: 20px;
        }
        .message {
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 16px;
        }
        .success { background: #1e4620; color: #8eff8e; }
        .error { background: #4a1515; color: #ff8e8e; }
        .upload-section {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .upload-btn {
          background: #6c5ce7;
          color: white;
          border: none;
          padding: 16px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
        }
        .upload-btn:hover { background: #5b4cdb; }
        .upload-btn:disabled { background: #444; cursor: not-allowed; }
        .or {
          text-align: center;
          color: #666;
          font-size: 14px;
        }
        textarea, input, select {
          width: 100%;
          padding: 12px;
          border: 1px solid #333;
          border-radius: 8px;
          font-size: 16px;
          background: #0f0f23;
          color: #fff;
        }
        textarea:focus, input:focus, select:focus {
          outline: none;
          border-color: #6c5ce7;
        }
        .preview {
          margin-top: 16px;
          border-radius: 8px;
          overflow: hidden;
        }
        .preview img {
          width: 100%;
          max-height: 300px;
          object-fit: contain;
          background: #0f0f23;
        }
        .loading {
          text-align: center;
          padding: 20px;
          color: #888;
        }
        .cards-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .cards-header select {
          width: auto;
          min-width: 150px;
        }
        .cards-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }
        .card-item {
          display: flex;
          gap: 8px;
        }
        .card-item input {
          flex: 1;
        }
        .remove-btn {
          background: #4a1515;
          color: #ff8e8e;
          border: none;
          width: 40px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 20px;
        }
        .remove-btn:hover { background: #6a2020; }
        .add-all-btn {
          width: 100%;
          background: #27ae60;
          color: white;
          border: none;
          padding: 16px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
        }
        .add-all-btn:hover { background: #219a52; }
        .add-all-btn:disabled { background: #444; cursor: not-allowed; }
      `}</style>
    </>
  );
}
