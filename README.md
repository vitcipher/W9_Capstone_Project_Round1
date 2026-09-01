# Capstone — Round 1: AI Consulting Pitch

## Scenario
- **Sector:** Real estate — PropTech / property management for private landlords
- **Company size:** Medium (existing property listing platform, expanding into a new
  product line — see `research/sector_research.md` for the reasoning)
- **One-line pitch:** Chleo's listing platform already has private landlords as users;
  add a property-management module that turns their rent/expense/EMI/Nebenkosten
  documents into a real profit-and-loss dashboard, with AI doing the tedious data entry
  and a human confirming anything the AI isn't confident about. Also further provide a AI Tax advisor Bot, a Tenants complaints management feature, and also later Automated Rental Contract Generation.

## Overview
Round 1 mandatory deliverables for Chleo's pitch: sector research, BI dashboard, light
n8n POC, LangSmith monitoring sample, cost/timeline estimate, and the presentation given
to the teaching staff, plus the recorded decision. This repo is trimmed to just those
required deliverables — the fuller working prototype (Streamlit app + Supabase backend)
that grew out of this pitch lives in a separate development repo, out of scope for the
Round 1 submission itself.

## Repo structure
```
research/
├── sector_research.md
├── opportunities_risks.md
└── use_cases.md
dashboard/
└── dashboard_documentation.md   # includes the published Tableau Public link
n8n/
├── workflow.json
└── workflow_documentation.md
langsmith/
├── README.md
└── run_monitoring_sample.py
cost_estimation/
├── cost_analysis.md
└── timeline_estimate.md
presentation/
├── Capstone Consulting Round 1.pptx   # the deck actually presented — the submission
└── README.md                          # what changed vs. the earlier working draft
feedback/
└── round1_decision.md
data/                            # data sources backing the research pack + dashboard
requirements.txt
README.md
.env.example
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in any API keys, do not commit .env
```
Only `langsmith/run_monitoring_sample.py` needs these dependencies/keys — the dashboard
and n8n workflow are viewed/imported directly, no Python required.

## How to view the deliverables
- **Research pack:** `research/sector_research.md`, `opportunities_risks.md`,
  `use_cases.md` — data sources cited inline, backing data in `data/`.
- **Dashboard:** published on Tableau Public — link in
  `dashboard/dashboard_documentation.md`. That doc also has the full build spec (data
  sources, joins, calculated fields) and a note on a chart bug that was found and fixed
  post-presentation.
- **POC:** import `n8n/workflow.json` into n8n (Workflows → Import from File), or read the
  annotated walkthrough in `n8n/workflow_documentation.md`, which includes a standalone
  `curl` command to trigger it without any other app.
- **Monitoring:** `langsmith/README.md` documents what was monitored and links to the
  LangSmith project; `run_monitoring_sample.py` is the script that produced those traces
  (`pip install -r requirements.txt`, set `OPENAI_API_KEY`/`LANGSMITH_API_KEY` in `.env`,
  then run it).
- **Cost/timeline:** `cost_estimation/cost_analysis.md` and `timeline_estimate.md`.
- **Presentation:** `presentation/Capstone Consulting Round 1.pptx` is the deck that was
  actually presented — open it in PowerPoint/Google Slides. `presentation/README.md`
  documents what changed between it and the earlier working draft (numbers, added
  claims, one bug found and fixed).
- **Decision:** `feedback/round1_decision.md` — the keep/change call recorded after the
  teaching-staff presentation, and what carries into Round 2.

## Status
- [x] Sector + company size locked
- [x] Research pack complete
- [x] Dashboard built and published (Tableau Public — link in `dashboard/dashboard_documentation.md`)
- [x] n8n POC built
- [x] LangSmith sample captured (4/4 runs verified present via the LangSmith API — project `capstone-round1-property-extraction`, EU workspace)
- [x] Cost/timeline estimated
- [x] Presentation deck built and presented (`presentation/Capstone Consulting Round 1.pptx`)
- [x] Presented to teaching staff
- [x] `round1_decision.md` written
