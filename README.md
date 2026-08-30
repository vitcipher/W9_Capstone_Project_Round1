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
  screenshots in `n8n/workflow_documentation.md`.
- **Monitoring:** see `langsmith/` for the dataset/experiment link or export.
- **Decision:** see `feedback/round1_decision.md` for the keep/change call
  after the teaching-staff presentation.

## Status
- [x] Sector + company size locked
- [x] Research pack complete
- [ ] Dashboard built
- [ ] n8n POC built
- [ ] LangSmith sample captured
- [ ] Cost/timeline estimated
- [ ] Presented to teaching staff
- [ ] `round1_decision.md` written
