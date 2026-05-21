# Lead Generation Agency

AI agents that identify prospective clients, enrich them with contact data and buying signals, score them against a buyer's Ideal Customer Profile (ICP), draft personalized outreach, send it, and sell the qualified leads through a marketplace — all behind a typed REST API and a Next.js dashboard.

## Architecture

Four cooperating agents in a pipeline:

```
ICP --> Discovery --> Enrichment --> Scoring --> Outreach --> Lead --> Send --> Sell
```

| Layer | What it does | Providers (env-pluggable) |
| --- | --- | --- |
| Discovery | Finds candidate companies matching an ICP | `mock`, `google_cse`, `hunter`, `composite` |
| Enrichment | Adds contact + tech stack + buying signals | LLM-driven (mock/OpenAI/Anthropic) |
| Scoring   | Fit score 0–100 with reasoning | LLM-driven |
| Outreach  | Personalized first-touch + follow-up emails | LLM-driven |
| Mailer    | Sends outreach + tracks delivery/opens/replies | `mock`, `resend` |
| Payments  | Marketplace checkout for buyers | `mock`, `stripe` |

Every external integration **falls back to a mock implementation** when its API key isn't set, so the entire stack runs end-to-end with no credentials.

## Project layout

```
Lead-Generation/
├── src/lead_gen/                 Python backend
│   ├── api.py                    FastAPI app
│   ├── pipeline.py               Orchestrator
│   ├── agents/                   Discovery / Enrichment / Scoring / Outreach
│   ├── sources/                  Pluggable discovery sources
│   ├── llm.py                    Provider-agnostic LLM client (mock|openai|anthropic)
│   ├── mailer.py                 Outreach sender (mock|resend)
│   ├── payments.py               Marketplace checkout (mock|stripe)
│   ├── marketplace.py            Pricing + order lifecycle
│   ├── models.py                 ORM + Pydantic schemas
│   ├── db.py                     SQLite + SQLAlchemy
│   ├── config.py                 Settings from .env
│   └── seed.py                   Demo prospect pool + sample ICPs
├── scripts/run_pipeline.py       CLI end-to-end demo
├── frontend/                     Next.js 14 App Router dashboard
│   ├── app/                      /, /icps, /leads, /leads/[id], /marketplace, /marketplace/success
│   ├── components/               Nav + status/score badges
│   └── lib/                      Typed API client
├── requirements.txt
├── .env.example
└── README.md
```

## Quick start

### 1. Backend

```bash
pip install -r requirements.txt
cp .env.example .env       # mock providers work with no API keys

# CLI demo
python scripts/run_pipeline.py

# HTTP API
uvicorn lead_gen.api:app --app-dir src --reload
# http://localhost:8000/docs for Swagger UI
```

### 2. Frontend (in a second terminal)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
# http://localhost:3000
```

## Example flows

### CLI

`python scripts/run_pipeline.py` runs the full pipeline against the seeded ICP and prints scored leads with one-line outreach previews.

### API

```bash
# 1. Run the pipeline for the seeded ICP
curl -X POST localhost:8000/pipeline/run \
  -H "content-type: application/json" \
  -d '{"icp_id": 1, "max_leads": 5}'

# 2. Browse high-quality leads
curl "localhost:8000/leads?icp_id=1&min_score=70"

# 3. Send the outreach (uses configured mailer)
curl -X POST localhost:8000/leads/1/send \
  -H "content-type: application/json" \
  -d '{"use_followup": false}'

# 4. Buyer purchases a lead via Stripe-style checkout
curl -X POST localhost:8000/marketplace/checkout \
  -H "content-type: application/json" \
  -d '{"buyer_id": 1, "lead_id": 1}'
# -> returns { url: "...", session_id: "...", payment_status: "paid|pending" }
```

### Webhooks

| Endpoint | Source | Effect |
| --- | --- | --- |
| `POST /webhooks/resend`  | Resend events | Updates `delivered_at`, `opened_at`, `bounced_at`, status |
| `POST /webhooks/inbound` | Any inbound email parser | Marks `replied_at`, status=`replied` |
| `POST /webhooks/stripe`  | Stripe `checkout.session.completed` | Marks Order paid, Lead sold |

## Provider configuration

All keys are optional. Anything left blank silently falls back to its mock implementation.

```ini
# LLM
LLM_PROVIDER=openai           # or "anthropic"
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Discovery
DISCOVERY_SOURCE=composite    # tries google_cse -> hunter -> mock
GOOGLE_CSE_API_KEY=...
GOOGLE_CSE_ENGINE_ID=...
HUNTER_API_KEY=...

# Outreach mailer
MAILER_PROVIDER=resend
RESEND_API_KEY=re_...
OUTREACH_FROM_EMAIL=hello@your-domain.com

# Marketplace
PAYMENTS_PROVIDER=stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Lead lifecycle

```
new -> enriched -> scored -> ready -> sent -> delivered -> opened -> replied
                                          \-> bounced
                                  -> sold (after marketplace purchase)
```

## Pricing

Marketplace prices are score-based:

| Score | Price |
| --- | --- |
| 85+ | $50 |
| 70–84 | $30 |
| 50–69 | $15 |
| <50  | $5 |

## Roadmap

- BuiltWith / Apollo / LinkedIn Sales Nav discovery sources.
- Background workers (RQ / Celery) so `/pipeline/run` doesn't block when sources are slow.
- Per-buyer auth (API keys + dashboard sessions).
- Reply summarisation + auto-followups via the LLM.
- Multi-tenant marketplace with seller payouts (Stripe Connect).
