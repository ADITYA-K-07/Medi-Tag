# ADR 0001: Use a small monorepo

Status: accepted

Keep the Flutter app, Next.js app, FastAPI service, shared contracts, and local
infrastructure in one repository. This makes API changes visible to every client
and keeps setup simple for a small team. Each application remains independently
buildable and deployable.
