import Anthropic from '@anthropic-ai/sdk';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY not configured' });
  }

  const { image, mimeType, text } = req.body;

  if (!image && !text) {
    return res.status(400).json({ error: 'Image or text required' });
  }

  try {
    const client = new Anthropic({ apiKey });

    const systemPrompt = `You are a vocabulary extraction assistant. Extract vocabulary pairs from the content provided.

For each vocabulary item, output a JSON array of objects with "front" and "back" fields.

Rules:
- For foreign language vocab: front = foreign word with article (le/la/les for French), back = English translation with gender (m)/(f) if applicable
- Include verb conjugations or forms if relevant
- For phrases/idioms: front = phrase, back = meaning/translation
- Keep entries concise
- Only output valid JSON array, no other text

Example output:
[
  {"front": "le chat", "back": "the cat (m)"},
  {"front": "manger", "back": "to eat"},
  {"front": "c'était", "back": "it was"}
]`;

    const userContent = [];

    if (image) {
      userContent.push({
        type: 'image',
        source: {
          type: 'base64',
          media_type: mimeType || 'image/jpeg',
          data: image,
        },
      });
      userContent.push({
        type: 'text',
        text: 'Extract all vocabulary from this image. Output as JSON array.',
      });
    } else {
      userContent.push({
        type: 'text',
        text: `Extract vocabulary from this text. Output as JSON array.\n\n${text}`,
      });
    }

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2048,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }],
    });

    const content = response.content[0]?.text || '[]';

    // Parse JSON from response (handle markdown code blocks)
    let jsonStr = content;
    const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (jsonMatch) {
      jsonStr = jsonMatch[1];
    }

    const cards = JSON.parse(jsonStr.trim());

    return res.status(200).json({ cards });
  } catch (error) {
    console.error('Extraction error:', error);
    return res.status(500).json({ error: error.message });
  }
}
