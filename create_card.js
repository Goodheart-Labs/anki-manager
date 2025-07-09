#!/usr/bin/env node

import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
config({ path: join(__dirname, '.env') });

const API_KEY = process.env.OWL_API_KEY;
const API_URL = process.env.OWL_API_URL;

// Local Anki backup file
const ANKI_BACKUP_FILE = join(__dirname, 'owl_created_cards', 'new_cards.json');

// Ensure backup directory exists
async function ensureBackupDir() {
  const backupDir = join(__dirname, 'owl_created_cards');
  if (!existsSync(backupDir)) {
    await mkdir(backupDir, { recursive: true });
  }
}

// Load existing backup
async function loadBackup() {
  try {
    if (existsSync(ANKI_BACKUP_FILE)) {
      const data = await readFile(ANKI_BACKUP_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error loading backup:', error.message);
  }
  
  return {
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    cards: []
  };
}

// Save backup
async function saveBackup(data) {
  data.updated_at = new Date().toISOString();
  await writeFile(ANKI_BACKUP_FILE, JSON.stringify(data, null, 2));
}

// Create card in Owl
async function createOwlCard(deckId, card) {
  const response = await fetch(`${API_URL}/decks/${deckId}/cards`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': API_KEY
    },
    body: JSON.stringify(card)
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create card in Owl: ${response.status} - ${error}`);
  }
  
  return await response.json();
}

// Get deck by name
async function getDeckByName(deckName) {
  const response = await fetch(`${API_URL}/decks`, {
    method: 'GET',
    headers: { 'X-Api-Key': API_KEY }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get decks: ${response.status}`);
  }
  
  const data = await response.json();
  const decks = data.items || [];
  
  return decks.find(d => d.title === deckName);
}

// Main function to create a card
export async function createCard(deckName, cardData) {
  await ensureBackupDir();
  
  try {
    // Find the deck in Owl
    const deck = await getDeckByName(deckName);
    if (!deck) {
      throw new Error(`Deck "${deckName}" not found in Owl Cards`);
    }
    
    // Create card in Owl
    console.log(`Creating card in Owl deck "${deckName}"...`);
    const owlCard = await createOwlCard(deck.id, cardData);
    console.log(`✓ Created card in Owl (ID: ${owlCard.id})`);
    
    // Create Anki backup
    const backup = await loadBackup();
    const ankiCard = {
      guid: `anki_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      created_at: new Date().toISOString(),
      deck: deckName,
      owl_id: owlCard.id,
      type: cardData.type,
      fields: cardData.type === 'BasicCard' 
        ? { front: cardData.front, back: cardData.back }
        : { text: cardData.text },
      tags: []
    };
    
    backup.cards.push(ankiCard);
    await saveBackup(backup);
    console.log(`✓ Saved backup to owl_created_cards (${backup.cards.length} total cards)`);
    
    return { owlCard, ankiCard };
    
  } catch (error) {
    console.error('Error creating card:', error.message);
    throw error;
  }
}

// Helper function for creating basic cards
export async function createBasicCard(deckName, front, back) {
  return createCard(deckName, {
    type: 'BasicCard',
    front,
    back
  });
}

// Helper function for creating cloze cards
export async function createClozeCard(deckName, text) {
  return createCard(deckName, {
    type: 'ClozeCard',
    text
  });
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args.length < 3) {
    console.log('Usage:');
    console.log('  Basic card: node create_card.js <deck> <front> <back>');
    console.log('  Cloze card: node create_card.js --cloze <deck> <text>');
    console.log('\nExample:');
    console.log('  node create_card.js "Facts and figures" "What is 2+2?" "4"');
    console.log('  node create_card.js --cloze "Language" "The capital of France is {{Paris}}"');
    process.exit(1);
  }
  
  try {
    if (args[0] === '--cloze') {
      await createClozeCard(args[1], args[2]);
    } else {
      await createBasicCard(args[0], args[1], args[2]);
    }
  } catch (error) {
    console.error('Failed:', error.message);
    process.exit(1);
  }
}