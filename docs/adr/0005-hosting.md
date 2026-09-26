# ADR 0005: Use Render and Vercel

Status: accepted

Run FastAPI and managed PostgreSQL on Render and deploy Next.js to Vercel. Local
development uses PostgreSQL and Redis through Docker Compose. All provider
settings are environment-based so hosting can change without rewriting clients.
