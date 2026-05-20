# Lead Generation Agency

AI agents that identify prospective clients, enrich them with contact data and buying signals, score them against a buyer's Ideal Customer Profile (ICP), draft personalized outreach, and sell qualified leads through a marketplace API.

## Architecture

Four cooperating agents in a pipeline:

```
ICP --> Discovery --> Enrichment --> Scoring --> Outreach --> Lead (sellable)
```

| Agent | Responsibility |
| --- | --- |
| `DiscoveryAgent` | Finds candidate companies matching an ICP. MVP filters a mock pool; pluggable for Apollo, LinkedIn, Crunchbase, web search. |
| `EnrichmentAgent` | Adds contact, tech stack, and buying signals. |
| `ScoringAgent`    | Scores fit (0-100) with reasoning. |
| `OutreachAgent`   | Drafts a personalized first-touch email + a follow-up. |

A separate `marketplace` module prices leads by score and records buyer purchases.

## Project layout

```
src/lead_gen/
  config.py         env-driven settings
  db.py             SQLite + SQLAlchemy
  models.py         ORM + Pydantic schemas
  llm.py            provider-agnostic LLM client (mock | openai)
  agents/           four AI agents
  pipeline.py       orchestrator
  marketplace.py    pricing + purchase
  api.py            FastAPI app
  seed.py           demo prospect pool + sample ICPs
scripts/run_pipeline.py    CLI end-to-end demo
```

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env       # LLM_PROVIDER=mock works with no API keys

# CLI demo
python scripts/run_pipeline.py

# HTTP API
uvicorn lead_gen.api:app --app-dir src --reload
# then visit http://localhost:8000/docs
```

## Example flow (HTTP)

```bash
# 1. List the seeded ICPs
curl localhost:8000/icps

# 2. Run the pipeline for ICP #1
curl -X POST localhost:8000/pipeline/run \
  -H "content-type: application/json" \
  -d '{"icp_id": 1, "max_leads": 5}'

# 3. Browse high-quality leads
curl "localhost:8000/leads?icp_id=1&min_score=70"

# 4. Buyer purchases a lead
curl -X POST localhost:8000/marketplace/purchase \
  -H "content-type: application/json" \
  -d '{"buyer_id": 1, "lead_id": 1}'
```

## LLM configuration

Set `LLM_PROVIDER`:
- `mock` (default) — deterministic stubs, no API key needed. Useful for development and tests.
- `openai` — set `OPENAI_API_KEY` and `LLM_MODEL` (e.g. `gpt-4o-mini`).

The `LLMClient` in `llm.py` uses structured JSON responses where applicable and falls back to heuristic outputs on any error, so the pipeline never hard-fails.

## Roadmap

- Real discovery sources: Apollo, Hunter, Google Custom Search, LinkedIn Sales Nav scraper.
- Enrichment via Clearbit / Apollo / website scraping.
- Outreach automation: send via Gmail/Outlook/Resend; reply detection.
- Buyer dashboard (Next.js) on top of the API.
- Stripe-backed marketplace billing.
- Background workers for long pipelines (Celery / RQ).
