# Flask Benchmark App

Part of the [Flask vs Next.js Benchmark](https://flaskvibe.com/benchmark) by [Flask Vibe](https://flaskvibe.com).

A SaaS-style dashboard built with **Flask + raw SQL + Tailwind CDN**. Compare with the [Next.js version](https://github.com/callmefredcom/flaskvibe-benchmark-nextjs).

## Stack

- Flask 3.1 — Python web framework
- psycopg2 — raw SQL, no ORM
- Tailwind CSS CDN — no build step, no npm
- PostgreSQL — same schema as the Next.js version
- bcrypt — password hashing

## Quick Start

```bash
git clone https://github.com/callmefredcom/flaskvibe-benchmark-flask
cd flaskvibe-benchmark-flask
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```bash
createdb benchmark_flask
psql benchmark_flask < schema.sql
cp .env.example .env   # set DATABASE_URL
python seed.py         # seeds 100 projects
flask run              # → http://localhost:5000
```

**Demo login:** `demo@benchmark.dev` / `password123`

## Run the Benchmark

The `/dashboard` route is **public** (no auth required) so Lighthouse can hit it directly:

```bash
npm install -g lighthouse

lighthouse http://localhost:5000/dashboard \
  --output=json \
  --throttling-method=simulate \
  --output-path=./flask-results.json
```

## Lines of Code

```
app.py              ~120 lines
templates/          ~200 lines
schema.sql          ~15 lines
seed.py             ~25 lines
─────────────────────────────
Total               ~360 lines
```

Compare to the [Next.js version](https://github.com/callmefredcom/flaskvibe-benchmark-nextjs): ~4,200 lines.
