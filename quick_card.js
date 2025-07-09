#!/usr/bin/env node

// Quick card creation script
import { createBasicCard, createClozeCard } from './create_card.js';

// This script provides a simple interface for creating cards
// and will be used by the assistant when you ask to create cards

export async function quickCard(type, deck, ...content) {
  try {
    if (type === 'basic') {
      const [front, back] = content;
      return await createBasicCard(deck, front, back);
    } else if (type === 'cloze') {
      const [text] = content;
      return await createClozeCard(deck, text);
    } else {
      throw new Error('Invalid card type. Use "basic" or "cloze"');
    }
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Example usage when called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  // Test card creation
  console.log('Testing card creation system...\n');
  
  try {
    const result = await quickCard(
      'basic',
      'Facts and figures',
      'What is the speed of light?',
      '299,792,458 meters per second'
    );
    
    console.log('\nTest successful!');
    console.log('Card created in both Owl and Anki backup');
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}