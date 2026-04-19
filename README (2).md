# 🌍 EcoScan — Climate + Data = Action Tool

> **Tech Builders Hackathon 2026 submission**  
> Domain: Climate Technology & Sustainability × AI/ML

---

## Problem Statement

Every day, individuals and small businesses make decisions that impact the climate — but they lack **real-time, actionable feedback** on the carbon cost of those decisions. Generic sustainability advice doesn't drive behavior change. **Personalized, data-driven nudges do.**

## Solution

EcoScan is a two-in-one Streamlit application powered by **Mistral-7B-Instruct** (open-source LLM via Hugging Face) that:

1. **🛒 Purchase Carbon Scanner** — Paste your grocery/shopping list → AI estimates the CO₂e of each item → suggests specific lower-carbon alternatives with percentage savings
2. **🏢 Business Energy Advisor** — Input your business type, energy bill, heating & lighting → AI generates a personalised 5-step energy reduction plan with monthly £ savings and payback periods

## Architecture

```
User Input (Streamlit UI)
        │
        ▼
Prompt Engineering (structured JSON prompts)
        │
        ▼
Hugging Face Inference API
(mistralai/Mistral-7B-Instruct-v0.2)
        │
        ▼
JSON Response Parsing
        │
        ▼
Interactive Results Dashboard (Streamlit)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Mistral-7B-Instruct-v0.2 (Hugging Face) |
| API | Hugging Face Inference API (free tier) |
| Language | Python 3.10+ |

## How to Run

```bash
# 1. Clone this repo
git clone <your-repo-url>
cd climate-action-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

You'll need a **free Hugging Face API token** from: https://huggingface.co/settings/tokens

## Judging Criteria Alignment

| Criterion | How EcoScan delivers |
|---|---|
| **Innovation (25%)** | Open-source LLM + structured JSON prompting for actionable climate intelligence — not a dashboard, a decision engine |
| **Functionality (25%)** | Two fully working modes, live AI inference, real parsed outputs with metrics |
| **Presentation (25%)** | Clean branded UI, clear narrative, demo-ready |
| **Problem Solving (25%)** | Addresses both individual consumer emissions AND small business energy waste — two of the highest-impact levers |

## Real-World Impact

- **Target users**: 33M UK adults who want to reduce footprint but lack guidance; 5.5M UK small businesses wasting ~£1.6bn on avoidable energy
- **Scalability**: Swap HF Inference API for a self-hosted model for zero marginal cost at scale
- **Extensions**: Receipt OCR scanning, energy meter API integration, community leaderboards

## Team

Built for the Tech Builders Program 2026 Hackathon.
