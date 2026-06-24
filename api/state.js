const { kv } = require('@vercel/kv');

const KEY = 'album_copa2026_familia';

module.exports = async function handler(req, res) {
  if (req.method === 'GET') {
    const owned = (await kv.get(KEY)) || [];
    res.status(200).json({ owned, updatedAt: Date.now() });
    return;
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = {}; }
    }
    const owned = Array.isArray(body && body.owned) ? body.owned : [];
    await kv.set(KEY, owned);
    res.status(200).json({ ok: true, owned, updatedAt: Date.now() });
    return;
  }

  res.status(405).json({ error: 'Method not allowed' });
};
