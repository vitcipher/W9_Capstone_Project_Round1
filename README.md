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
│   ├── Capstone Consulting Round 1.pptx   # SUBMITTED deck — what was actually presented
│   ├── README.md                # what changed between the draft below and the presented deck
│   └── slides.html              # design draft/generator, not the submitted version
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
- **Dashboard:** published on Tableau Public — link in
  `dashboard/dashboard_documentation.md` (a `.twbx` backup may also be in
  `dashboard/`, openable in Tableau Desktop/Public if the link isn't
  reachable). Note: that doc also flags a known data bug in the published
  chart worth fixing before further grading.
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
- **Presentation:** `presentation/Capstone Consulting Round 1.pptx` is the deck that was
  actually presented and submitted — open it in PowerPoint/Google Slides. `slides.html`
  (open directly in any browser, arrow keys or the left-edge tab rail to navigate) is the
  earlier design draft it was adapted from; see `presentation/README.md` for exactly what
  changed between the two.
- **Decision:** see `feedback/round1_decision.md` for the keep/change call
  after the teaching-staff presentation.

## Status
- [x] Sector + company size locked
- [x] Research pack complete
- [x] Dashboard built and published (Tableau Public — link in `dashboard/dashboard_documentation.md`; one known data bug flagged there)
- [x] n8n POC built
- [x] LangSmith sample captured (4/4 runs verified present via the LangSmith API — project `capstone-round1-property-extraction`, EU workspace)
- [x] Cost/timeline estimated
- [x] Presentation deck built and presented (`presentation/Capstone Consulting Round 1.pptx`)
- [x] Presented to teaching staff
- [x] `round1_decision.md` written
