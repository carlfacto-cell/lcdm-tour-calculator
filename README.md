# LCDM Tour Eligibility & Casting Priority Calculator

**Los Cantantes de Manila — Organizational Decision-Support System v1.0**

Interactive web application that precisely implements the logic, scoring architecture, eligibility gates, and reporting structure of the LCDM Tour Eligibility Casting Priority Calculator workbook.

## Features

- **Tour Setup** — Configure tour identity, dates, lock-in periods, score thresholds, voice-part requirements, and financial compliance rules.
- **Member Database** — Maintain master member records with voice parts, membership status, passport/visa, and notes.
- **Tour Assessment** — Enter YES/NO mandatory gates and 1–5 ratings per category. Eligibility, weighted scores, priority class, and auto-status calculate live.
- **Casting Roster** — Ranked list of eligible members by total priority score with selection status.
- **Voice Balance** — Real-time section capacity planning (Soprano/Alto/Tenor/Bass + Male/Female).
- **Dashboard** — Executive KPIs: eligibility rate, priority distribution, artistic averages, roster fill, compliance rates, traffic-light summary.
- **Rubric** — Full objective 1–5 descriptors for every scoring category.
- **Exception Log** — Documented overrides of mandatory gates with approval trail.
- **Casting Report** — Print-ready decision report with final cast, reserves, voice distribution, and signature blocks.

## Scoring Architecture (100 points)

| Category | Weight |
|----------|--------|
| A. Musical & Technical Readiness | 30 pts |
| B. Attendance & Commitment | 20 pts |
| C. Conduct, Attitude & Professionalism | 15 pts |
| D. Ensemble Suitability & Artistic Contribution | 15 pts |
| E. Sustained LCDM Participation | 10 pts |
| F. Tour Readiness & Administrative Reliability | 10 pts |

## Decision Hierarchy

1. Mandatory Eligibility Gates (any NO → INELIGIBLE)
2. Weighted 100-point Casting Priority Assessment
3. Musical minimum (default 19/30) required for final consideration
4. Overall Priority Score → Priority Band (A/B/C/Conditional/Below)
5. Artistic / roster need → Final Casting Decision

## How to Run

```bash
cd /home/workdir/artifacts/lcdm_app
streamlit run app.py --server.port 8501
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## Pre-loaded Data

The app ships with the full member roster and sample assessments from the source workbook so you can explore every page immediately. Edit any values; calculations update in real time within the session.

## Governance Notes

- Financial capacity / additional contributions never generate priority points.
- Seniority, popularity, or personal relationships do not increase scores.
- Gate 8 (Financial Compliance) is non-negotiable.
- Final artistic decisions remain with the authorized Artistic/Management body.
