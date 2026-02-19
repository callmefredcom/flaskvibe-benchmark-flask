import os, random, psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

ADJECTIVES = ['Alpha', 'Beta', 'Core', 'Delta', 'Edge', 'Fast', 'Global', 'Hub', 'Insight', 'Joint']
NOUNS = ['Platform', 'Dashboard', 'Pipeline', 'System', 'Module', 'Integration', 'Service', 'API', 'Engine', 'Portal']
STATUSES = ['active', 'active', 'active', 'completed', 'paused']

conn = psycopg2.connect(os.environ.get('DATABASE_URL', 'postgresql://localhost/benchmark_flask'))
cur = conn.cursor()

cur.execute("TRUNCATE projects, users RESTART IDENTITY CASCADE")

pw = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode()
cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id", ('demo@benchmark.dev', pw))
uid = cur.fetchone()[0]

for i in range(100):
    title = f"{ADJECTIVES[i % 10]} {NOUNS[i % 10]} {i + 1}"
    desc = f"Project number {i + 1} for the Flask vs Next.js benchmark."
    status = STATUSES[i % 5]
    budget = round(random.uniform(1000, 51000), 2)
    cur.execute(
        "INSERT INTO projects (user_id, title, description, status, budget) VALUES (%s, %s, %s, %s, %s)",
        (uid, title, desc, status, budget)
    )

conn.commit()
cur.close()
conn.close()
print("✓ Seeded 100 projects — login: demo@benchmark.dev / password123")
