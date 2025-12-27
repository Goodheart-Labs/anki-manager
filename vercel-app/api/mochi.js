export default async function handler(req, res) {
    // Only allow POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { endpoint, method, body } = req.body;

    // Use env var - set in Vercel dashboard
    const apiKey = process.env.MOCHI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ error: 'MOCHI_API_KEY not configured' });
    }

    if (!endpoint) {
        return res.status(400).json({ error: 'Endpoint required' });
    }

    try {
        const authString = Buffer.from(`${apiKey}:`).toString('base64');

        const fetchOptions = {
            method: method || 'GET',
            headers: {
                'Authorization': `Basic ${authString}`,
                'Content-Type': 'application/json'
            }
        };

        if (body && (method === 'POST' || method === 'PUT')) {
            fetchOptions.body = JSON.stringify(body);
        }

        const response = await fetch(
            `https://app.mochi.cards/api/${endpoint}`,
            fetchOptions
        );

        const data = await response.json();

        if (!response.ok) {
            return res.status(response.status).json({
                error: data.message || `API error: ${response.status}`
            });
        }

        return res.status(200).json(data);
    } catch (error) {
        console.error('Mochi API error:', error);
        return res.status(500).json({ error: error.message });
    }
}
