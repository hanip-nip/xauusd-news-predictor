# XAUUSD News Predictor — Deploy ke Vercel

Struktur:
```
index.html      ← website (satu file)
api/proxy.js    ← CORS proxy (Vercel serverless function)
vercel.json     ← konfigurasi
server.py       ← opsional, hanya untuk jalan lokal (diabaikan Vercel)
```

## Cara deploy (tanpa coding)
1. Login ke https://vercel.com (pakai akun GitHub/Google, gratis — tidak perlu kartu kredit).
2. Cara termudah: upload lewat GitHub
   - Buat repo baru di GitHub, upload semua file di folder ini (termasuk folder `api`).
   - Di Vercel: **Add New → Project → Import** repo tersebut → Framework Preset: **Other** → **Deploy**.
3. Atau via CLI: `npx vercel` di folder ini, lalu `npx vercel --prod`.

Setelah deploy, buka `https://<nama-project>.vercel.app`.
Di sidebar "Status sumber data" harus muncul **Proxy aktif (/api/proxy)**.

Catatan: data input & history tersimpan di localStorage browser masing-masing pengunjung.
