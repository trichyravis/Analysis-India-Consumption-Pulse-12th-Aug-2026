from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"

st.set_page_config(page_title="India Consumption Pulse", page_icon="◉", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: #F6F2EA; }
      .block-container { max-width: 1280px; padding-top: 4.75rem; }
      [data-testid="stSidebar"] { background: #18332F; }
      [data-testid="stSidebar"] * { color: #F6F2EA !important; }
      section[data-testid="stSidebar"] [data-testid="stDateInput"] input,
      section[data-testid="stSidebar"] [data-testid="stDateInput"] input::selection {
        color:#18332F !important;
        -webkit-text-fill-color:#18332F !important;
        caret-color:#18332F !important;
        font-weight:650 !important;
        opacity:1 !important;
      }
      section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"] {
        background:#FFFDF8 !important;
      }
      .eyebrow { letter-spacing:.14em; text-transform:uppercase; color:#C8583E; font-size:.72rem; font-weight:700; }
      .academy-banner { display:flex; align-items:center; gap:.9rem; background:linear-gradient(110deg,#18332F,#28534C); color:#FFFDF8; padding:.9rem 1.15rem; border-radius:15px; margin:0 0 1.35rem; border-bottom:4px solid #EF6A4C; box-shadow:0 8px 24px rgba(24,51,47,.12); }
      .academy-mark { color:#F5B39F; font-size:1.55rem; line-height:1; }
      .academy-name { color:#FFFDF8; font-size:1.08rem; font-weight:780; letter-spacing:.01em; }
      .academy-tagline { color:#CBD8D2; font-size:.8rem; margin-top:.12rem; }
      .hero { font-size:3rem; line-height:1.02; letter-spacing:-.045em; color:#18332F; font-weight:750; margin:.35rem 0 .6rem; }
      .subhero { color:#53645E; max-width:780px; font-size:1.04rem; margin-bottom:1.2rem; }
      .pill { display:inline-block; padding:.28rem .65rem; border:1px solid #B7B0A4; border-radius:999px; color:#53645E; font-size:.78rem; margin:.1rem .25rem .1rem 0; }
      div[data-testid="stMetric"] { background:#FFFDF8; border:1px solid #DDD5C8; border-radius:14px; padding:15px 16px; box-shadow:0 6px 20px rgba(24,51,47,.04); }
      div[data-testid="stMetric"] label { color:#69756F; }
      .section-title { color:#18332F; font-size:1.5rem; font-weight:700; letter-spacing:-.025em; margin-top:1rem; }
      .callout { background:#E8EFEA; border-left:4px solid #2D756C; padding:1rem 1.1rem; border-radius:0 10px 10px 0; color:#26443F; }
      .warn { background:#F7E7D7; border-left-color:#EF6A4C; }
      .profile-card { margin-top:.65rem; padding:1rem; border:1px solid rgba(246,242,234,.22); border-radius:14px; background:rgba(255,255,255,.07); }
      .profile-name { color:#F5B39F!important; font-size:1rem; font-weight:750; margin-bottom:.25rem; }
      .profile-role { color:#E7E1D7!important; font-size:.78rem; line-height:1.5; }
      .profile-links { margin-top:.7rem; line-height:1.7; }
      .profile-links a { color:#F5B39F!important; font-size:.78rem; font-weight:700; text-decoration:none; }
      .profile-links a:hover { text-decoration:underline; }
      .profile-footer { background:#18332F; color:#EDE7DC; padding:1.35rem 1.5rem; border-radius:16px; margin-top:2.5rem; text-align:center; border-top:4px solid #EF6A4C; line-height:1.55; }
      .profile-footer strong { color:#FFFDF8; }
      .profile-footer a { color:#F5B39F!important; font-weight:700; text-decoration:none; }
      .profile-footer small { color:#BFC9C4; }
      .insight-card { background:#FFFDF8; border:1px solid #DDD5C8; border-radius:14px; padding:1.05rem 1.15rem; min-height:175px; box-shadow:0 6px 20px rgba(24,51,47,.04); }
      .insight-card h4 { color:#18332F; margin:0 0 .55rem; font-size:1.02rem; }
      .insight-card ul { color:#53645E; padding-left:1.15rem; margin-bottom:0; }
      .insight-card li { margin-bottom:.42rem; }
      .signal-label { color:#C8583E; font-weight:750; text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; }
      footer { visibility:hidden; }
      @media(max-width:700px) { .block-container { padding-top:4.25rem; } .hero { font-size:2.15rem; } .academy-banner { align-items:flex-start; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    parse = lambda name: pd.read_csv(DATA / name, parse_dates=["date"])
    return {
        "inflation": parse("inflation.csv"),
        "confidence": parse("confidence.csv"),
        "gst": parse("gst.csv"),
        "vehicles": parse("passenger_vehicles.csv"),
        "rates": parse("policy_rates.csv"),
        "catalog": pd.read_csv(DATA / "source_catalog.csv", parse_dates=["latest_period"]),
    }


d = load_data()
COLORS = {"Inflation": "#EF6A4C", "Confidence": "#2D756C", "GST": "#C49A45", "Vehicles": "#657B9A", "Repo rate": "#7B61A8"}


def mom_delta(frame, column):
    s = frame[column].dropna()
    return s.iloc[-1] - s.iloc[-2]


def line_chart(frame, x, y, color="#2D756C", height=310, domain=None, rule=None):
    base = alt.Chart(frame).encode(
        x=alt.X(f"{x}:T", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0, tickCount=8)),
        tooltip=[alt.Tooltip(f"{x}:T", title="Period", format="%B %Y"), alt.Tooltip(f"{y}:Q", format=",.2f")],
    )
    scale = alt.Scale(domain=domain) if domain else alt.Scale(zero=False)
    chart = base.mark_area(line={"color": color, "strokeWidth": 2.5}, color=alt.Gradient(
        gradient="linear", stops=[alt.GradientStop(color=color, offset=0), alt.GradientStop(color="#F6F2EA", offset=1)], x1=1, x2=1, y1=0, y2=1
    ), opacity=.32).encode(y=alt.Y(f"{y}:Q", title=None, scale=scale))
    if rule is not None:
        chart += alt.Chart(pd.DataFrame({"y": [rule]})).mark_rule(color="#9A8E80", strokeDash=[5, 5]).encode(y="y:Q")
    return chart.properties(height=height).configure_view(strokeWidth=0).configure_axis(gridColor="#DED8CE", labelColor="#53645E")


with st.sidebar:
    st.markdown("### India Consumption Pulse")
    st.caption("A compact macro demand monitor")
    page = st.radio("Navigate", ["About & insights", "Concepts & checks", "Pulse", "Deep dive", "Relationships", "Data desk"], label_visibility="collapsed")
    st.markdown("---")
    start = st.date_input("Start period", pd.Timestamp("2024-07-01"), min_value=pd.Timestamp("2024-01-01"), max_value=pd.Timestamp("2026-07-31"))
    show_notes = st.toggle("Show methodology notes", value=True)
    st.markdown("---")
    st.caption("Snapshot prepared 12 Aug 2026 · Official release dates differ by series.")
    st.markdown(
        """
        <div class="profile-card">
          <div class="profile-name">Prof. V. Ravichandran</div>
          <div class="profile-role">Faculty · Finance, Risk &amp; Quantitative Analytics<br>28+ years in corporate finance and banking · 10+ years in academia</div>
          <div class="profile-links">
            <a href="https://www.linkedin.com/in/trichyravis" target="_blank">LinkedIn ↗</a> &nbsp;·&nbsp;
            <a href="https://github.com/trichyravis" target="_blank">GitHub ↗</a><br>
            <a href="https://themountainpathacademy.com/about.html" target="_blank">Full faculty profile ↗</a><br>
            <a href="https://themountainpathacademy.com/courses" target="_blank">Mountain Path Academy courses ↗</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

start_ts = pd.Timestamp(start)
infl = d["inflation"].query("date >= @start_ts")
conf = d["confidence"].query("date >= @start_ts")
gst = d["gst"].query("date >= @start_ts")
veh = d["vehicles"].query("date >= @start_ts")
rates = d["rates"].query("date >= @start_ts")

st.markdown(
    """<div class="academy-banner"><div class="academy-mark">▲</div><div><div class="academy-name">The Mountain Path Academy</div><div class="academy-tagline">Finance · Risk Management · Quantitative Analytics</div></div></div>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="eyebrow">India · household demand monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Consumption, beneath the headline.</div>', unsafe_allow_html=True)
st.markdown('<div class="subhero">Five signals—prices, sentiment, tax receipts, automobile demand and monetary policy—read together, with their publication gaps kept visible.</div>', unsafe_allow_html=True)
st.markdown('<span class="pill">Official-source snapshot</span><span class="pill">Monthly + bi-monthly</span><span class="pill">Latest available ≠ July 2026</span>', unsafe_allow_html=True)

if page == "Concepts & checks":
    st.markdown('<div class="section-title">Concepts & knowledge checks</div>', unsafe_allow_html=True)
    st.write("A short learning studio for understanding the indicators before interpreting their movements.")

    concept_tab, reading_tab, check_tab = st.tabs(["Core concepts", "Reading signals", "Knowledge checks"])
    with concept_tab:
        st.markdown("#### The five building blocks")
        cards = [
            ("CPI inflation", "The percentage change in the consumer-price index from a year earlier. Falling inflation means prices are rising more slowly—not necessarily falling."),
            ("Consumer confidence", "CSI describes how urban households view current conditions; FEI captures expectations one year ahead. A value of 100 is neutral."),
            ("GST collections", "A nominal, high-frequency signal of formal taxable activity. Inflation, imports, compliance and calendar effects also influence it."),
            ("Passenger vehicles", "A financing-sensitive discretionary-demand indicator. SIAM reports wholesale dispatches, which can differ from retail registrations."),
            ("RBI policy rates", "Repo influences borrowing conditions. SDF absorbs banks' surplus liquidity and forms the operative floor; fixed reverse repo remains published but is not the current floor."),
        ]
        for row in range(0, len(cards), 2):
            cols = st.columns(2)
            for col, (title, body) in zip(cols, cards[row:row+2]):
                col.markdown(f'<div class="insight-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

        st.markdown("#### RBI policy-rate corridor")
        corridor = pd.DataFrame({
            "Facility": ["Fixed reverse repo", "SDF · operative floor", "Policy repo", "MSF · upper bound"],
            "Rate": [3.35, 5.00, 5.25, 5.50],
            "Role": ["Legacy published rate", "RBI absorbs bank liquidity", "RBI lends under policy framework", "Emergency overnight borrowing"],
        })
        corridor_chart = alt.Chart(corridor).mark_bar(cornerRadiusEnd=7).encode(
            x=alt.X("Rate:Q", title="Rate, %", scale=alt.Scale(domain=[3, 5.75])),
            y=alt.Y("Facility:N", title=None, sort=["MSF · upper bound", "Policy repo", "SDF · operative floor", "Fixed reverse repo"]),
            color=alt.Color("Facility:N", scale=alt.Scale(range=["#EF6A4C", "#2D756C", "#7B61A8", "#C49A45"]), legend=None),
            tooltip=["Facility:N", alt.Tooltip("Rate:Q", format=".2f"), "Role:N"],
        ).properties(height=250)
        labels_chart = alt.Chart(corridor).mark_text(align="left", dx=5, color="#18332F", fontWeight="bold").encode(
            x="Rate:Q", y=alt.Y("Facility:N", sort=["MSF · upper bound", "Policy repo", "SDF · operative floor", "Fixed reverse repo"]), text=alt.Text("Rate:Q", format=".2f")
        )
        st.altair_chart((corridor_chart + labels_chart).configure_view(strokeWidth=0), use_container_width=True)
        st.caption("Illustrative corridor using July 2026 rates. SDF is the relevant floor; the fixed reverse repo is shown to prevent the two concepts being confused.")

    with reading_tab:
        st.markdown("#### From observation to inference")
        st.markdown(
            """
            1. **Check the definition.** Confirm whether the series measures a rate, index, rupee value or number of units.
            2. **Check freshness.** Do not assume that all indicators refer to the same month.
            3. **Compare like with like.** Use year-on-year changes for seasonal series or index each series when comparing direction.
            4. **Look for confirmation.** A demand conclusion is stronger when confidence, GST and discretionary sales point in a similar direction.
            5. **Consider transmission lags.** Repo-rate changes can take months to affect deposit rates, loan pricing and purchases.
            6. **Separate association from causation.** Correlation alone cannot establish that one indicator caused another to move.
            """
        )
        st.markdown('<div class="callout"><b>Example:</b> Lower repo rates plus stronger vehicle sales are consistent with improving credit-sensitive demand. They do not prove the rate cut caused the sales increase; income, launches, discounts and festival timing may also matter.</div>', unsafe_allow_html=True)
        st.markdown("#### Common interpretation traps")
        st.markdown(
            """
            - Lower inflation is not the same as lower prices; it usually means slower price increases.
            - Higher GST does not automatically mean higher real consumption because GST is measured in current rupees.
            - FEI above 100 does not mean current conditions are strong; CSI may still be below 100.
            - Wholesale vehicle dispatches can rise because dealers build inventory, even before consumers register those vehicles.
            - Fixed reverse repo should not be used as the current corridor floor; use SDF after April 2022.
            """
        )

    with check_tab:
        st.markdown("#### Test your understanding")
        q1 = st.radio("1. If CPI inflation falls from 6% to 4%, what does it usually mean?", ["Prices fell by 2%", "Prices rose more slowly", "All household costs fell"], index=None)
        if q1:
            st.success("Correct — inflation slowed, but the price level can still be rising.") if q1 == "Prices rose more slowly" else st.error("Not quite. A lower positive inflation rate means prices are generally still rising, but more slowly.")

        q2 = st.radio("2. Which rate is the effective floor of RBI's liquidity corridor?", ["Fixed reverse repo", "Standing Deposit Facility", "Policy repo"], index=None)
        if q2:
            st.success("Correct — SDF has been the operative floor since April 2022.") if q2 == "Standing Deposit Facility" else st.error("Review the corridor concept: SDF, not fixed reverse repo, is the operative floor.")

        q3 = st.radio("3. Can a positive correlation prove that repo-rate cuts increased vehicle sales?", ["Yes", "No"], index=None)
        if q3:
            st.success("Correct — correlation is descriptive and does not establish causality.") if q3 == "No" else st.error("No. Timing, income, financing transmission, seasonality and other factors must be examined.")

        q4 = st.radio("4. Which consumer-confidence reading signals optimism?", ["CSI or FEI above 100", "Any reading above zero", "Only a rising GST value"], index=None)
        if q4:
            st.success("Correct — 100 is the neutral point for CSI and FEI.") if q4 == "CSI or FEI above 100" else st.error("Consumer-confidence indices use 100 as the neutral threshold.")

elif page == "Pulse":
    latest_i, latest_c, latest_g, latest_v, latest_r = d["inflation"].iloc[-1], d["confidence"].iloc[-1], d["gst"].iloc[-1], d["vehicles"].iloc[-1], d["rates"].iloc[-1]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Headline inflation", f"{latest_i.cpi_inflation_yoy:.2f}%", f"{mom_delta(infl, 'cpi_inflation_yoy'):+.2f} pp", help="All-India Combined CPI, year on year")
    c2.metric("Urban confidence", f"{latest_c.csi:.1f}", f"{mom_delta(conf, 'csi'):+.1f} pts", help="CSI; below 100 denotes pessimism")
    c3.metric("Gross GST", f"₹{latest_g.gross_gst_crore/100000:.2f}L cr", f"{mom_delta(gst, 'gross_gst_crore')/1000:+.1f}k cr")
    c4.metric("Passenger vehicles", f"{latest_v.domestic_sales_units/100000:.2f}L", f"{mom_delta(veh, 'domestic_sales_units')/1000:+.1f}k", help="SIAM domestic wholesale dispatches")
    c5.metric("Policy repo rate", f"{latest_r.repo_rate:.2f}%", f"{latest_r.repo_rate-d['rates'].iloc[0].repo_rate:+.2f} pp since Jan 2024", help="RBI policy repo rate")

    st.markdown('<div class="section-title">Different clocks, one demand story</div>', unsafe_allow_html=True)
    st.caption("Each series rebased to 100 at its first available observation in the selected window. This compares direction, not units.")
    indexed = []
    specs = [(infl, "cpi_inflation_yoy", "Inflation"), (conf, "csi", "Confidence"), (gst, "gross_gst_crore", "GST"), (veh, "domestic_sales_units", "Vehicles"), (rates, "repo_rate", "Repo rate")]
    for frame, col, label in specs:
        temp = frame[["date", col]].dropna().copy()
        temp["value"] = temp[col] / temp[col].iloc[0] * 100
        temp["series"] = label
        indexed.append(temp[["date", "value", "series"]])
    index_df = pd.concat(indexed)
    chart = alt.Chart(index_df).mark_line(point=alt.OverlayMarkDef(size=35), strokeWidth=2.4).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)),
        y=alt.Y("value:Q", title="Index (first observation = 100)", scale=alt.Scale(zero=False)),
        color=alt.Color("series:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())), title=None),
        tooltip=[alt.Tooltip("date:T", format="%b %Y"), "series:N", alt.Tooltip("value:Q", format=".1f")],
    ).properties(height=390).configure_view(strokeWidth=0).configure_axis(gridColor="#DED8CE")
    st.altair_chart(chart, use_container_width=True)
    if show_notes:
        st.markdown('<div class="callout"><b>Read with care.</b> GST and vehicle sales are nominal/activity measures and are seasonal. Consumer confidence is bi-monthly. Indexed lines are descriptive; they do not establish causality.</div>', unsafe_allow_html=True)

elif page == "Deep dive":
    topic = st.radio("Indicator", ["Inflation", "Confidence", "GST", "Vehicles", "Policy rates"], horizontal=True)
    if topic == "Inflation":
        melted = infl.melt("date", ["cpi_inflation_yoy", "food_inflation_yoy"], var_name="series", value_name="percent")
        melted["series"] = melted.series.map({"cpi_inflation_yoy": "Headline CPI", "food_inflation_yoy": "Food CPI"})
        chart = alt.Chart(melted).mark_line(point=True, strokeWidth=2.5).encode(x=alt.X("date:T", title=None), y=alt.Y("percent:Q", title="Year-on-year, %"), color=alt.Color("series:N", scale=alt.Scale(range=["#EF6A4C", "#C49A45"]), title=None), tooltip=[alt.Tooltip("date:T", format="%b %Y"), "series", alt.Tooltip("percent", format=".2f")]).properties(height=420)
        st.altair_chart(chart, use_container_width=True)
        st.info("The 2%–6% band is the RBI tolerance range around its 4% CPI target. The official CPI basket/base changed in 2026.")
    elif topic == "Confidence":
        melted = conf.melt("date", ["csi", "fei"], var_name="series", value_name="index")
        melted["series"] = melted.series.map({"csi": "Current situation", "fei": "Future expectations"})
        chart = alt.Chart(melted).mark_line(point=True, strokeWidth=2.5).encode(x=alt.X("date:T", title=None), y=alt.Y("index:Q", title="Index", scale=alt.Scale(domain=[85, 130])), color=alt.Color("series:N", scale=alt.Scale(range=["#2D756C", "#C49A45"]), title=None), tooltip=[alt.Tooltip("date:T", format="%b %Y"), "series", alt.Tooltip("index", format=".1f")]).properties(height=420)
        st.altair_chart(chart + alt.Chart(pd.DataFrame({"y":[100]})).mark_rule(strokeDash=[6,4], color="#8C8176").encode(y="y:Q"), use_container_width=True)
        st.caption("Below 100 = pessimistic; above 100 = optimistic. CSI and FEI are based on five net-response components.")
    elif topic == "GST":
        st.altair_chart(line_chart(gst, "date", "gross_gst_crore", "#C49A45"), use_container_width=True)
        st.caption("Gross GST revenue, ₹ crore. The April spike is influenced by financial-year-end settlement and compliance seasonality.")
    elif topic == "Vehicles":
        st.altair_chart(line_chart(veh, "date", "domestic_sales_units", "#657B9A"), use_container_width=True)
        st.caption("Domestic wholesale dispatches. This is not VAHAN retail registration data; festive stocking can shift timing.")
    else:
        policy_long = rates.melt("date", ["repo_rate", "fixed_reverse_repo_rate", "sdf_rate"], var_name="series", value_name="percent")
        policy_long["series"] = policy_long.series.map({"repo_rate":"Policy repo", "fixed_reverse_repo_rate":"Fixed reverse repo", "sdf_rate":"Standing Deposit Facility"})
        policy_chart = alt.Chart(policy_long).mark_line(interpolate="step-after", point=True, strokeWidth=2.6).encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0)), y=alt.Y("percent:Q", title="Rate, %", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N", scale=alt.Scale(range=["#7B61A8", "#EF6A4C", "#2D756C"]), title=None),
            tooltip=[alt.Tooltip("date:T", format="%b %Y"), "series:N", alt.Tooltip("percent:Q", format=".2f")]
        ).properties(height=420)
        st.altair_chart(policy_chart, use_container_width=True)
        st.info("Since April 2022, the Standing Deposit Facility (SDF)—not the unchanged 3.35% fixed reverse repo—has been the effective floor of RBI's liquidity corridor.")

elif page == "Relationships":
    st.markdown('<div class="section-title">Aligned monthly signals</div>', unsafe_allow_html=True)
    st.caption("Bi-monthly confidence is forward-filled for one month only. Values are standardized before correlation.")
    merged = infl[["date", "cpi_inflation_yoy"]].merge(gst[["date", "gross_gst_crore"]], on="date", how="outer").merge(veh[["date", "domestic_sales_units"]], on="date", how="outer").merge(conf[["date", "csi"]], on="date", how="outer").merge(rates[["date", "repo_rate"]], on="date", how="outer").sort_values("date")
    merged["csi"] = merged.csi.ffill(limit=1)
    merged = merged.query("date >= @start_ts")
    labels = {"cpi_inflation_yoy":"Inflation", "csi":"Confidence", "gross_gst_crore":"GST", "domestic_sales_units":"Vehicles", "repo_rate":"Repo rate"}
    corr = merged[list(labels)].corr(min_periods=6).rename(index=labels, columns=labels).round(2)
    corr_long = corr.stack().rename("correlation").reset_index()
    heat = alt.Chart(corr_long).mark_rect(cornerRadius=4).encode(x=alt.X("level_1:N", title=None), y=alt.Y("level_0:N", title=None), color=alt.Color("correlation:Q", scale=alt.Scale(domain=[-1,0,1], range=["#C8583E", "#F4EEE5", "#2D756C"]), title="r"), tooltip=["level_0", "level_1", "correlation"]).properties(height=370)
    text_layer = alt.Chart(corr_long).mark_text(fontSize=15).encode(x="level_1:N", y="level_0:N", text=alt.Text("correlation:Q", format=".2f"), color=alt.condition("abs(datum.correlation) > 0.55", alt.value("white"), alt.value("#18332F")))
    st.altair_chart((heat + text_layer).configure_view(strokeWidth=0), use_container_width=True)
    st.markdown('<div class="callout warn"><b>Not a causal model.</b> The window is short, seasonal effects remain, and releases have different frequencies. Treat coefficients as prompts for investigation.</div>', unsafe_allow_html=True)

elif page == "Data desk":
    st.markdown('<div class="section-title">Availability before analysis</div>', unsafe_allow_html=True)
    catalog = d["catalog"].copy()
    catalog["latest_period"] = catalog.latest_period.dt.strftime("%b %Y")
    st.dataframe(catalog[["indicator", "owner", "frequency", "coverage", "latest_period", "availability"]], hide_index=True, use_container_width=True)
    st.markdown("#### Source notes")
    for row in d["catalog"].itertuples():
        with st.expander(f"{row.indicator} · {row.owner}"):
            st.write(row.definition)
            st.write(row.caveat)
            st.link_button("Open official source", row.source_url)
    st.markdown("#### Download clean snapshots")
    cols = st.columns(5)
    exports = [
        ("india_inflation.xlsx", "Inflation"),
        ("india_consumer_confidence.xlsx", "Confidence"),
        ("india_gst_collections.xlsx", "GST"),
        ("india_passenger_vehicle_sales.xlsx", "Vehicles"),
        ("india_policy_rates.xlsx", "Policy rates"),
    ]
    for col, (file_name, label) in zip(cols, exports):
        workbook_bytes = (DATA / "excel" / file_name).read_bytes()
        col.download_button(
            label,
            workbook_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    st.markdown('<div class="callout warn"><b>Different freshness dates.</b> RBI policy rates are available through July 2026, while CPI/GST stop at June, vehicles at May and confidence at March. The dashboard does not fabricate missing observations to force a common endpoint.</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="section-title">About this project</div>', unsafe_allow_html=True)
    st.write(
        "India Consumption Pulse is an educational macro-demand dashboard. It brings together five public indicators "
        "that describe different parts of the household-consumption cycle: the prices consumers face, how households "
        "feel, tax receipts associated with formal economic activity, and demand for a major discretionary purchase."
    )
    st.markdown(
        '<div class="callout"><b>Core question:</b> Are household demand conditions strengthening, weakening, or becoming more uneven—and do prices, confidence and observed spending signals tell a consistent story?</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### What each indicator contributes")
    a, b = st.columns(2)
    with a:
        st.markdown(
            """<div class="insight-card"><h4>Prices and confidence</h4><ul>
            <li><b>CPI inflation</b> measures the speed of consumer-price change, not the absolute cost of living.</li>
            <li><b>Food inflation</b> matters disproportionately because it can compress household discretionary budgets.</li>
            <li><b>CSI</b> captures perceptions of current conditions; <b>FEI</b> captures expectations one year ahead.</li>
            </ul></div>""",
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """<div class="insight-card"><h4>Activity and discretionary demand</h4><ul>
            <li><b>Gross GST</b> is a high-frequency formal-economy activity signal, but is nominal and seasonal.</li>
            <li><b>Passenger-vehicle sales</b> proxy large discretionary purchases and financing-sensitive demand.</li>
            <li>SIAM figures are wholesale dispatches; they need not equal final retail registrations in the same month.</li>
            </ul></div>""",
            unsafe_allow_html=True,
        )
    st.markdown(
        """<div class="insight-card"><h4>Monetary policy and borrowing conditions</h4><ul>
        <li><b>Repo rate</b> is the policy rate at which RBI lends to banks and influences borrowing costs across the economy.</li>
        <li><b>Fixed reverse repo</b> remains published at 3.35%, but it is no longer the operative corridor floor.</li>
        <li><b>SDF</b> is the relevant liquidity-absorption floor since April 2022 and should be read alongside repo.</li>
        </ul></div>""", unsafe_allow_html=True,
    )

    st.markdown("#### Comparative analysis — what the latest signals mean")
    latest_i, latest_c, latest_g, latest_v, latest_r = d["inflation"].iloc[-1], d["confidence"].iloc[-1], d["gst"].iloc[-1], d["vehicles"].iloc[-1], d["rates"].iloc[-1]
    vehicle_yoy = (latest_v.domestic_sales_units / d["vehicles"].loc[d["vehicles"].date == latest_v.date - pd.DateOffset(years=1), "domestic_sales_units"].iloc[0] - 1) * 100
    st.caption("Comparable direction, not comparable units: each line below starts at 100 in July 2024.")
    visual_parts = []
    for frame, col, label in [
        (d["inflation"], "cpi_inflation_yoy", "Inflation"),
        (d["confidence"], "csi", "Confidence"),
        (d["gst"], "gross_gst_crore", "GST"),
        (d["vehicles"], "domestic_sales_units", "Vehicles"),
        (d["rates"], "repo_rate", "Repo rate"),
    ]:
        temp = frame.loc[frame.date >= pd.Timestamp("2024-07-01"), ["date", col]].dropna().copy()
        temp["Indexed value"] = temp[col] / temp[col].iloc[0] * 100
        temp["Signal"] = label
        visual_parts.append(temp[["date", "Indexed value", "Signal"]])
    visual_df = pd.concat(visual_parts)
    comparison_chart = alt.Chart(visual_df).mark_line(point=alt.OverlayMarkDef(size=42), strokeWidth=2.8).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0, tickCount=7)),
        y=alt.Y("Indexed value:Q", title="Index · Jul 2024 = 100", scale=alt.Scale(zero=False)),
        color=alt.Color("Signal:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())), title=None),
        tooltip=[alt.Tooltip("date:T", title="Period", format="%B %Y"), "Signal:N", alt.Tooltip("Indexed value:Q", format=".1f")],
    ).properties(height=330)
    st.altair_chart(comparison_chart.configure_view(strokeWidth=0).configure_axis(gridColor="#DED8CE"), use_container_width=True)

    left_chart, right_chart = st.columns(2)
    confidence_long = d["confidence"].melt("date", ["csi", "fei"], var_name="Measure", value_name="Index")
    confidence_long["Measure"] = confidence_long.Measure.map({"csi": "Current situation", "fei": "Future expectations"})
    confidence_chart = alt.Chart(confidence_long).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)),
        y=alt.Y("Index:Q", scale=alt.Scale(domain=[85, 130])),
        color=alt.Color("Measure:N", scale=alt.Scale(range=["#2D756C", "#C49A45"]), title=None),
        tooltip=[alt.Tooltip("date:T", format="%b %Y"), "Measure:N", alt.Tooltip("Index:Q", format=".1f")],
    ).properties(title="Confidence: present vs future", height=245)
    neutral = alt.Chart(pd.DataFrame({"Index": [100]})).mark_rule(color="#8C8176", strokeDash=[5, 5]).encode(y="Index:Q")
    left_chart.altair_chart((confidence_chart + neutral).configure_view(strokeWidth=0), use_container_width=True)

    price_long = d["inflation"].melt("date", ["cpi_inflation_yoy", "food_inflation_yoy"], var_name="Measure", value_name="Percent")
    price_long["Measure"] = price_long.Measure.map({"cpi_inflation_yoy": "Headline CPI", "food_inflation_yoy": "Food CPI"})
    price_chart = alt.Chart(price_long).mark_area(opacity=.22, line={"strokeWidth":2.4}, point=alt.OverlayMarkDef(size=26)).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)),
        y=alt.Y("Percent:Q", title="Year-on-year, %"),
        color=alt.Color("Measure:N", scale=alt.Scale(range=["#EF6A4C", "#C49A45"]), title=None),
        tooltip=[alt.Tooltip("date:T", format="%b %Y"), "Measure:N", alt.Tooltip("Percent:Q", format=".2f")],
    ).properties(title="Inflation: headline vs food", height=245)
    right_chart.altair_chart(price_chart.configure_view(strokeWidth=0), use_container_width=True)
    rate_long = d["rates"].melt("date", ["repo_rate", "fixed_reverse_repo_rate", "sdf_rate"], var_name="Measure", value_name="Percent")
    rate_long["Measure"] = rate_long.Measure.map({"repo_rate":"Policy repo", "fixed_reverse_repo_rate":"Fixed reverse repo", "sdf_rate":"SDF"})
    rate_chart = alt.Chart(rate_long).mark_line(interpolate="step-after", point=True, strokeWidth=2.5).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)), y=alt.Y("Percent:Q", title="Rate, %", scale=alt.Scale(zero=False)),
        color=alt.Color("Measure:N", scale=alt.Scale(range=["#7B61A8", "#EF6A4C", "#2D756C"]), title=None),
        tooltip=[alt.Tooltip("date:T", format="%b %Y"), "Measure:N", alt.Tooltip("Percent:Q", format=".2f")]
    ).properties(title="RBI policy-rate corridor", height=270)
    st.altair_chart(rate_chart.configure_view(strokeWidth=0), use_container_width=True)
    st.markdown(
        f"""
        - **Inflation has re-accelerated:** headline CPI rose to **{latest_i.cpi_inflation_yoy:.2f}% in {latest_i.date:%B %Y}**, with food inflation at **{latest_i.food_inflation_yoy:.2f}%**. This suggests renewed pressure on household budgets, especially for lower-income consumers.

        - **Present confidence remains cautious:** the urban CSI was **{latest_c.csi:.1f} in {latest_c.date:%B %Y}**, below the neutral level of 100. Households therefore remained pessimistic about current conditions at that survey round.

        - **Expectations are better than present perceptions:** FEI was **{latest_c.fei:.1f}**, comfortably above 100. The **{latest_c.fei-latest_c.csi:.1f}-point** CSI–FEI gap indicates optimism about the year ahead despite dissatisfaction with current conditions.

        - **Formal activity remains large:** gross GST was **₹{latest_g.gross_gst_crore/100000:.2f} lakh crore in {latest_g.date:%B %Y}**. Read this as a broad nominal activity signal—not a pure measure of real household consumption—because inflation, imports, compliance and timing also affect collections.

        - **Vehicle demand is comparatively strong:** passenger-vehicle wholesale sales reached **{latest_v.domestic_sales_units/100000:.2f} lakh units in {latest_v.date:%B %Y}**, approximately **{vehicle_yoy:.1f}% higher** than the same month a year earlier. This points to resilience in a financing-sensitive discretionary category.

        - **Monetary policy is more supportive than in early 2025:** the repo rate is **{latest_r.repo_rate:.2f}%**, down **{d['rates'].iloc[0].repo_rate-latest_r.repo_rate:.2f} percentage points** from January 2024. Lower policy rates can support credit-sensitive consumption with a lag, though actual loan-rate transmission varies.

        - **Reverse repo needs context:** the fixed reverse repo remains **{latest_r.fixed_reverse_repo_rate:.2f}%**, while the operative SDF floor is **{latest_r.sdf_rate:.2f}%**. For current liquidity conditions, SDF is the economically relevant comparison.

        - **Combined inference:** the indicators describe an **uneven but resilient consumption environment**. Current household sentiment is subdued and food-price pressure has returned, yet forward expectations and passenger-vehicle demand are stronger than the confidence reading alone would imply.

        - **Possible interpretation:** spending may be stronger among households able to access credit or absorb higher prices, while budget-sensitive households remain cautious. This is an inference, not something these aggregate series can prove directly.
        """
    )

    st.markdown("#### How to use the analysis responsibly")
    st.markdown(
        """
        - Compare direction and turning points rather than expecting all series to move in the same month.
        - Check each series' latest period before comparing readings; release schedules differ.
        - Treat GST and vehicle sales for seasonality, festival timing, year-end effects and policy changes.
        - Allow for transmission lags: a repo-rate cut does not immediately or uniformly reduce every household borrowing rate.
        - Use correlations as exploratory evidence only. A short shared trend does not establish causation.
        - Supplement this dashboard with rural confidence, retail registrations, real consumption expenditure and income data before making investment or policy decisions.
        """
    )
    st.markdown('<div class="callout warn"><b>Scope:</b> This is an educational analytical tool, not an economic forecast or investment recommendation. The Data desk records every coverage limitation and official source.</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="profile-footer">
      <strong>Prof. V. Ravichandran · The Mountain Path Academy</strong><br>
      Visiting Faculty at Leading Business Schools<br>
      Finance, Risk Management &amp; Quantitative Analytics<br><br>
      <a href="https://www.linkedin.com/in/trichyravis" target="_blank">LinkedIn</a> &nbsp;·&nbsp;
      <a href="https://github.com/trichyravis" target="_blank">GitHub</a> &nbsp;·&nbsp;
      <a href="https://themountainpathacademy.com/about.html" target="_blank">Faculty profile</a> &nbsp;·&nbsp;
      <a href="https://themountainpathacademy.com/contact" target="_blank">Contact</a><br><br>
      <small>India Consumption Pulse · Educational analysis · Source limitations are documented in the Data desk</small>
    </div>
    """,
    unsafe_allow_html=True,
)
