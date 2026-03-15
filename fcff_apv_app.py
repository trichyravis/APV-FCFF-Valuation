
"""
FCFF & APV Dynamic Valuation Model
The Mountain Path — World of Finance
NMIMS Bangalore · Corporate Finance · Capital Structure and Valuation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FCFF & APV Valuation | Mountain Path",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────────
GD = "#FFD700"; DB = "#003366"; MB = "#004d80"; LB = "#ADD8E6"
BG = "#0a1628"; CB = "#112240"; TP = "#e6f1ff"; TS = "#8892b0"
GR = "#28a745"; RD = "#dc3545"; TD = "#1a1a2e"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+Pro:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {{background:linear-gradient(135deg,#1a2332 0%,#243447 50%,#2a3f5f 100%);}}
.main,.main *,.main p,.main span,.main div,.main li,.main label{{color:{TP}!important;}}
.main h1,.main h2,.main h3,.main h4,.main h5,.main h6{{color:{GD}!important;font-family:'Playfair Display',serif;}}

section[data-testid="stSidebar"]{{background:linear-gradient(180deg,{BG} 0%,{DB} 100%);border-right:1px solid rgba(255,215,0,0.25);}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] div[class*="markdown"]{{color:{TP}!important;-webkit-text-fill-color:{TP}!important;}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{{color:{LB}!important;-webkit-text-fill-color:{LB}!important;font-weight:600!important;opacity:1!important;}}
section[data-testid="stSidebar"] input{{color:{TD}!important;background-color:#fff!important;}}

.metric-card{{background:{CB};border:1px solid rgba(255,215,0,0.3);border-radius:10px;padding:1.2rem;text-align:center;margin-bottom:0.8rem;}}
.metric-card .lbl{{color:{TS};font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;}}
.metric-card .val{{color:{GD};font-size:1.6rem;font-weight:700;font-family:'Playfair Display',serif;margin-top:0.3rem;}}
.metric-card .sub{{color:{TS};font-size:0.76rem;margin-top:0.3rem;}}
.section-title{{font-family:'Playfair Display',serif;color:{GD};font-size:1.25rem;border-bottom:2px solid rgba(255,215,0,0.3);padding-bottom:0.4rem;margin:1.2rem 0 0.8rem;}}
.info-box{{background:rgba(0,51,102,0.5);border:1px solid {GD};border-radius:8px;padding:0.9rem 1.4rem;color:{TP};margin:0.7rem 0;}}
.formula-box{{font-family:'JetBrains Mono',monospace;background:rgba(0,0,0,0.35);padding:10px 14px;border-radius:6px;border-left:3px solid {GD};font-size:0.83rem;color:{TP};margin:8px 0;}}
.stTabs [data-baseweb="tab-list"]{{gap:6px;}}
.stTabs [data-baseweb="tab"]{{background:{CB};border:1px solid rgba(255,215,0,0.3);border-radius:8px;color:{TP};padding:0.45rem 0.9rem;}}
.stTabs [aria-selected="true"]{{background:{DB};border:2px solid {GD};color:{GD};}}
.stButton>button{{background:linear-gradient(135deg,{MB},{DB})!important;color:{GD}!important;border:2px solid {GD}!important;border-radius:8px!important;font-weight:600!important;}}
.stButton>button:hover{{background:linear-gradient(135deg,{GD},#d4af37)!important;color:{DB}!important;}}
.stAlert{{background-color:rgba(255,255,255,0.95)!important;}}
.stAlert p,.stAlert span,.stAlert div{{color:{TD}!important;}}
details summary{{color:{GD}!important;}}
footer{{visibility:hidden;}}

/* input number text */
input[type="number"]{{color:{TD}!important;}}
div[data-testid="stNumberInput"] input{{color:{TD}!important;background:#fff!important;}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def sec(t):
    st.markdown(f'<div class="section-title">{t}</div>', unsafe_allow_html=True)

def mcard(label, value, sub=None, color=None):
    clr = color or GD
    sh = f'<div class="sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card">
      <div class="lbl">{label}</div>
      <div class="val" style="color:{clr};-webkit-text-fill-color:{clr};">{value}</div>{sh}
    </div>""", unsafe_allow_html=True)

def ibox(content, title=None):
    th = f"<h4 style='color:{GD};margin-top:0;font-family:Playfair Display,serif;'>{title}</h4>" if title else ""
    st.markdown(f'<div class="info-box">{th}{content}</div>', unsafe_allow_html=True)

def fbox(text):
    st.markdown(f'<div class="formula-box">{text}</div>', unsafe_allow_html=True)

def playout(**kw):
    base = dict(paper_bgcolor=CB, plot_bgcolor=CB,
                font=dict(color=TP, family="Source Sans Pro"),
                margin=dict(l=50, r=30, t=45, b=45))
    base.update(kw)
    return base

def header():
    st.html(f"""
    <div style="background:linear-gradient(135deg,{DB},{MB});border:2px solid {GD};
                border-radius:12px;padding:1.4rem 2rem;margin-bottom:1.2rem;text-align:center;
                user-select:none;">
      <p style="font-family:'Playfair Display',serif;color:{GD};
                -webkit-text-fill-color:{GD};margin:0;font-size:1rem;font-weight:700;">
        🏔️ The Mountain Path — World of Finance
      </p>
      <h1 style="font-family:'Playfair Display',serif;color:{GD};
                 -webkit-text-fill-color:{GD};margin:0.3rem 0;font-size:1.9rem;">
        📊 FCFF &amp; APV Dynamic Valuation Model
      </h1>
      <p style="color:{LB};-webkit-text-fill-color:{LB};margin:0.4rem 0 0;
                font-size:0.95rem;font-weight:600;">
        Free Cash Flow to Firm  ·  WACC Method  ·  Adjusted Present Value
      </p>
      <p style="color:{TS};-webkit-text-fill-color:{TS};margin:0.25rem 0 0;font-size:0.82rem;">
        Prof. V. Ravichandran  ·  28+ Years Corporate Finance &amp; Banking  ·  10+ Years Academic Excellence
      </p>
      <p style="color:{TS};-webkit-text-fill-color:{TS};margin:0.15rem 0 0;font-size:0.78rem;">
        Visiting Faculty: NMIMS Bangalore  ·  BITS Pilani  ·  RV University Bangalore  ·  Goa Institute of Management
      </p>
    </div>""")

def footer():
    st.divider()
    st.html(f"""
    <div style="text-align:center;padding:1.5rem;user-select:none;">
      <p style="color:{GD};-webkit-text-fill-color:{GD};font-family:'Playfair Display',serif;
                font-weight:700;font-size:1.1rem;margin:0;">
        🏔️ The Mountain Path — World of Finance
      </p>
      <p style="color:{TP};-webkit-text-fill-color:{TP};font-size:0.88rem;margin:0.3rem 0 0;">
        Prof. V. Ravichandran  ·  28+ Years Corporate Finance &amp; Banking  ·  10+ Years Academic Excellence
      </p>
      <p style="color:{TS};-webkit-text-fill-color:{TS};font-size:0.78rem;margin:0.2rem 0 0;">
        Visiting Faculty: NMIMS Bangalore  ·  BITS Pilani  ·  RV University Bangalore  ·  Goa Institute of Management
      </p>
      <div style="margin-top:1rem;padding-top:1rem;
                  border-top:1px solid rgba(255,215,0,0.3);">
        <a href="https://www.linkedin.com/in/trichyravis" target="_blank"
           style="color:{GD};-webkit-text-fill-color:{GD};text-decoration:none;
                  margin:0 1rem;font-size:0.85rem;font-weight:600;">
          🔗 LinkedIn
        </a>
        <a href="https://github.com/trichyravis" target="_blank"
           style="color:{GD};-webkit-text-fill-color:{GD};text-decoration:none;
                  margin:0 1rem;font-size:0.85rem;font-weight:600;">
          💻 GitHub
        </a>
      </div>
    </div>""")

def df_style(df):
    return df.style\
        .set_properties(**{"font-family":"JetBrains Mono,monospace","font-size":"11px","text-align":"right"})\
        .set_table_styles([
            {"selector":"th","props":[("background-color",DB),("color",GD),
                                       ("font-weight","700"),("text-align","center"),
                                       ("font-size","11px")]},
            {"selector":"td:first-child","props":[("text-align","left"),("font-weight","600"),
                                                    ("color",LB)]},
        ])

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.html(f"""
    <div style="text-align:center;padding:0.8rem 0 1rem;
                border-bottom:1px solid rgba(255,215,0,0.3);
                margin-bottom:1rem;user-select:none;">
      <span style="font-family:'Playfair Display',serif;font-size:1.05rem;
                   color:{GD};-webkit-text-fill-color:{GD};font-weight:700;">
        🏔️ The Mountain Path
      </span><br>
      <span style="color:{LB};-webkit-text-fill-color:{LB};font-size:0.82rem;font-weight:600;">
        Prof. V. Ravichandran
      </span><br>
      <span style="color:{TS};-webkit-text-fill-color:{TS};font-size:0.72rem;">
        FCFF &amp; APV Valuation Model
      </span>
    </div>""")

    # ── Company ──────────────────────────────────────────────────────────────
    st.markdown(f'<div style="color:{GD};font-weight:700;font-size:0.9rem;margin-bottom:6px;">🏢 Company</div>',
                unsafe_allow_html=True)
    company = st.text_input("Company Name", value="Nova Coatings Ltd.", key="company")
    currency = st.selectbox("Currency Unit", ["₹ Crore", "$ Million", "€ Million"], key="curr")
    curr = currency.split()[0]

    st.markdown("---")

    # ── FCFF Projections ─────────────────────────────────────────────────────
    st.markdown(f'<div style="color:{GD};font-weight:700;font-size:0.9rem;margin-bottom:6px;">📈 5-Year FCFF Inputs</div>',
                unsafe_allow_html=True)

    n_years = 5
    rev_default   = [1200, 1500, 1900, 2300, 2600]
    cogs_pct_def  = [58.3, 60.0, 57.9, 56.5, 57.7]
    sga_def       = [220,  260,  300,  350,  380]
    dep_def       = [30,   30,   40,   40,   40]
    capex_def     = [60,   70,   200,  70,   60]
    nwc_def       = [40,   25,   30,   30,   20]
    tax_rate      = st.slider("Corporate Tax Rate (%)", 0.0, 50.0, 25.0, 0.5, key="tax") / 100

    st.markdown(f'<div style="color:{LB};font-size:0.82rem;margin:8px 0 4px;">Revenue (each year)</div>', unsafe_allow_html=True)
    revenues = [st.number_input(f"FY{i+1}", value=float(rev_default[i]),
                                min_value=0.0, step=10.0, key=f"rev{i}") for i in range(n_years)]

    with st.expander("⚙️ COGS, SG&A, Dep, CapEx, ΔNWC"):
        cogs_pct = [st.number_input(f"COGS % FY{i+1}", value=cogs_pct_def[i],
                                     min_value=0.0, max_value=100.0, step=0.5, key=f"cogs{i}") / 100
                    for i in range(n_years)]
        sga   = [st.number_input(f"SG&A FY{i+1}", value=float(sga_def[i]),   step=5.0, key=f"sga{i}")  for i in range(n_years)]
        dep   = [st.number_input(f"Dep FY{i+1}",  value=float(dep_def[i]),   step=5.0, key=f"dep{i}")  for i in range(n_years)]
        capex = [st.number_input(f"CapEx FY{i+1}",value=float(capex_def[i]), step=5.0, key=f"cap{i}")  for i in range(n_years)]
        dnwc  = [st.number_input(f"ΔNWC FY{i+1}", value=float(nwc_def[i]),   step=5.0, key=f"nwc{i}")  for i in range(n_years)]

    st.markdown("---")

    # ── Cost of Capital ───────────────────────────────────────────────────────
    st.markdown(f'<div style="color:{GD};font-weight:700;font-size:0.9rem;margin-bottom:6px;">💰 Cost of Capital</div>',
                unsafe_allow_html=True)
    rf      = st.slider("Risk-Free Rate Rf (%)",      2.0, 12.0, 6.0,  0.25, key="rf")  / 100
    erp     = st.slider("Equity Risk Premium (%)",    3.0, 10.0, 6.0,  0.25, key="erp") / 100
    beta_u  = st.slider("Asset Beta β_U",             0.3,  2.0, 0.85, 0.05, key="bu")
    kd_pre  = st.slider("Pre-tax Cost of Debt (%)",   4.0, 15.0, 8.0,  0.25, key="kd")  / 100
    g       = st.slider("Terminal Growth Rate g (%)", 0.0,  8.0, 4.0,  0.25, key="g")   / 100

    st.markdown("---")

    # ── Method Selector ───────────────────────────────────────────────────────
    st.markdown(f'<div style="color:{GD};font-weight:700;font-size:0.9rem;margin-bottom:6px;">🔧 Valuation Method</div>',
                unsafe_allow_html=True)
    method = st.radio("Select Method", ["WACC Method", "APV Method", "Both Methods"],
                      index=2, key="method")

    st.markdown("---")

    # ── Capital Structure ─────────────────────────────────────────────────────
    st.markdown(f'<div style="color:{GD};font-weight:700;font-size:0.9rem;margin-bottom:6px;">🏗️ Capital Structure</div>',
                unsafe_allow_html=True)

    if method in ["WACC Method", "Both Methods"]:
        wacc_policy = st.selectbox("WACC Debt Policy",
                                   ["Constant D/V ratio", "Constant D/E ratio"], key="wpol")
        if wacc_policy == "Constant D/V ratio":
            dv_ratio = st.slider("D/V Ratio (%)", 0.0, 60.0, 30.0, 1.0, key="dv") / 100
            de_ratio_wacc = dv_ratio / max(1 - dv_ratio, 0.001)
        else:
            de_ratio_wacc = st.slider("D/E Ratio", 0.0, 3.0, 0.5, 0.05, key="de_wacc")
            dv_ratio = de_ratio_wacc / (1 + de_ratio_wacc)

    if method in ["APV Method", "Both Methods"]:
        debt_type = st.selectbox("APV Debt Policy",
                                 ["Perpetual (permanent) debt", "Finite debt — repaid at Year N"],
                                 key="dtype")
        debt_amount = st.number_input(f"Debt Amount ({curr})", value=500.0, min_value=0.0,
                                       step=10.0, key="damt")
        if debt_type == "Finite debt — repaid at Year N":
            debt_years = st.slider("Debt Repaid at End of Year", 1, 10, 5, key="dyrs")
        else:
            debt_years = None

# ══════════════════════════════════════════════════════════════════════════════
# CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════

years = [f"FY{i+1}" for i in range(n_years)]

# ── FCFF ──────────────────────────────────────────────────────────────────────
cogs_abs  = [revenues[i] * cogs_pct[i] for i in range(n_years)]
gross     = [revenues[i] - cogs_abs[i] for i in range(n_years)]
ebitda    = [gross[i] - sga[i] for i in range(n_years)]
ebit      = [ebitda[i] - dep[i] for i in range(n_years)]
nopat     = [ebit[i] * (1 - tax_rate) for i in range(n_years)]
fcff      = [nopat[i] + dep[i] - capex[i] - dnwc[i] for i in range(n_years)]

# ── Costs ─────────────────────────────────────────────────────────────────────
r0    = rf + beta_u * erp          # unlevered cost of capital
kd_at = kd_pre * (1 - tax_rate)    # after-tax cost of debt

# ── WACC Method ───────────────────────────────────────────────────────────────
if method in ["WACC Method", "Both Methods"]:
    ev_wacc = de_ratio_wacc
    beta_l_wacc = beta_u * (1 + (1 - tax_rate) * de_ratio_wacc)
    ke_wacc = rf + beta_l_wacc * erp
    wacc = (1 - dv_ratio) * ke_wacc + dv_ratio * kd_at
    tv_wacc = fcff[-1] * (1 + g) / (wacc - g) if wacc > g else None
    # Discount FCFFs + TV
    pv_fcff_wacc = [fcff[i] / (1 + wacc) ** (i + 1) for i in range(n_years)]
    pv_tv_wacc   = (tv_wacc / (1 + wacc) ** n_years) if tv_wacc else 0
    ev_wacc_val  = sum(pv_fcff_wacc) + pv_tv_wacc
    # Debt and equity
    debt_wacc   = dv_ratio * ev_wacc_val
    equity_wacc = ev_wacc_val - debt_wacc

# ── APV Method ────────────────────────────────────────────────────────────────
if method in ["APV Method", "Both Methods"]:
    tv_apv = fcff[-1] * (1 + g) / (r0 - g) if r0 > g else None
    pv_fcff_apv = [fcff[i] / (1 + r0) ** (i + 1) for i in range(n_years)]
    pv_tv_apv   = (tv_apv / (1 + r0) ** n_years) if tv_apv else 0
    vu          = sum(pv_fcff_apv) + pv_tv_apv

    # Tax shield
    if debt_type == "Perpetual (permanent) debt":
        pv_ts = tax_rate * debt_amount
        ts_label = f"Perpetual: Tc × D = {tax_rate*100:.0f}% × {debt_amount:,.0f}"
        ts_annual = kd_pre * debt_amount * tax_rate
        ts_years_list = [ts_annual] * n_years
        ts_pv_list    = [ts_annual / (1 + kd_pre) ** (i + 1) for i in range(n_years)]
    else:
        ts_annual    = kd_pre * debt_amount * tax_rate
        n_d          = debt_years
        ann_factor   = (1 - (1 + kd_pre) ** (-n_d)) / kd_pre if n_d > 0 else 0
        pv_ts        = ts_annual * ann_factor
        ts_label     = f"{n_d}-yr annuity at Rd={kd_pre*100:.1f}%: {ts_annual:,.1f} × {ann_factor:.4f}"
        ts_years_list = [ts_annual if i < n_d else 0.0 for i in range(n_years)]
        ts_pv_list    = [ts_years_list[i] / (1 + kd_pre) ** (i + 1) for i in range(n_years)]

    vl_apv      = vu + pv_ts
    equity_apv  = vl_apv - debt_amount

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════
header()

# Session state for method display
if "top_nav" not in st.session_state:
    st.session_state.top_nav = "📊 FCFF Build"

nav1, nav2, nav3, nav4, nav5, nav6 = st.columns(6)
with nav1:
    if st.button("📊 FCFF Build",     use_container_width=True, key="n1"): st.session_state.top_nav = "📊 FCFF Build"
with nav2:
    if st.button("📈 WACC Valuation", use_container_width=True, key="n2"): st.session_state.top_nav = "📈 WACC Valuation"
with nav3:
    if st.button("🔬 APV Valuation",  use_container_width=True, key="n3"): st.session_state.top_nav = "🔬 APV Valuation"
with nav4:
    if st.button("💥 MM with Tax",    use_container_width=True, key="n4"): st.session_state.top_nav = "💥 MM with Tax"
with nav5:
    if st.button("⚖️ Comparison",     use_container_width=True, key="n5"): st.session_state.top_nav = "⚖️ Comparison"
with nav6:
    if st.button("📖 Methodology",    use_container_width=True, key="n6"): st.session_state.top_nav = "📖 Methodology"

active = st.session_state.top_nav
st.markdown(f"""
<div style="background:linear-gradient(135deg,{DB},{MB});border:2px solid {GD};
            border-radius:8px;padding:8px 18px;margin:8px 0 14px;display:inline-block;">
  <span style="color:{GD};font-size:1rem;font-weight:700;">▶ &nbsp; {active}</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FCFF BUILD
# ══════════════════════════════════════════════════════════════════════════════
if active == "📊 FCFF Build":
    sec("📊 FCFF Build — Free Cash Flow to Firm")

    # KPI strip
    k1, k2, k3, k4, k5 = st.columns(5)
    total_rev  = sum(revenues)
    total_fcff = sum(fcff)
    avg_ebit_m = np.mean([ebit[i] / revenues[i] for i in range(n_years)]) * 100
    fy5_fcff   = fcff[-1]
    with k1: mcard("Total Revenue", f"{curr} {total_rev:,.0f}", sub="5-Year Sum")
    with k2: mcard("Total FCFF",    f"{curr} {total_fcff:,.1f}", sub="5-Year Sum",
                   color=GR if total_fcff > 0 else RD)
    with k3: mcard("Avg EBIT Margin", f"{avg_ebit_m:.1f}%", sub="5-Year Average")
    with k4: mcard("FY5 FCFF",  f"{curr} {fy5_fcff:,.1f}", sub="Terminal Base",
                   color=GR if fy5_fcff > 0 else RD)
    with k5: mcard("Tax Rate", f"{tax_rate*100:.1f}%", sub="Corporate")

    st.markdown("---")

    # Income Statement & FCFF Table
    sec("📋 Income Statement & FCFF Derivation")
    fbox("FCFF  =  EBIT × (1 − Tc)  +  Depreciation  −  CapEx  −  ΔNWC")

    fcff_df = pd.DataFrame({
        "Item":    ["Revenue", "COGS", "Gross Profit", "SG&A", "EBITDA", "Depreciation",
                    "EBIT", "Tax (EBIT×Tc)", "NOPAT = EBIT(1−Tc)",
                    "Add: Depreciation", "Less: CapEx", "Less: ΔNWC", "─────────────",
                    "FCFF"],
    })
    for i, yr in enumerate(years):
        fcff_df[yr] = [
            f"{revenues[i]:,.1f}", f"({cogs_abs[i]:,.1f})", f"{gross[i]:,.1f}",
            f"({sga[i]:,.1f})", f"{ebitda[i]:,.1f}", f"({dep[i]:,.1f})",
            f"{ebit[i]:,.1f}", f"({ebit[i]*tax_rate:,.1f})", f"{nopat[i]:,.1f}",
            f"{dep[i]:,.1f}", f"({capex[i]:,.1f})", f"({dnwc[i]:,.1f})", "─────",
            f"{fcff[i]:,.1f}",
        ]
    fcff_df = fcff_df.set_index("Item")
    st.dataframe(df_style(fcff_df), use_container_width=True)

    st.markdown("---")

    # FCFF Bar chart
    sec("📊 FCFF Visualisation")
    c1, c2 = st.columns(2)
    with c1:
        fig_fcff = go.Figure(go.Bar(
            x=years, y=fcff, marker_color=[GR if v >= 0 else RD for v in fcff],
            text=[f"{curr} {v:,.1f}" for v in fcff], textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=TP), width=0.55))
        fig_fcff.update_layout(**playout(height=320),
            title=dict(text=f"FCFF by Year ({curr})", font=dict(color=GD, size=13), x=0),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title=curr, gridcolor="rgba(255,255,255,0.05)"),
            showlegend=False)
        st.plotly_chart(fig_fcff, use_container_width=True, key="fcff_bar")

    with c2:
        # Revenue vs EBIT waterfall
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(x=years, y=revenues,
            mode="lines+markers", name="Revenue",
            line=dict(color=LB, width=2.5),
            marker=dict(size=8, color=LB)))
        fig_rev.add_trace(go.Scatter(x=years, y=ebit,
            mode="lines+markers", name="EBIT",
            line=dict(color=GD, width=2.5, dash="dash"),
            marker=dict(size=8, color=GD)))
        fig_rev.add_trace(go.Scatter(x=years, y=fcff,
            mode="lines+markers", name="FCFF",
            line=dict(color=GR, width=2.5, dash="dot"),
            marker=dict(size=8, color=GR)))
        fig_rev.update_layout(**playout(height=320),
            title=dict(text="Revenue, EBIT and FCFF Trend", font=dict(color=GD, size=13), x=0),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title=curr, gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP)))
        st.plotly_chart(fig_rev, use_container_width=True, key="rev_trend")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — WACC VALUATION
# ══════════════════════════════════════════════════════════════════════════════
elif active == "📈 WACC Valuation":
    if method not in ["WACC Method", "Both Methods"]:
        st.warning("Select 'WACC Method' or 'Both Methods' in the sidebar to enable this tab.")
    else:
        sec("📈 WACC Valuation — Step-by-Step")

        if tv_wacc is None:
            st.error(f"⚠ WACC ({wacc*100:.2f}%) ≤ Terminal Growth ({g*100:.1f}%). Increase WACC or reduce g.")
        else:
            # KPI strip
            k1, k2, k3, k4 = st.columns(4)
            with k1: mcard("β_L (Levered Beta)", f"{beta_l_wacc:.4f}", sub=f"β_U={beta_u} × [1+(1-t)×D/E]")
            with k2: mcard("Cost of Equity k_e", f"{ke_wacc*100:.2f}%", sub=f"Rf+β_L×ERP")
            with k3: mcard("WACC", f"{wacc*100:.2f}%", sub=f"D/V={dv_ratio*100:.1f}%")
            with k4: mcard("Enterprise Value", f"{curr} {ev_wacc_val:,.1f}", sub="EV (WACC)", color=GD)

            st.markdown("---")

            # Working steps
            sec("🔢 Step-by-Step WACC Calculation")
            ibox(f"""
            <b>Step 1 — Relever Beta (Hamada):</b><br>
            β_L = β_U × [1 + (1−T_c) × D/E] = {beta_u} × [1 + (1−{tax_rate:.2f}) × {de_ratio_wacc:.4f}] = <b>{beta_l_wacc:.4f}</b><br><br>
            <b>Step 2 — Cost of Equity (CAPM):</b><br>
            k_e = R_f + β_L × ERP = {rf*100:.2f}% + {beta_l_wacc:.4f} × {erp*100:.2f}% = <b>{ke_wacc*100:.2f}%</b><br><br>
            <b>Step 3 — WACC:</b><br>
            WACC = (E/V)×k_e + (D/V)×k_d×(1−T_c)
            = {(1-dv_ratio)*100:.1f}%×{ke_wacc*100:.2f}% + {dv_ratio*100:.1f}%×{kd_pre*100:.2f}%×{1-tax_rate:.2f}
            = <b>{wacc*100:.2f}%</b><br><br>
            <b>Step 4 — Terminal Value (Gordon Growth):</b><br>
            TV = FCFF₅×(1+g) / (WACC−g) = {fcff[-1]:,.1f}×{1+g:.3f} / ({wacc*100:.2f}%−{g*100:.1f}%) = <b>{curr} {tv_wacc:,.1f}</b>
            """, title="WACC Computation")

            st.markdown("---")
            sec("📋 WACC Valuation Table")
            fbox("Enterprise Value  =  Σ [FCFF_t / (1+WACC)^t]  +  TV / (1+WACC)^N")

            rows = []
            cum_pv = 0
            for i in range(n_years):
                disc = (1 + wacc) ** (i + 1)
                pv   = pv_fcff_wacc[i]
                cum_pv += pv
                rows.append({
                    "Year": years[i],
                    f"FCFF ({curr})": f"{fcff[i]:,.1f}",
                    "Discount Factor": f"{1/disc:.4f}",
                    f"PV of FCFF ({curr})": f"{pv:,.1f}",
                    f"Cumulative PV ({curr})": f"{cum_pv:,.1f}",
                })
            rows.append({
                "Year": f"TV (FY{n_years})",
                f"FCFF ({curr})": f"{tv_wacc:,.1f}",
                "Discount Factor": f"{1/(1+wacc)**n_years:.4f}",
                f"PV of FCFF ({curr})": f"{pv_tv_wacc:,.1f}",
                f"Cumulative PV ({curr})": f"{ev_wacc_val:,.1f}",
            })
            wacc_df = pd.DataFrame(rows).set_index("Year")
            st.dataframe(df_style(wacc_df), use_container_width=True)

            st.markdown("---")

            # Summary & charts
            sec("📊 Value Attribution & Equity Bridge")
            c1, c2 = st.columns(2)
            with c1:
                ex_pv = sum(pv_fcff_wacc)
                pie_data = {
                    "Explicit Period FCFFs": ex_pv,
                    "Terminal Value PV": pv_tv_wacc,
                }
                fig_pie = go.Figure(go.Pie(
                    labels=list(pie_data.keys()),
                    values=list(pie_data.values()),
                    hole=0.45,
                    marker=dict(colors=[LB, GD], line=dict(color=CB, width=2)),
                    textfont=dict(color=TD, size=11),
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value:,.1f}<br>%{percent}<extra></extra>"))
                fig_pie.update_layout(**playout(height=300, margin=dict(l=20,r=20,t=40,b=20)),
                    title=dict(text="Value Attribution (WACC)", font=dict(color=GD, size=13), x=0),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP, size=10)))
                st.plotly_chart(fig_pie, use_container_width=True, key="wacc_pie")

            with c2:
                # Equity bridge waterfall
                wf_labels = ["Enterprise Value", "Less: Debt", "Equity Value"]
                wf_values = [ev_wacc_val, -debt_wacc, equity_wacc]
                fig_wf = go.Figure(go.Waterfall(
                    orientation="v", measure=["absolute", "relative", "total"],
                    x=wf_labels, y=wf_values,
                    connector=dict(line=dict(color=TS)),
                    increasing=dict(marker_color=GD),
                    decreasing=dict(marker_color=RD),
                    totals=dict(marker_color=GR),
                    text=[f"{curr} {abs(v):,.1f}" for v in wf_values],
                    textposition="outside",
                    textfont=dict(family="JetBrains Mono", size=10, color=TP)))
                fig_wf.update_layout(**playout(height=300, margin=dict(l=20,r=80,t=40,b=30)),
                    title=dict(text="Equity Value Bridge (WACC)", font=dict(color=GD, size=13), x=0),
                    showlegend=False,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
                st.plotly_chart(fig_wf, use_container_width=True, key="wacc_wf")

            st.markdown("---")
            r1, r2, r3 = st.columns(3)
            with r1: mcard("Enterprise Value (EV)", f"{curr} {ev_wacc_val:,.1f}", color=GD)
            with r2: mcard("Less: Debt", f"{curr} ({debt_wacc:,.1f})", color=RD)
            with r3: mcard("Equity Value", f"{curr} {equity_wacc:,.1f}",
                           sub="EV − Debt", color=GR if equity_wacc > 0 else RD)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — APV VALUATION
# ══════════════════════════════════════════════════════════════════════════════
elif active == "🔬 APV Valuation":
    if method not in ["APV Method", "Both Methods"]:
        st.warning("Select 'APV Method' or 'Both Methods' in the sidebar to enable this tab.")
    else:
        sec("🔬 APV Valuation — Adjusted Present Value")

        if tv_apv is None:
            st.error(f"⚠ r₀ ({r0*100:.2f}%) ≤ Terminal Growth ({g*100:.1f}%). Increase r₀ or reduce g.")
        else:
            # KPI strip
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1: mcard("Unlevered Cost r₀", f"{r0*100:.2f}%", sub=f"Rf+β_U×ERP")
            with k2: mcard("Unlevered Value V_U", f"{curr} {vu:,.1f}", sub="DCF at r₀")
            with k3: mcard("PV Tax Shield", f"{curr} {pv_ts:,.1f}",
                           sub="Perpetual" if debt_type.startswith("Perpetual") else f"{debt_years}-yr annuity",
                           color=GD)
            with k4: mcard("APV (V_L)", f"{curr} {vl_apv:,.1f}",
                           sub="V_U + PV(TS)", color=GD)
            with k5: mcard("Equity Value", f"{curr} {equity_apv:,.1f}",
                           sub="V_L − Debt", color=GR if equity_apv > 0 else RD)

            st.markdown("---")

            # Working steps
            sec("🔢 Step-by-Step APV Calculation")
            ibox(f"""
            <b>Step 1 — Unlevered Cost of Capital r₀:</b><br>
            r₀ = R_f + β_U × ERP = {rf*100:.2f}% + {beta_u} × {erp*100:.2f}% = <b>{r0*100:.2f}%</b><br><br>
            <b>Step 2 — Terminal Value (Unlevered, Gordon Growth):</b><br>
            TV = FCFF₅×(1+g) / (r₀−g) = {fcff[-1]:,.1f}×{1+g:.3f} / ({r0*100:.2f}%−{g*100:.1f}%) = <b>{curr} {tv_apv:,.1f}</b><br><br>
            <b>Step 3 — Unlevered Firm Value V_U:</b><br>
            V_U = Σ FCFF_t/(1+r₀)^t + TV/(1+r₀)^N = <b>{curr} {vu:,.1f}</b><br><br>
            <b>Step 4 — PV of Tax Shield:</b><br>
            {'Perpetual: PV(TS) = Tc × D = ' + f'{tax_rate*100:.0f}% × {debt_amount:,.0f} = {curr} {pv_ts:,.1f}'
             if debt_type.startswith("Perpetual")
             else f'Finite ({debt_years}-yr annuity at k_d={kd_pre*100:.1f}%):<br>'
                  f'Annual TS = k_d × D × Tc = {kd_pre*100:.1f}% × {debt_amount:,.0f} × {tax_rate:.2f} = {curr} {kd_pre*debt_amount*tax_rate:,.1f}<br>'
                  f'Annuity Factor = [1−(1+k_d)^−N]/k_d = {(1-(1+kd_pre)**(-debt_years))/kd_pre:.4f}<br>'
                  f'PV(TS) = {kd_pre*debt_amount*tax_rate:,.1f} × {(1-(1+kd_pre)**(-debt_years))/kd_pre:.4f} = <b>{curr} {pv_ts:,.1f}</b>'}<br><br>
            <b>Step 5 — APV:</b><br>
            V_L = V_U + PV(TS) = {vu:,.1f} + {pv_ts:,.1f} = <b>{curr} {vl_apv:,.1f}</b><br><br>
            <b>Step 6 — Equity Value:</b><br>
            Equity = V_L − D = {vl_apv:,.1f} − {debt_amount:,.1f} = <b>{curr} {equity_apv:,.1f}</b>
            """, title="APV Computation")

            st.markdown("---")
            sec("📋 APV Valuation Tables")

            # V_U table
            st.markdown(f"<p style='color:{LB};font-weight:600;'>Unlevered Firm Value (V_U)</p>",
                        unsafe_allow_html=True)
            vu_rows = []
            cum_vu = 0
            for i in range(n_years):
                pv = pv_fcff_apv[i]
                cum_vu += pv
                vu_rows.append({"Year": years[i],
                                f"FCFF ({curr})": f"{fcff[i]:,.1f}",
                                "Disc. at r₀": f"{1/(1+r0)**(i+1):.4f}",
                                f"PV ({curr})": f"{pv:,.1f}",
                                f"Cum. PV ({curr})": f"{cum_vu:,.1f}"})
            vu_rows.append({"Year": f"TV(FY{n_years})",
                            f"FCFF ({curr})": f"{tv_apv:,.1f}",
                            "Disc. at r₀": f"{1/(1+r0)**n_years:.4f}",
                            f"PV ({curr})": f"{pv_tv_apv:,.1f}",
                            f"Cum. PV ({curr})": f"{vu:,.1f}"})
            vu_df = pd.DataFrame(vu_rows).set_index("Year")
            st.dataframe(df_style(vu_df), use_container_width=True)

            # Tax shield table
            st.markdown(f"<p style='color:{LB};font-weight:600;margin-top:12px;'>Tax Shield Schedule ({ts_label})</p>",
                        unsafe_allow_html=True)
            ts_rows = []
            cum_ts = 0
            for i in range(n_years):
                cum_ts += ts_pv_list[i]
                ts_rows.append({"Year": years[i],
                                "Debt Outstanding": f"{debt_amount:,.1f}" if ts_years_list[i] > 0 else "0",
                                f"Interest = k_d×D ({curr})": f"{kd_pre*debt_amount:,.1f}" if ts_years_list[i] > 0 else "0",
                                f"Tax Shield = TS×Tc ({curr})": f"{ts_years_list[i]:,.1f}",
                                "Disc. at k_d": f"{1/(1+kd_pre)**(i+1):.4f}",
                                f"PV of TS ({curr})": f"{ts_pv_list[i]:,.1f}",
                                f"Cum. PV ({curr})": f"{cum_ts:,.1f}"})
            if debt_type.startswith("Perpetual"):
                ts_rows.append({"Year": "Terminal TS",
                                "Debt Outstanding": f"{debt_amount:,.1f}",
                                f"Interest = k_d×D ({curr})": f"{kd_pre*debt_amount:,.1f}",
                                f"Tax Shield = TS×Tc ({curr})": f"{kd_pre*debt_amount*tax_rate:,.1f} (perpetuity)",
                                "Disc. at k_d": "Tc×D formula",
                                f"PV of TS ({curr})": f"{pv_ts - sum(ts_pv_list[:n_years]):,.1f}",
                                f"Cum. PV ({curr})": f"{pv_ts:,.1f}"})
            ts_df = pd.DataFrame(ts_rows).set_index("Year")
            st.dataframe(df_style(ts_df), use_container_width=True)

            st.markdown("---")

            # APV chart
            c1, c2 = st.columns(2)
            with c1:
                fig_apv = go.Figure(go.Bar(
                    x=["V_U (Unlevered)", "PV Tax Shield", "V_L (APV)"],
                    y=[vu, pv_ts, vl_apv],
                    marker_color=[LB, GD, GR],
                    text=[f"{curr} {v:,.1f}" for v in [vu, pv_ts, vl_apv]],
                    textposition="outside",
                    textfont=dict(family="JetBrains Mono", size=10, color=TP),
                    width=0.55))
                fig_apv.update_layout(**playout(height=310),
                    title=dict(text="APV Build-Up", font=dict(color=GD, size=13), x=0),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(title=curr, gridcolor="rgba(255,255,255,0.05)"),
                    showlegend=False)
                st.plotly_chart(fig_apv, use_container_width=True, key="apv_bar")

            with c2:
                fig_ts = go.Figure()
                fig_ts.add_trace(go.Bar(x=years, y=ts_years_list,
                    marker_color=GD, opacity=0.85, name="Annual Tax Shield",
                    text=[f"{v:,.1f}" for v in ts_years_list],
                    textposition="outside",
                    textfont=dict(family="JetBrains Mono", size=9, color=TP)))
                fig_ts.add_trace(go.Scatter(x=years, y=[sum(ts_pv_list[:i+1]) for i in range(n_years)],
                    mode="lines+markers", name="Cumulative PV(TS)",
                    line=dict(color=LB, width=2), yaxis="y2"))
                fig_ts.update_layout(**playout(height=310),
                    title=dict(text="Tax Shield Schedule", font=dict(color=GD, size=13), x=0),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(title="Annual TS", gridcolor="rgba(255,255,255,0.05)"),
                    yaxis2=dict(title="Cumulative PV", overlaying="y", side="right",
                                tickfont=dict(color=LB), color=LB),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP)))
                st.plotly_chart(fig_ts, use_container_width=True, key="ts_bar")


# ══════════════════════════════════════════════════════════════════════════════
# TAB — MM WITH TAX + BANKRUPTCY COSTS (TRADE-OFF THEORY)
# ══════════════════════════════════════════════════════════════════════════════
elif active == "💥 MM with Tax":
    sec("💥 MM with Corporate Tax + Bankruptcy Costs — Trade-Off Theory")

    ibox(f"""
    <b>MM Proposition I with Tax:</b> V_L = V_U + T_c × D  (tax shield adds value with each ₹ of debt)<br>
    <b>Trade-Off Theory:</b> V_L = V_U + T_c × D − PV(Bankruptcy Costs)<br><br>
    As debt rises: the tax shield grows linearly, but expected bankruptcy costs grow non-linearly.
    The <b>optimal capital structure</b> is where the marginal benefit of the tax shield exactly
    equals the marginal expected bankruptcy cost.
    """, title="The Trade-Off Theory Framework")

    st.markdown("---")
    sec("⚙️ Bankruptcy Cost Parameters")

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        bc_total = st.number_input(
            f"Total Bankruptcy Cost if it occurs ({curr})",
            value=200.0, min_value=0.0, step=10.0, key="bc_total")
    with bc2:
        n_debt_plans = st.slider("Number of Debt Plans", 3, 8, 5, key="ndp")
    with bc3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="lbl">Unlevered Firm Value V_U</div>
          <div class="val" style="color:{LB};-webkit-text-fill-color:{LB};">
            {curr} {vu if method in ["APV Method","Both Methods"] and tv_apv is not None else "—"}
          </div>
          <div class="sub">From APV tab (set APV method)</div>
        </div>""", unsafe_allow_html=True)

    # Let user define debt levels and bankruptcy probabilities
    st.markdown(f"""
    <div class="section-title">📋 Debt Plans — Enter Debt Levels and Bankruptcy Probabilities</div>
    """, unsafe_allow_html=True)

    # Default debt levels and probs
    default_debts = [0, 200, 400, 600, 800, 1000, 1200, 1500]
    default_probs = [0.0, 1.5, 3.0, 6.0, 12.0, 20.0, 30.0, 45.0]

    cols_hdr = st.columns([2, 2, 2])
    with cols_hdr[0]:
        st.markdown(f"<p style='color:{GD};font-weight:700;font-size:0.85rem;'>Plan</p>", unsafe_allow_html=True)
    with cols_hdr[1]:
        st.markdown(f"<p style='color:{GD};font-weight:700;font-size:0.85rem;'>Debt ({curr})</p>", unsafe_allow_html=True)
    with cols_hdr[2]:
        st.markdown(f"<p style='color:{GD};font-weight:700;font-size:0.85rem;'>P(Bankruptcy) %</p>", unsafe_allow_html=True)

    plan_debts = []
    plan_probs = []
    plan_names = ["A","B","C","D","E","F","G","H"]

    for i in range(n_debt_plans):
        c1_, c2_, c3_ = st.columns([2, 2, 2])
        with c1_:
            st.markdown(f"<p style='color:{LB};font-size:0.88rem;padding:6px 0;'><b>Plan {plan_names[i]}</b></p>",
                        unsafe_allow_html=True)
        with c2_:
            d = st.number_input("", value=float(default_debts[i]), min_value=0.0, step=50.0,
                                key=f"pd_{i}", label_visibility="collapsed")
        with c3_:
            p = st.number_input("", value=default_probs[i], min_value=0.0, max_value=100.0,
                                step=0.5, key=f"pp_{i}", label_visibility="collapsed")
        plan_debts.append(d)
        plan_probs.append(p / 100.0)

    st.markdown("---")

    # Use V_U from APV if available, else ask user
    if method in ["APV Method", "Both Methods"] and tv_apv is not None:
        vu_mm = vu
    else:
        vu_mm = st.number_input(
            f"Enter Unlevered Firm Value V_U ({curr}) manually:",
            value=2000.0, min_value=0.0, step=100.0, key="vu_mm")
        st.info("💡 Run the APV Method in the sidebar to auto-populate V_U from your FCFF projections.")

    # ── Calculations ──────────────────────────────────────────────────────────
    ts_list    = [tax_rate * d for d in plan_debts]               # Tax shield
    exp_bc_list = [p * bc_total for p, d in zip(plan_probs, plan_debts)]  # Expected BC
    vl_mm_list  = [vu_mm + ts - ebc for ts, ebc in zip(ts_list, exp_bc_list)]  # V_L
    eq_mm_list  = [vl - d for vl, d in zip(vl_mm_list, plan_debts)]

    best_idx = int(np.argmax(vl_mm_list))

    # ── KPI row ────────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1: mcard("V_U (All-Equity Value)", f"{curr} {vu_mm:,.1f}", sub="Baseline")
    with k2: mcard("Max Tax Shield", f"{curr} {max(ts_list):,.1f}",
                   sub=f"Plan {plan_names[ts_list.index(max(ts_list))]}", color=GD)
    with k3: mcard("Optimal Plan", f"Plan {plan_names[best_idx]}",
                   sub=f"D = {curr} {plan_debts[best_idx]:,.0f}", color=GR)
    with k4: mcard("Maximum V_L", f"{curr} {max(vl_mm_list):,.1f}",
                   sub="Trade-Off Optimum", color=GR)

    st.markdown("---")

    # ── Summary Table ──────────────────────────────────────────────────────────
    sec("📋 Trade-Off Theory — Full Computation Table")
    fbox("V_L  =  V_U  +  T_c × D  −  P(Bankruptcy) × Bankruptcy Cost")

    rows_mm = []
    for i in range(n_debt_plans):
        rows_mm.append({
            "Plan": f"Plan {plan_names[i]}",
            f"Debt ({curr})": f"{plan_debts[i]:,.0f}",
            f"V_U ({curr})": f"{vu_mm:,.1f}",
            "Tax Rate Tc": f"{tax_rate*100:.1f}%",
            f"Tax Shield = Tc×D ({curr})": f"{ts_list[i]:,.1f}",
            "P(Bankruptcy)": f"{plan_probs[i]*100:.1f}%",
            f"Exp. BC = P×Total ({curr})": f"{exp_bc_list[i]:,.1f}",
            f"V_L = VU+TS−EBC ({curr})": f"{vl_mm_list[i]:,.1f}",
            f"Equity = VL−D ({curr})": f"{eq_mm_list[i]:,.1f}",
            "Optimal?": "✅ OPTIMAL" if i == best_idx else "",
        })

    mm_df = pd.DataFrame(rows_mm).set_index("Plan")
    st.dataframe(df_style(mm_df), use_container_width=True)

    st.markdown("---")

    # ── Charts ─────────────────────────────────────────────────────────────────
    sec("📊 Trade-Off Theory Visualisations")
    fig_mm = make_subplots(rows=1, cols=2,
        subplot_titles=["Firm Value Components by Plan",
                        "V_L, Tax Shield and Expected BC"],
        horizontal_spacing=0.08)

    plan_lbls = [f"Plan {plan_names[i]}" for i in range(n_debt_plans)]

    # Left: stacked bar — V_U base + tax shield − exp BC
    fig_mm.add_trace(go.Bar(name="V_U (Base)", x=plan_lbls,
        y=[vu_mm]*n_debt_plans, marker_color=MB, opacity=0.8), row=1, col=1)
    fig_mm.add_trace(go.Bar(name="Tax Shield (+)", x=plan_lbls,
        y=ts_list, marker_color=GD, opacity=0.9), row=1, col=1)
    fig_mm.add_trace(go.Bar(name="Expected BC (−)", x=plan_lbls,
        y=[-e for e in exp_bc_list], marker_color=RD, opacity=0.9), row=1, col=1)

    # Right: line chart — V_L vs D
    fig_mm.add_trace(go.Scatter(x=plan_lbls, y=vl_mm_list,
        mode="lines+markers", name="V_L (Trade-Off)",
        line=dict(color=GR, width=2.5),
        marker=dict(size=9, color=[GD if i == best_idx else GR for i in range(n_debt_plans)])),
        row=1, col=2)
    fig_mm.add_trace(go.Scatter(x=plan_lbls, y=ts_list,
        mode="lines+markers", name="Tax Shield",
        line=dict(color=GD, width=1.8, dash="dash"),
        marker=dict(size=7, color=GD)), row=1, col=2)
    fig_mm.add_trace(go.Scatter(x=plan_lbls, y=exp_bc_list,
        mode="lines+markers", name="Expected BC",
        line=dict(color=RD, width=1.8, dash="dot"),
        marker=dict(size=7, color=RD)), row=1, col=2)

    # Mark optimal plan — scatter trace (add_vline fails on categorical x-axis)
    fig_mm.add_trace(go.Scatter(
        x=[f"Plan {plan_names[best_idx]}", f"Plan {plan_names[best_idx]}"],
        y=[0, max(vl_mm_list) * 1.06],
        mode="lines+text",
        line=dict(color=GD, width=2, dash="dash"),
        text=["", "  ★ Optimal"],
        textposition="top right",
        textfont=dict(color=GD, size=11),
        showlegend=False,
    ), row=1, col=2)

    # V_U reference line — horizontal scatter across all plan labels
    fig_mm.add_trace(go.Scatter(
        x=plan_lbls,
        y=[vu_mm] * n_debt_plans,
        mode="lines+text",
        line=dict(color=LB, width=1.5, dash="dot"),
        text=[""] * (n_debt_plans - 1) + [f"  V_U={vu_mm:,.0f}"],
        textposition="middle right",
        textfont=dict(color=LB, size=10),
        showlegend=False,
    ), row=1, col=2)

    fig_mm.update_layout(
        paper_bgcolor=CB, plot_bgcolor=CB,
        font=dict(color=TP, family="Source Sans Pro"),
        height=420,
        margin=dict(l=50, r=30, t=60, b=40),
        barmode="relative",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP)),
        title=dict(text="", font=dict(color=GD)),
    )
    for ax in ["xaxis","xaxis2","yaxis","yaxis2"]:
        fig_mm.update_layout(**{ax: dict(gridcolor="rgba(255,255,255,0.05)",
                                         tickfont=dict(color=TP))})
    # Subplot title colours
    for ann in fig_mm.layout.annotations:
        ann.font.color = GD

    st.plotly_chart(fig_mm, use_container_width=True, key="mm_tax_chart")

    st.markdown("---")

    # ── Sensitivity heatmap — V_L across debt and P(Bankruptcy) ───────────────
    sec("🌡 Sensitivity: V_L Across Debt Levels and Bankruptcy Probabilities")

    debt_range = np.linspace(0, max(plan_debts) * 1.2, 30)
    prob_range = np.linspace(0, 0.40, 30)
    VL_grid = np.array([[vu_mm + tax_rate * d - p * bc_total
                          for d in debt_range] for p in prob_range])

    fig_heat = go.Figure(go.Heatmap(
        z=VL_grid,
        x=np.round(debt_range, 0),
        y=np.round(prob_range * 100, 1),
        colorscale=[
            [0.0, "#8b0000"], [0.3, RD], [0.5, GD],
            [0.7, GR], [1.0, "#004d00"]
        ],
        colorbar=dict(
            title=dict(text=f"V_L ({curr})", font=dict(color=GD)),
            tickfont=dict(color=TP), thickness=14, outlinewidth=0
        ),
        hoverongaps=False,
        hovertemplate=f"Debt: %{{x:,.0f}}<br>P(BC): %{{y:.1f}}%<br>V_L: {curr} %{{z:,.1f}}<extra></extra>",
    ))

    # Mark current optimal plan
    fig_heat.add_trace(go.Scatter(
        x=[plan_debts[best_idx]], y=[plan_probs[best_idx] * 100],
        mode="markers",
        marker=dict(size=16, color=GD, symbol="star",
                    line=dict(width=2, color=TP)),
        name=f"Optimal Plan {plan_names[best_idx]}",
        showlegend=True
    ))

    fig_heat.update_layout(
        **dict(paper_bgcolor=CB, plot_bgcolor=CB,
               font=dict(color=TP, family="Source Sans Pro"),
               margin=dict(l=60, r=80, t=50, b=60)),
        title=dict(text=f"V_L Heatmap — Debt vs P(Bankruptcy) — Gold star = current optimal plan",
                   font=dict(color=GD, size=13), x=0),
        xaxis=dict(title=f"Debt Level ({curr})", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="P(Bankruptcy) %", gridcolor="rgba(255,255,255,0.05)"),
        height=420,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP)),
    )
    st.plotly_chart(fig_heat, use_container_width=True, key="mm_heatmap")

    st.markdown("---")

    # ── Interpretation ─────────────────────────────────────────────────────────
    ts_gain_opt = ts_list[best_idx]
    bc_cost_opt = exp_bc_list[best_idx]
    vl_gain_opt = vl_mm_list[best_idx] - vu_mm

    ibox(f"""
    <b>Optimal Plan: Plan {plan_names[best_idx]}</b> — Debt = {curr} {plan_debts[best_idx]:,.0f}<br><br>
    <table style="width:100%;font-size:0.87rem;border-collapse:collapse;">
    <tr style="border-bottom:1px solid rgba(255,215,0,0.3);">
      <th style="color:{GD};padding:6px;text-align:left;">Component</th>
      <th style="color:{GD};padding:6px;text-align:right;">Value ({curr})</th>
      <th style="color:{GD};padding:6px;text-align:left;">Direction</th>
    </tr>
    <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
      <td style="padding:5px;">V_U (All-equity base)</td>
      <td style="padding:5px;text-align:right;">{vu_mm:,.1f}</td>
      <td style="padding:5px;">Baseline</td>
    </tr>
    <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
      <td style="padding:5px;color:{GD};">+ Tax Shield (Tc × D)</td>
      <td style="padding:5px;text-align:right;color:{GD};">+{ts_gain_opt:,.1f}</td>
      <td style="padding:5px;color:{GD};">Value creation ↑</td>
    </tr>
    <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
      <td style="padding:5px;color:{RD};">− Expected Bankruptcy Cost</td>
      <td style="padding:5px;text-align:right;color:{RD};">−{bc_cost_opt:,.1f}</td>
      <td style="padding:5px;color:{RD};">Value erosion ↓</td>
    </tr>
    <tr>
      <td style="padding:5px;font-weight:700;">= V_L (Optimal)</td>
      <td style="padding:5px;text-align:right;font-weight:700;color:{GR};">{vl_mm_list[best_idx]:,.1f}</td>
      <td style="padding:5px;color:{GR};">Net gain: +{vl_gain_opt:,.1f}</td>
    </tr>
    </table><br>
    <b>Trade-Off Theory conclusion:</b> The optimal debt level balances the marginal tax shield gain
    against the marginal rise in expected bankruptcy costs. Beyond Plan {plan_names[best_idx]},
    bankruptcy risk accelerates faster than the tax shield grows, destroying firm value.
    """, title=f"📌 Optimal Capital Structure — Plan {plan_names[best_idx]}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif active == "⚖️ Comparison":
    sec("⚖️ WACC vs APV — Side-by-Side Comparison")

    if method == "Both Methods" and tv_wacc is not None and tv_apv is not None:
        c1, c2 = st.columns(2)
        metrics = [
            ("Discount Rate",       f"{wacc*100:.2f}% (WACC)",          f"{r0*100:.2f}% (r₀)"),
            ("Terminal Value",      f"{curr} {tv_wacc:,.1f}",            f"{curr} {tv_apv:,.1f}"),
            ("PV Explicit FCFFs",   f"{curr} {sum(pv_fcff_wacc):,.1f}",  f"{curr} {sum(pv_fcff_apv):,.1f}"),
            ("Tax Shield Treatment","Embedded in WACC",                  f"Explicit: {curr} {pv_ts:,.1f}"),
            ("Enterprise Value",    f"{curr} {ev_wacc_val:,.1f}",        f"{curr} {vl_apv:,.1f}"),
            ("Debt",                f"{curr} {debt_wacc:,.1f}",          f"{curr} {debt_amount:,.1f}"),
            ("Equity Value",        f"{curr} {equity_wacc:,.1f}",        f"{curr} {equity_apv:,.1f}"),
        ]
        with c1:
            mcard("Enterprise Value (WACC)", f"{curr} {ev_wacc_val:,.1f}", sub="WACC Method")
            mcard("Equity Value (WACC)",     f"{curr} {equity_wacc:,.1f}", sub="EV − Debt", color=GR)
        with c2:
            mcard("Enterprise Value (APV)", f"{curr} {vl_apv:,.1f}", sub="APV Method")
            mcard("Equity Value (APV)",     f"{curr} {equity_apv:,.1f}", sub="V_L − Debt", color=GR)

        st.markdown("---")

        # Comparison table
        comp_df = pd.DataFrame(metrics, columns=["Metric", "WACC Method", "APV Method"])
        comp_df = comp_df.set_index("Metric")
        st.dataframe(df_style(comp_df), use_container_width=True)

        st.markdown("---")

        # Grouped bar
        fig_cmp = go.Figure()
        for label, ev, eq, color in [
            ("WACC", ev_wacc_val, equity_wacc, LB),
            ("APV",  vl_apv,      equity_apv,  GD),
        ]:
            fig_cmp.add_trace(go.Bar(name=f"{label} — EV",  x=[f"Enterprise Value ({label})"],
                y=[ev],  marker_color=color, width=0.4,
                text=[f"{curr} {ev:,.1f}"], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color=TP)))
            fig_cmp.add_trace(go.Bar(name=f"{label} — Equity", x=[f"Equity Value ({label})"],
                y=[eq], marker_color=color, opacity=0.65, width=0.4,
                text=[f"{curr} {eq:,.1f}"], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color=TP)))

        fig_cmp.update_layout(**playout(height=380),
            title=dict(text="WACC vs APV — Enterprise and Equity Values", font=dict(color=GD,size=13), x=0),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title=curr, gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TP)),
            barmode="group")
        st.plotly_chart(fig_cmp, use_container_width=True, key="cmp_bar")

        diff_ev = ev_wacc_val - vl_apv
        ibox(f"""
        <b>Why do the two methods give different values?</b><br><br>
        The difference in Enterprise Value is <b>{curr} {abs(diff_ev):,.1f}</b>
        ({'WACC higher' if diff_ev > 0 else 'APV higher'}).<br><br>
        <b>Debt assumption drives the gap:</b><br>
        • WACC assumes debt = {dv_ratio*100:.1f}% of EV = <b>{curr} {debt_wacc:,.1f}</b> (proportional, grows with firm)<br>
        • APV assumes fixed debt = <b>{curr} {debt_amount:,.1f}</b> ({'permanent' if debt_type.startswith('Perpetual') else f'{debt_years}-year finite'})<br><br>
        {'The higher debt load under WACC creates a larger tax shield embedded in the lower discount rate, raising EV.' if debt_wacc > debt_amount
         else 'The fixed APV debt is larger, so the explicit tax shield adds more value under APV.'}<br><br>
        <b>If both methods used the same debt assumption, they would produce identical results.</b>
        """, title="Reconciliation Note")
    else:
        st.info("Select 'Both Methods' in the sidebar and ensure WACC > g and r₀ > g to see a comparison.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
elif active == "📖 Methodology":
    sec("📖 Methodology — FCFF, WACC and APV")

    c1, c2 = st.columns(2)
    with c1:
        ibox("""
        <h4 style='color:#FFD700;margin-top:0;'>Free Cash Flow to Firm (FCFF)</h4>
        <p style='font-size:0.88rem;line-height:1.9;'>
        FCFF is the cash flow generated by the firm's operations available to <b>all capital providers</b>
        — both debt and equity holders. It is capital-structure neutral:
        it is calculated as if the firm has no interest deductions.
        </p>""",
        )
        fbox("FCFF = EBIT × (1−Tc) + Dep − CapEx − ΔNWC")
        fbox("     = NOPAT + Dep − CapEx − ΔNWC")
        ibox("""
        <h4 style='color:#FFD700;margin-top:0;'>WACC Method</h4>
        <p style='font-size:0.88rem;line-height:1.9;'>
        Discounts FCFF at the <b>Weighted Average Cost of Capital</b>, which blends
        the after-tax cost of debt and cost of equity weighted by their market value proportions.
        The tax shield is <i>embedded</i> in the lower discount rate via k_d(1−Tc).
        </p>""")
        fbox("WACC = (E/V)×k_e + (D/V)×k_d×(1−Tc)")
        fbox("k_e  = Rf + β_L × ERP   (CAPM)")
        fbox("β_L  = β_U × [1 + (1−Tc) × D/E]   (Hamada)")
        fbox("EV   = Σ FCFF_t/(1+WACC)^t + TV/(1+WACC)^N")

    with c2:
        ibox("""
        <h4 style='color:#FFD700;margin-top:0;'>APV Method</h4>
        <p style='font-size:0.88rem;line-height:1.9;'>
        Separates the <b>unlevered firm value</b> from the <b>tax shield value</b>.
        Preferred when debt is fixed (known quantum) rather than proportional to firm value.
        </p>""")
        fbox("V_L = V_U + PV(Tax Shield)")
        fbox("V_U = Σ FCFF_t/(1+r₀)^t + TV_U/(1+r₀)^N")
        fbox("r₀  = Rf + β_U × ERP   (unlevered cost)")
        fbox("PV(TS) = Tc × D              [perpetual debt]")
        fbox("PV(TS) = TS × [1−(1+k_d)^−N]/k_d  [finite debt]")

        ibox("""
        <h4 style='color:#FFD700;margin-top:0;'>When to Use Each Method</h4>
        <table style='width:100%;font-size:0.83rem;border-collapse:collapse;'>
        <tr style='border-bottom:1px solid rgba(255,215,0,0.3);'>
          <th style='color:#FFD700;padding:5px;text-align:left;'>Criterion</th>
          <th style='color:#FFD700;padding:5px;'>WACC</th>
          <th style='color:#FFD700;padding:5px;'>APV</th>
        </tr>
        <tr style='border-bottom:1px solid rgba(255,255,255,0.07);'>
          <td style='padding:4px;color:#ADD8E6;'>Debt policy</td>
          <td style='padding:4px;'>Proportional (D/V stable)</td>
          <td style='padding:4px;'>Fixed amount known</td>
        </tr>
        <tr style='border-bottom:1px solid rgba(255,255,255,0.07);'>
          <td style='padding:4px;color:#ADD8E6;'>Tax shield visibility</td>
          <td style='padding:4px;'>Implicit</td>
          <td style='padding:4px;'>Explicit, transparent</td>
        </tr>
        <tr>
          <td style='padding:4px;color:#ADD8E6;'>Best for</td>
          <td style='padding:4px;'>Steady-state firms</td>
          <td style='padding:4px;'>LBO, project finance</td>
        </tr>
        </table>""")

    st.markdown("---")
    st.html(f"""
    <div style="background:linear-gradient(135deg,{DB},{MB});border:2px solid {GD};
                border-radius:8px;padding:1rem 1.5rem;text-align:center;user-select:none;">
      <p style="color:{GD};-webkit-text-fill-color:{GD};font-family:'Playfair Display',serif;
                font-weight:700;font-size:1rem;margin:0;">
        🏔️ The Mountain Path — World of Finance
      </p>
      <p style="color:{TP};-webkit-text-fill-color:{TP};font-size:0.85rem;margin:0.3rem 0 0;">
        Prof. V. Ravichandran  ·  28+ Years Corporate Finance &amp; Banking
      </p>
      <p style="color:{TS};-webkit-text-fill-color:{TS};font-size:0.78rem;margin:0.2rem 0 0;">
        NMIMS Bangalore  ·  BITS Pilani  ·  RV University Bangalore  ·  Goa Institute of Management
      </p>
    </div>""")

footer()
