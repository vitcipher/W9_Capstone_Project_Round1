# Capstone — Round 1: AI Consulting Pitch

## Scenario
- **Sector:** Real estate — PropTech / property management for private landlords
- **Company size:** Medium (existing property listing platform, expanding into a new
  product line — see `research/sector_research.md` for the reasoning)
- **One-line pitch:** Chleo's listing platform already has private landlords as users;
  add a property-management module that turns their rent/expense/EMI/Nebenkosten
  documents into a real profit-and-loss dashboard, with AI doing the tedious data entry
  and a human confirming anything the AI isn't confident about.

## Overview
Pitch package for Chleo: sector research, BI dashboard, light n8n POC,
LangSmith monitoring sample, cost/timeline estimate, and a presentation to
the teaching staff.

## Repo structure
```
capstone-round1/
├── data/                     # raw/sample data used for research + dashboard
├── research/
│   ├── sector_research.md
│   ├── opportunities_risks.md
│   └── use_cases.md
├── dashboard/
│   ├── dashboard.twbx           # local workbook backup (optional)
│   └── dashboard_documentation.md   # includes Tableau Cloud link
├── n8n/
│   ├── workflow.json
│   └── workflow_documentation.md
├── app/
│   ├── streamlit_app.py         # frontend: auth-gated, 3 tabs
│   ├── db.py                    # Supabase persistence + auth helpers
│   └── bank_feed.py             # Enable Banking (Mock ASPSP) integration
├── supabase/
│   └── schema.sql               # run once in the Supabase SQL Editor
├── presentation/
│   └── slides.html              # Round 1 pitch deck, open directly in a browser
├── langsmith/
├── cost_estimation/
│   ├── cost_analysis.md
│   └── timeline_estimate.md
├── feedback/
│   └── round1_decision.md
├── requirements.txt
├── README.md
└── .env.example
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in any API keys, do not commit .env
```

## How to view the deliverables
- **Dashboard:** published on Tableau Cloud — link in
  `dashboard/dashboard_documentation.md` (a `.twbx` backup may also be in
  `dashboard/`, openable in Tableau Desktop/Public if the link isn't
  reachable).
- **POC:** import `n8n/workflow.json` into n8n, or see the annotated
  screenshots in `n8n/workflow_documentation.md`. Run `streamlit run
  app/streamlit_app.py` for an interactive demo frontend — needs a Supabase
  project first (create one at supabase.com, run `supabase/schema.sql` in its
  SQL Editor, set `SUPABASE_URL`/`SUPABASE_ANON_KEY` in `.env` — see
  `app/db.py`). Sign up with any email/password (private per account, enforced
  via Postgres Row Level Security, not just app-level filtering), then use
  "Load demo portfolio" to seed 8 example properties. 3 tabs: Document
  Extraction (upload → AI draft → confirm, saved to your account), Maintenance
  Requests (plain CRUD, saved to your account — the one must-have feature from
  a competitive review that fit a 3-day budget), and Bank Feed (a stretch
  feature — real PSD2-style open banking via Enable Banking's Mock ASPSP;
  optional, session-only, needs its own setup, see `.env.example`).
- **Monitoring:** see `langsmith/` for the dataset/experiment link or export.
- **Presentation:** open `presentation/slides.html` directly in any browser — arrow
  keys or the left-edge tab rail navigate between slides. No build step, no dependency
  on this being viewed inside Claude.
- **Decision:** see `feedback/round1_decision.md` for the keep/change call
  after the teaching-staff presentation.

## Status
- [x] Sector + company size locked
- [x] Research pack complete
- [ ] Dashboard built (spec complete in `dashboard/dashboard_documentation.md`, not yet built in Tableau)
- [x] n8n POC built
- [x] LangSmith sample captured (4/4 runs verified present via the LangSmith API — project `capstone-round1-property-extraction`, EU workspace)
- [x] Cost/timeline estimated
- [x] Presentation deck built (`presentation/slides.html`)
- [ ] Presented to teaching staff
- [ ] `round1_decision.md` written
