import streamlit as st
import json
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoScan – Climate Action Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.main { background: #f7f5f0; }
.block-container { padding: 2rem 3rem; max-width: 1100px; }

.hero-banner {
    background: linear-gradient(135deg, #1a3a2a 0%, #2d5a3d 60%, #4a8c5c 100%);
    border-radius: 20px;
    padding: 3rem;
    margin-bottom: 2rem;
    color: white;
}
.hero-banner h1 { color: #c8e6c9; font-size: 2.8rem; margin: 0; }
.hero-banner p { color: #a5d6a7; font-size: 1.1rem; margin: 0.5rem 0 0; }

.score-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    border-left: 5px solid #4a8c5c;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.score-card.high { border-left-color: #e53935; }
.score-card.medium { border-left-color: #fb8c00; }
.score-card.low { border-left-color: #43a047; }

.alt-card {
    background: #e8f5e9;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    border: 1px solid #c8e6c9;
}
.co2-badge {
    display: inline-block;
    background: #1b5e20;
    color: white;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    font-weight: 600;
}
.saving-badge {
    display: inline-block;
    background: #4caf50;
    color: white;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    font-weight: 600;
}
.stTextArea textarea { border-radius: 12px; border: 2px solid #c8e6c9; font-size: 0.95rem; }
.stButton > button {
    background: #2d5a3d;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover { background: #1a3a2a; transform: translateY(-1px); }
.tip-box {
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── HF Inference helper ───────────────────────────────────────────────────────
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

def call_hf(prompt: str, hf_token: str) -> str:
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 700, "temperature": 0.4, "return_full_text": False},
    }
    resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        return f"[API Error {resp.status_code}]: {resp.text[:300]}"
    data = resp.json()
    if isinstance(data, list) and data:
        return data[0].get("generated_text", "").strip()
    return str(data)

# ── Prompts ───────────────────────────────────────────────────────────────────
PURCHASE_PROMPT = """<s>[INST]
You are an expert climate and sustainability analyst. A user listed their recent purchases.
Analyze each item, estimate its carbon footprint (kg CO2e), and suggest a lower-carbon alternative.

Purchases:
{purchases}

Respond ONLY with a valid JSON array. Each element:
{{
  "item": "<purchase name>",
  "co2_kg": <number>,
  "impact_level": "high|medium|low",
  "reason": "<1 sentence why>",
  "alternative": "<specific product/brand or habit>",
  "alt_co2_kg": <number>,
  "saving_pct": <integer 0-100>
}}
No markdown, no explanation, only the JSON array.
[/INST]"""

ENERGY_PROMPT = """<s>[INST]
You are an energy efficiency consultant for small businesses.
A business provided details about their energy usage.

Business info:
{biz_info}

Give 5 specific, actionable recommendations to reduce energy costs and carbon footprint.
Respond ONLY as a valid JSON array. Each element:
{{
  "title": "<short action title>",
  "description": "<2-3 sentence explanation>",
  "estimated_saving_pct": <integer>,
  "payback_months": <integer or null>,
  "difficulty": "easy|medium|hard",
  "co2_impact": "high|medium|low"
}}
No markdown, no explanation, only the JSON array.
[/INST]"""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>🌍 EcoScan</h1>
  <p>Climate + Data = Action &nbsp;·&nbsp; Turn your purchases & energy use into a greener future</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: HF Token ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Hugging Face Token")
    hf_token = st.text_input("Paste your HF token", type="password",
                              help="Get a free token at huggingface.co/settings/tokens")
    st.markdown("---")
    st.markdown("**About EcoScan**\n\nAI-powered tool to help you understand and reduce your carbon footprint using open-source LLMs from Hugging Face.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🛒  Purchase Carbon Scanner", "🏢  Business Energy Advisor"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Purchase Scanner
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### What did you buy recently?")
        st.markdown("List your purchases — one per line. Be specific (brand, quantity, type).")
        purchases_input = st.text_area(
            "Your purchases",
            placeholder="500g beef mince\n1 litre whole milk\nFlight London to New York\nNew iPhone 15\nNike running shoes\n5 litres of petrol",
            height=220,
            label_visibility="collapsed",
        )
        scan_btn = st.button("🔍 Scan My Carbon Footprint", key="scan")

    with col2:
        st.markdown("### 💡 How it works")
        st.markdown("""
        1. **List** your recent purchases (food, travel, products)
        2. **AI analyses** each item's lifecycle carbon footprint
        3. **Get** specific lower-carbon alternatives with real savings
        4. **Act** on the biggest wins first
        """)
        st.markdown("""
        <div class="tip-box">
        🌱 <strong>Did you know?</strong> The average person's consumption emits ~10 tonnes of CO₂ per year. 
        Small swaps — like replacing beef with lentils twice a week — can cut that by 5-10%.
        </div>
        """, unsafe_allow_html=True)

    if scan_btn:
        if not hf_token:
            st.error("Please enter your Hugging Face token in the sidebar.")
        elif not purchases_input.strip():
            st.warning("Please enter at least one purchase.")
        else:
            with st.spinner("Analysing your carbon footprint with Mistral-7B..."):
                prompt = PURCHASE_PROMPT.format(purchases=purchases_input.strip())
                raw = call_hf(prompt, hf_token)

            try:
                # Extract JSON from response
                start = raw.find("[")
                end = raw.rfind("]") + 1
                results = json.loads(raw[start:end])

                total_co2 = sum(r.get("co2_kg", 0) for r in results)
                total_alt = sum(r.get("alt_co2_kg", 0) for r in results)
                saved = total_co2 - total_alt

                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("Total CO₂e", f"{total_co2:.1f} kg")
                m2.metric("If you switch", f"{total_alt:.1f} kg")
                m3.metric("Potential saving", f"{saved:.1f} kg", delta=f"-{saved/total_co2*100:.0f}%" if total_co2 else "")

                st.markdown("### Your Purchase Analysis")
                for r in results:
                    level = r.get("impact_level", "medium")
                    st.markdown(f"""
                    <div class="score-card {level}">
                      <strong>{r['item']}</strong>
                      &nbsp;<span class="co2-badge">{r['co2_kg']} kg CO₂e</span>
                      &nbsp;<em style="color:#666;font-size:0.85rem">{r.get('reason','')}</em>
                      <div class="alt-card" style="margin-top:0.75rem;margin-bottom:0">
                        ✅ <strong>Switch to:</strong> {r['alternative']}
                        &nbsp;<span class="saving-badge">Save {r.get('saving_pct',0)}%</span>
                        &nbsp;<span style="font-size:0.8rem;color:#555">→ {r['alt_co2_kg']} kg CO₂e</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Could not parse AI response. Raw output:\n\n{raw}")
                st.exception(e)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Business Energy Advisor
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### Tell us about your business")
        biz_type = st.selectbox("Business type", [
            "Restaurant / Café", "Retail shop", "Office (10-50 staff)",
            "Small manufacturing", "Gym / Leisure", "Hotel / B&B", "Other"
        ])
        monthly_bill = st.slider("Monthly energy bill (£)", 200, 5000, 800, step=50)
        heating = st.selectbox("Primary heating", ["Gas boiler", "Electric heating", "Heat pump", "Oil boiler", "District heating"])
        lighting = st.selectbox("Lighting type", ["Mix of old and LED", "Mostly fluorescent", "All LED", "Halogen/incandescent"])
        extra_info = st.text_area("Any extra context (equipment, hours, issues)?",
                                   placeholder="We run a 20-seat café, open 7am-6pm daily. Old commercial fridges, no insulation.",
                                   height=100)
        energy_btn = st.button("⚡ Get Energy Reduction Plan", key="energy")

    with col2:
        st.markdown("### 📊 Typical savings by sector")
        sectors = {"Restaurant": 28, "Retail": 22, "Office": 31, "Manufacturing": 19, "Gym": 25}
        for s, pct in sectors.items():
            st.markdown(f"**{s}** &nbsp; `{pct}% avg reduction possible`")
            st.progress(pct / 100)

        st.markdown("""
        <div class="tip-box" style="margin-top:1rem">
        💰 <strong>UK small businesses</strong> waste an estimated £1.6bn annually on avoidable energy costs.
        AI-guided efficiency plans typically deliver 20–35% savings within 12 months.
        </div>
        """, unsafe_allow_html=True)

    if energy_btn:
        if not hf_token:
            st.error("Please enter your Hugging Face token in the sidebar.")
        else:
            biz_info = (
                f"Type: {biz_type}\n"
                f"Monthly energy bill: £{monthly_bill}\n"
                f"Heating: {heating}\n"
                f"Lighting: {lighting}\n"
                f"Extra context: {extra_info or 'None provided'}"
            )
            with st.spinner("Building your personalised energy plan with Mistral-7B..."):
                prompt = ENERGY_PROMPT.format(biz_info=biz_info)
                raw = call_hf(prompt, hf_token)

            try:
                start = raw.find("[")
                end = raw.rfind("]") + 1
                tips = json.loads(raw[start:end])

                st.markdown("---")
                st.markdown(f"### ⚡ Your Energy Action Plan — {biz_type}")

                diff_colors = {"easy": "#43a047", "medium": "#fb8c00", "hard": "#e53935"}
                impact_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

                for i, tip in enumerate(tips, 1):
                    diff = tip.get("difficulty", "medium")
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"""
                        <div class="score-card">
                          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                            <span style="font-size:1.4rem;font-weight:700;color:#2d5a3d">{i}</span>
                            <strong style="font-size:1rem">{tip['title']}</strong>
                            <span style="background:{diff_colors[diff]};color:white;border-radius:10px;padding:1px 8px;font-size:0.75rem">{diff}</span>
                            <span>{impact_icons.get(tip.get('co2_impact','medium'), '🟡')} CO₂ impact</span>
                          </div>
                          <p style="margin:0;color:#444;font-size:0.9rem">{tip['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        save_pct = tip.get("estimated_saving_pct", 0)
                        payback = tip.get("payback_months")
                        monthly_save = int(monthly_bill * save_pct / 100)
                        st.metric("Monthly save", f"£{monthly_save}", f"-{save_pct}%")
                        if payback:
                            st.caption(f"Payback: {payback} months")

            except Exception as e:
                st.error(f"Could not parse AI response. Raw output:\n\n{raw}")
                st.exception(e)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem'>"
    "🌍 EcoScan · Built for Tech Builders Hackathon 2026 · Powered by Mistral-7B on Hugging Face"
    "</div>",
    unsafe_allow_html=True
)
