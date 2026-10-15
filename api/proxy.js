// Vercel Serverless Function: CORS proxy untuk XAUUSD News Predictor
// Endpoint: /api/proxy?url=<url-terenkode>
// Hanya domain di whitelist yang boleh diproxy (bukan open proxy).
// Respons di-cache di edge Vercel (s-maxage) supaya tidak kena rate-limit sumber (mis. ForexFactory 429).

const ALLOWED = {
  'nfs.faireconomy.media': 900,      // kalender ForexFactory: cache 15 menit
  'query1.finance.yahoo.com': 60,
  'query2.finance.yahoo.com': 60,
  'api.gold-api.com': 20,
  'api.bls.gov': 300,
  'home.treasury.gov': 1800,
};

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const target = req.query && req.query.url;
  let host;
  try { host = new URL(target).hostname; } catch { return res.status(400).json({ error: 'url tidak valid' }); }
  if (!(host in ALLOWED)) return res.status(403).json({ error: 'Domain tidak diizinkan' });

  try {
    const r = await fetch(target, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',
        'Accept': 'application/json,text/csv,*/*',
      },
    });
    const body = Buffer.from(await r.arrayBuffer());
    if (!r.ok) return res.status(502).json({ error: 'Sumber membalas HTTP ' + r.status });
    const ttl = ALLOWED[host];
    res.setHeader('Content-Type', r.headers.get('content-type') || 'application/octet-stream');
    // cache di CDN Vercel; jika sumber error, sajikan versi lama hingga 1 hari
    res.setHeader('Cache-Control', `public, s-maxage=${ttl}, stale-while-revalidate=86400`);
    return res.status(200).send(body);
  } catch (e) {
    return res.status(502).json({ error: 'Gagal fetch: ' + e.message });
  }
};
