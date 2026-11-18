"""
Customer Segmentation Dashboard (RFM Analysis)
Run locally:  streamlit run app.py
Data:         rfm_customers.csv (saved by rfm_analysis.ipynb, Step 9)
"""
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =====================================================================
# BRANDING: change these to rebrand the whole dashboard
# =====================================================================
BRAND_NAME = "Maple & Thread Gifts"          # fictional demo brand
TAGLINE = "Customer Insights · RFM Segmentation"
PRIMARY = "#4338CA"      # indigo: headers, main bars
ACCENT = "#FB7185"       # coral: highlights
GOLD = "#818CF8"         # periwinkle: secondary accent
DARK = "#1E1B4B"         # deep indigo: sidebar, header, text
LIGHT = "#F5F5FF"        # page tint
LOGO_FILE = "logo.png"   # optional: put your own logo.png next to app.py to replace the drawn logo

# Original logo (a gift box with a ribbon), drawn in SVG so no image file is needed
LOGO_SVG = f"""
<svg width="54" height="54" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="60" height="60" rx="14" fill="{PRIMARY}"/>
  <rect x="14" y="27" width="36" height="25" rx="3" fill="#ffffff"/>
  <rect x="11" y="20" width="42" height="9" rx="3" fill="{GOLD}"/>
  <rect x="29" y="20" width="6" height="32" fill="{ACCENT}"/>
  <path d="M32 20 C24 8, 14 14, 22 20 Z" fill="{ACCENT}"/>
  <path d="M32 20 C40 8, 50 14, 42 20 Z" fill="{ACCENT}"/>
</svg>
"""

SEGMENT_ORDER = [
    "Champions", "Loyal Customers", "Potential Loyalists", "New Customers", "Promising",
    "Need Attention", "About to Sleep", "Can't Lose Them", "At Risk", "Hibernating",
]
SEGMENT_COLORS = {
    "Champions": "#312E81", "Loyal Customers": "#4338CA", "Potential Loyalists": "#6366F1",
    "New Customers": "#818CF8", "Promising": "#A5B4FC", "Need Attention": "#FDBA74",
    "About to Sleep": "#FED7AA", "Can't Lose Them": "#E11D48", "At Risk": "#FB7185",
    "Hibernating": "#A1A1AA",
}
ACTIONS = {
    "Champions": "Reward them: VIP program, early access to new products, ask for reviews and referrals",
    "Loyal Customers": "Upsell higher-value products, loyalty points, personalised recommendations",
    "Potential Loyalists": "Offer a membership or loyalty program, recommend related products",
    "New Customers": "Welcome email series, onboarding tips, small discount on the 2nd order",
    "Promising": "Build awareness: free shipping offer, highlight best-sellers",
    "Need Attention": "Limited-time offers based on past purchases",
    "About to Sleep": "Re-engage with popular products and a 'we miss you' discount",
    "Can't Lose Them": "High-priority win-back: personal outreach, exclusive offers, find out why they left",
    "At Risk": "Personalised win-back emails, special discounts, ask for feedback",
    "Hibernating": "Low-cost re-activation campaign; remove from regular mailing if no response",
}

st.set_page_config(page_title=f"{BRAND_NAME} | Customer Insights", page_icon="🎁", layout="wide")

# =====================================================================
# STYLE: brand colours applied with CSS
# =====================================================================
st.markdown(f"""
<style>
  .stApp {{ background: {LIGHT}; }}
  section[data-testid="stSidebar"] {{ background: {DARK}; }}
  section[data-testid="stSidebar"] * {{ color: #E0E7FF !important; }}
  section[data-testid="stSidebar"] span[data-baseweb="tag"] {{ background: {ACCENT} !important; }}
  .brand-bar {{
      display:flex; align-items:center; gap:16px; padding:18px 24px; border-radius:16px;
      background: linear-gradient(120deg, {DARK} 0%, {PRIMARY} 60%, {ACCENT} 120%);
      color:#fff; margin-bottom:18px; box-shadow: 0 6px 18px rgba(30,27,75,.22);
  }}
  .brand-bar h1 {{ color:#fff; font-size:1.9rem; margin:0; padding:0; line-height:1.15; }}
  .brand-bar p  {{ color:#C7D2FE; margin:2px 0 0 0; font-size:.95rem; }}
  .kpi {{
      background:#fff; border-radius:14px; padding:14px 16px; border-top:5px solid {PRIMARY};
      box-shadow: 0 2px 10px rgba(67,56,202,.12); height:100%;
  }}
  .kpi .label {{ color:#6B6B8A; font-size:.78rem; text-transform:uppercase; letter-spacing:.05em; }}
  .kpi .value {{ color:{DARK}; font-size:1.65rem; font-weight:700; margin-top:2px; }}
  .kpi .note  {{ color:{ACCENT}; font-size:.8rem; }}
  .action-card {{
      background:#fff; border-left:6px solid var(--c); border-radius:12px; padding:12px 16px;
      margin-bottom:10px; box-shadow: 0 1px 6px rgba(30,27,75,.08);
  }}
  .action-card b {{ color:{DARK}; }}
  .stTabs [data-baseweb="tab"] {{ font-weight:600; }}
  .stTabs [aria-selected="true"] {{ color:{PRIMARY} !important; }}
  .stTabs [data-baseweb="tab-highlight"] {{ background:{ACCENT} !important; }}
  div[data-testid="stMetricValue"] {{ color:{PRIMARY}; }}
</style>
""", unsafe_allow_html=True)


def kpi(col, label, value, note=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div>'
                 f'<div class="value">{value}</div><div class="note">{note}</div></div>',
                 unsafe_allow_html=True)


def brand_layout(fig, title=None):
    fig.update_layout(
        title=dict(text=title, font=dict(color=DARK, size=16)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        font=dict(color=DARK), legend_title_text="", margin=dict(t=60, l=10, r=10, b=10),
    )
    return fig


# =====================================================================
# DATA
# =====================================================================
@st.cache_data
def load_data(path: str = "rfm_customers.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"Customer ID": str, "RFM_Score": str})
    order = [s for s in SEGMENT_ORDER if s in df["Segment"].unique()]
    df["Segment"] = pd.Categorical(df["Segment"], categories=order, ordered=True)
    df["Avg_Order_Value"] = df["Monetary"] / df["Frequency"]
    return df


try:
    rfm = load_data()
except FileNotFoundError:
    st.error("`rfm_customers.csv` not found. Put it in the same folder as `app.py`. "
             "It is saved by Step 9 of `rfm_analysis.ipynb`.")
    st.stop()

ALL_SEGMENTS = list(rfm["Segment"].cat.categories)

# =====================================================================
# SIDEBAR
# =====================================================================
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, width=140)
else:
    st.sidebar.markdown(LOGO_SVG, unsafe_allow_html=True)
st.sidebar.markdown(f"### {BRAND_NAME}")
st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")
segments = st.sidebar.multiselect("Segment", ALL_SEGMENTS, default=ALL_SEGMENTS)
r_range = st.sidebar.slider("Recency score (5 = most recent)", 1, 5, (1, 5))
f_range = st.sidebar.slider("Frequency score (5 = most frequent)", 1, 5, (1, 5))
m_range = st.sidebar.slider("Monetary score (5 = highest spend)", 1, 5, (1, 5))
st.sidebar.markdown("---")
st.sidebar.caption("Data: Online Retail II (UCI), Dec 2009 – Dec 2011. Amounts in £. "
                   f"{BRAND_NAME} is a fictional brand used for this demo.")

df = rfm[
    rfm["Segment"].isin(segments)
    & rfm["R_Score"].between(*r_range)
    & rfm["F_Score"].between(*f_range)
    & rfm["M_Score"].between(*m_range)
]

# =====================================================================
# HEADER + KPIs
# =====================================================================
st.markdown(f'<div class="brand-bar">{LOGO_SVG}<div><h1>{BRAND_NAME}</h1>'
            f'<p>{TAGLINE} · {len(rfm):,} customers</p></div></div>', unsafe_allow_html=True)

if df.empty:
    st.warning("No customers match these filters. Widen the filters on the left.")
    st.stop()

total_rev = rfm["Monetary"].sum()
k1, k2, k3, k4, k5 = st.columns(5)
kpi(k1, "Customers", f"{len(df):,}", f"{len(df) / len(rfm):.0%} of all customers")
kpi(k2, "Revenue", f"£{df['Monetary'].sum() / 1e6:,.2f}M", f"{df['Monetary'].sum() / total_rev:.0%} of total revenue")
kpi(k3, "Avg spend / customer", f"£{df['Monetary'].mean():,.0f}", f"all customers: £{rfm['Monetary'].mean():,.0f}")
kpi(k4, "Avg orders / customer", f"{df['Frequency'].mean():.1f}", f"all customers: {rfm['Frequency'].mean():.1f}")
kpi(k5, "Days since last order", f"{df['Recency'].mean():.0f}", f"all customers: {rfm['Recency'].mean():.0f}")
st.write("")

seg = (
    df.groupby("Segment", observed=True)
    .agg(Customers=("Recency", "size"), Revenue=("Monetary", "sum"),
         Avg_Recency=("Recency", "mean"), Avg_Frequency=("Frequency", "mean"),
         Avg_Monetary=("Monetary", "mean"))
    .reset_index()
)
seg["% Customers"] = seg["Customers"] / seg["Customers"].sum() * 100
seg["% Revenue"] = seg["Revenue"] / seg["Revenue"].sum() * 100
seg = seg.sort_values("Revenue", ascending=False)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview", "🔍 Segment explorer", "🧩 RFM patterns", "🎯 Campaign planner", "👤 Customer lookup"])

# =====================================================================
# TAB 1: OVERVIEW (click a bar to explore that segment)
# =====================================================================
with tab1:
    c1, c2 = st.columns([3, 2])
    with c1:
        long = seg.melt(id_vars="Segment", value_vars=["% Customers", "% Revenue"],
                        var_name="Measure", value_name="Percent")
        fig = px.bar(long, x="Segment", y="Percent", color="Measure", barmode="group",
                     color_discrete_map={"% Customers": "#C7D2FE", "% Revenue": PRIMARY},
                     text_auto=".0f")
        fig.update_layout(xaxis_title="", yaxis_title="%")
        event = st.plotly_chart(brand_layout(fig, "Share of customers vs share of revenue"),
                                width="stretch", on_select="rerun", selection_mode="points",
                                key="seg_bar")
        points = event.selection.points if event and event.selection else []
        if points:
            st.session_state["explore_segment"] = points[0]["x"]
            st.success(f"**{points[0]['x']}** selected. Open the **🔍 Segment explorer** tab.")
        else:
            st.caption("Tip: click a bar to open that segment in the Segment explorer tab.")
    with c2:
        fig = px.pie(seg, names="Segment", values="Revenue", hole=0.55, color="Segment",
                     color_discrete_map=SEGMENT_COLORS)
        fig.update_traces(textposition="inside", textinfo="percent")
        fig.add_annotation(text=f"£{seg['Revenue'].sum() / 1e6:.1f}M", showarrow=False,
                           font=dict(size=22, color=PRIMARY))
        st.plotly_chart(brand_layout(fig, "Revenue by segment"), width="stretch")

    st.subheader("Segment summary")
    st.dataframe(
        seg.rename(columns={"Avg_Recency": "Avg Recency (days)", "Avg_Frequency": "Avg Orders",
                            "Avg_Monetary": "Avg Spend (£)", "Revenue": "Revenue (£)"}),
        hide_index=True, width="stretch",
        column_config={
            "Revenue (£)": st.column_config.ProgressColumn(
                format="£%.0f", min_value=0, max_value=float(seg["Revenue"].max())),
            "Avg Spend (£)": st.column_config.NumberColumn(format="£%.0f"),
            "Avg Recency (days)": st.column_config.NumberColumn(format="%.0f"),
            "Avg Orders": st.column_config.NumberColumn(format="%.1f"),
            "% Customers": st.column_config.NumberColumn(format="%.1f%%"),
            "% Revenue": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

# =====================================================================
# TAB 2: SEGMENT EXPLORER
# =====================================================================
with tab2:
    available = list(seg["Segment"])
    if st.session_state.get("explore_segment") not in available:
        st.session_state["explore_segment"] = available[0]
    choice = st.selectbox("Choose a segment", available, key="explore_segment")
    s = df[df["Segment"] == choice]
    color = SEGMENT_COLORS.get(choice, PRIMARY)

    st.markdown(f'<div class="action-card" style="--c:{color}"><b>{choice}</b>: '
                f'{len(s):,} customers · £{s["Monetary"].sum():,.0f} revenue<br>'
                f'<b>Recommended action:</b> {ACTIONS.get(choice, "")}</div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("Avg days since last order", f"{s['Recency'].mean():.0f}",
             f"{s['Recency'].mean() - rfm['Recency'].mean():+.0f} vs all", delta_color="inverse")
    b.metric("Avg orders", f"{s['Frequency'].mean():.1f}",
             f"{s['Frequency'].mean() - rfm['Frequency'].mean():+.1f} vs all")
    c.metric("Avg spend", f"£{s['Monetary'].mean():,.0f}",
             f"£{s['Monetary'].mean() - rfm['Monetary'].mean():+,.0f} vs all")
    d.metric("Avg order value", f"£{s['Avg_Order_Value'].mean():,.0f}",
             f"£{s['Avg_Order_Value'].mean() - rfm['Avg_Order_Value'].mean():+,.0f} vs all")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(s, x="Recency", nbins=30, color_discrete_sequence=[color])
        fig.update_layout(xaxis_title="Days since last order", yaxis_title="Customers", bargap=0.08)
        st.plotly_chart(brand_layout(fig, "When did they last buy?"), width="stretch")
    with c2:
        prof = pd.DataFrame({
            "Score": ["Recency", "Frequency", "Monetary"],
            choice: [s["R_Score"].mean(), s["F_Score"].mean(), s["M_Score"].mean()],
            "All customers": [rfm["R_Score"].mean(), rfm["F_Score"].mean(), rfm["M_Score"].mean()],
        })
        fig = go.Figure()
        for name, col in [("All customers", "#C7D2FE"), (choice, color)]:
            fig.add_trace(go.Scatterpolar(r=list(prof[name]) + [prof[name].iloc[0]],
                                          theta=list(prof["Score"]) + ["Recency"],
                                          fill="toself", name=name, line_color=col))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5], visible=True)))
        st.plotly_chart(brand_layout(fig, "Average R, F, M score vs all customers"), width="stretch")

    st.markdown(f"**Top 10 customers in {choice}** (by spend)")
    st.dataframe(s.nlargest(10, "Monetary")[["Customer ID", "Recency", "Frequency", "Monetary", "RFM_Score"]],
                 hide_index=True, width="stretch",
                 column_config={"Monetary": st.column_config.NumberColumn("Total spend", format="£%.0f")})

# =====================================================================
# TAB 3: RFM PATTERNS
# =====================================================================
with tab3:
    metric = st.radio("Heatmap shows", ["Average spend (£)", "Number of customers"], horizontal=True)
    if metric.startswith("Average"):
        heat = df.pivot_table(index="R_Score", columns="F_Score", values="Monetary", aggfunc="mean")
        fmt, scale = ".0f", [[0, "#FFFFFF"], [0.5, GOLD], [1, DARK]]
    else:
        heat = df.pivot_table(index="R_Score", columns="F_Score", values="Monetary", aggfunc="size")
        fmt, scale = "d", [[0, "#FFFFFF"], [0.5, "#FDA4AF"], [1, "#E11D48"]]
    fig = px.imshow(heat.sort_index(ascending=False), text_auto=fmt, color_continuous_scale=scale,
                    aspect="auto", labels=dict(x="Frequency score (5 = most frequent)",
                                               y="Recency score (5 = most recent)", color=""))
    fig.update_xaxes(type="category")
    fig.update_yaxes(type="category")
    st.plotly_chart(brand_layout(fig, f"{metric} by Recency and Frequency score"), width="stretch")

    fig = px.scatter(df, x="Recency", y="Frequency", size="Monetary", color="Segment",
                     color_discrete_map=SEGMENT_COLORS, log_y=True, size_max=40, opacity=0.65,
                     hover_data={"Customer ID": True, "Monetary": ":,.0f"})
    fig.update_layout(xaxis_title="Days since last order", yaxis_title="Number of orders (log scale)")
    st.plotly_chart(brand_layout(fig, "Every customer: recency vs frequency (bubble size = spend)"),
                    width="stretch")

# =====================================================================
# TAB 4: CAMPAIGN PLANNER (what-if)
# =====================================================================
with tab4:
    st.markdown("Estimate what a marketing campaign could earn. "
                "**These are planning assumptions, not predictions.** Adjust them to test scenarios.")
    default_targets = [x for x in ["Can't Lose Them", "At Risk"] if x in ALL_SEGMENTS]
    targets = st.multiselect("Target segments", ALL_SEGMENTS, default=default_targets)
    c1, c2, c3 = st.columns(3)
    response = c1.slider("Response rate (%)", 1, 50, 10)
    orders_each = c2.slider("Orders per responding customer", 1, 5, 1)
    cost_each = c3.number_input("Campaign cost per customer contacted (£)", 0.0, 100.0, 2.0, 0.5)

    t = rfm[rfm["Segment"].isin(targets)]
    if t.empty:
        st.info("Choose at least one target segment.")
    else:
        by_seg = (t.groupby("Segment", observed=True)
                   .agg(Customers=("Recency", "size"), AOV=("Avg_Order_Value", "mean"))
                   .reset_index())
        by_seg["Expected revenue"] = by_seg["Customers"] * response / 100 * orders_each * by_seg["AOV"]
        responders = len(t) * response / 100
        revenue = by_seg["Expected revenue"].sum()
        cost = len(t) * cost_each
        roi = (revenue - cost) / cost if cost else float("inf")

        a, b, c, d = st.columns(4)
        kpi(a, "Customers contacted", f"{len(t):,}")
        kpi(b, "Expected responders", f"{responders:,.0f}", f"{response}% response")
        kpi(c, "Expected revenue", f"£{revenue:,.0f}", f"{orders_each} order(s) per responder")
        kpi(d, "Campaign cost / ROI", f"£{cost:,.0f}", "ROI: n/a" if cost == 0 else f"ROI: {roi:,.1f}x")
        st.write("")

        fig = px.bar(by_seg, x="Segment", y="Expected revenue", color="Segment",
                     color_discrete_map=SEGMENT_COLORS, text_auto=",.0f")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="£")
        st.plotly_chart(brand_layout(fig, "Expected revenue by target segment"), width="stretch")
        st.caption("Expected revenue = customers × response rate × orders per responder × "
                   "the segment's historical average order value.")

    st.subheader("Recommended action for each segment")
    for _, row in seg.iterrows():
        name = row["Segment"]
        st.markdown(f'<div class="action-card" style="--c:{SEGMENT_COLORS.get(name, PRIMARY)}">'
                    f'<b>{name}</b> · {row["Customers"]:,} customers · £{row["Revenue"]:,.0f}<br>'
                    f'{ACTIONS.get(name, "")}</div>', unsafe_allow_html=True)

# =====================================================================
# TAB 5: CUSTOMER LOOKUP + DOWNLOAD
# =====================================================================
with tab5:
    cid = st.text_input("Search a Customer ID (e.g. 12347)")
    if cid:
        hit = rfm[rfm["Customer ID"] == cid.strip()]
        if hit.empty:
            st.info("Customer not found.")
        else:
            r = hit.iloc[0]
            a, b, c, d = st.columns(4)
            kpi(a, "Segment", r["Segment"])
            kpi(b, "RFM score", r["RFM_Score"])
            kpi(c, "Total spend", f"£{r['Monetary']:,.0f}", f"{int(r['Frequency'])} orders")
            kpi(d, "Days since last order", int(r["Recency"]))
            st.markdown(f'<div class="action-card" style="--c:{SEGMENT_COLORS.get(r["Segment"], PRIMARY)}">'
                        f'<b>Suggested action:</b> {ACTIONS.get(r["Segment"], "")}</div>',
                        unsafe_allow_html=True)

    st.subheader("Customers matching the filters")
    st.dataframe(df.drop(columns="Avg_Order_Value").sort_values("Monetary", ascending=False),
                 hide_index=True, width="stretch",
                 column_config={"Monetary": st.column_config.NumberColumn(format="£%.2f")})
    st.download_button("⬇ Download as CSV", df.drop(columns="Avg_Order_Value").to_csv(index=False).encode("utf-8"),
                       file_name="rfm_filtered_customers.csv", mime="text/csv")
