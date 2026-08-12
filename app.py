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
      .block-container { max-width: 1280px; padding-top: 2.2rem; }
      [data-testid="stSidebar"] { background: #18332F; }
      [data-testid="stSidebar"] * { color: #F6F2EA !important; }
      .eyebrow { letter-spacing:.14em; text-transform:uppercase; color:#C8583E; font-size:.72rem; font-weight:700; }
      .hero { font-size:3rem; line-height:1.02; letter-spacing:-.045em; color:#18332F; font-weight:750; margin:.35rem 0 .6rem; }
      .subhero { color:#53645E; max-width:780px; font-size:1.04rem; margin-bottom:1.2rem; }
      .pill { display:inline-block; padding:.28rem .65rem; border:1px solid #B7B0A4; border-radius:999px; color:#53645E; font-size:.78rem; margin:.1rem .25rem .1rem 0; }
      div[data-testid="stMetric"] { background:#FFFDF8; border:1px solid #DDD5C8; border-radius:14px; padding:15px 16px; box-shadow:0 6px 20px rgba(24,51,47,.04); }
      div[data-testid="stMetric"] label { color:#69756F; }
      .section-title { color:#18332F; font-size:1.5rem; font-weight:700; letter-spacing:-.025em; margin-top:1rem; }
      .callout { background:#E8EFEA; border-left:4px solid #2D756C; padding:1rem 1.1rem; border-radius:0 10px 10px 0; color:#26443F; }
      .warn { background:#F7E7D7; border-left-color:#EF6A4C; }
      footer { visibility:hidden; }
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
        "catalog": pd.read_csv(DATA / "source_catalog.csv", parse_dates=["latest_period"]),
    }


d = load_data()
COLORS = {"Inflation": "#EF6A4C", "Confidence": "#2D756C", "GST": "#C49A45", "Vehicles": "#657B9A"}


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
    page = st.radio("Navigate", ["Pulse", "Deep dive", "Relationships", "Data desk"], label_visibility="collapsed")
    st.markdown("---")
    start = st.date_input("Start period", pd.Timestamp("2024-07-01"), min_value=pd.Timestamp("2024-01-01"), max_value=pd.Timestamp("2026-07-31"))
    show_notes = st.toggle("Show methodology notes", value=True)
    st.markdown("---")
    st.caption("Snapshot prepared 12 Aug 2026 · Official release dates differ by series.")

start_ts = pd.Timestamp(start)
infl = d["inflation"].query("date >= @start_ts")
conf = d["confidence"].query("date >= @start_ts")
gst = d["gst"].query("date >= @start_ts")
veh = d["vehicles"].query("date >= @start_ts")

st.markdown('<div class="eyebrow">India · household demand monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Consumption, beneath the headline.</div>', unsafe_allow_html=True)
st.markdown('<div class="subhero">Four signals—prices, sentiment, tax receipts and automobile demand—read together, with their publication gaps kept visible.</div>', unsafe_allow_html=True)
st.markdown('<span class="pill">Official-source snapshot</span><span class="pill">Monthly + bi-monthly</span><span class="pill">Latest available ≠ July 2026</span>', unsafe_allow_html=True)

if page == "Pulse":
    latest_i, latest_c, latest_g, latest_v = infl.iloc[-1], conf.iloc[-1], gst.iloc[-1], veh.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Headline inflation", f"{latest_i.cpi_inflation_yoy:.2f}%", f"{mom_delta(infl, 'cpi_inflation_yoy'):+.2f} pp", help="All-India Combined CPI, year on year")
    c2.metric("Urban confidence", f"{latest_c.csi:.1f}", f"{mom_delta(conf, 'csi'):+.1f} pts", help="CSI; below 100 denotes pessimism")
    c3.metric("Gross GST", f"₹{latest_g.gross_gst_crore/100000:.2f}L cr", f"{mom_delta(gst, 'gross_gst_crore')/1000:+.1f}k cr")
    c4.metric("Passenger vehicles", f"{latest_v.domestic_sales_units/100000:.2f}L", f"{mom_delta(veh, 'domestic_sales_units')/1000:+.1f}k", help="SIAM domestic wholesale dispatches")

    st.markdown('<div class="section-title">Different clocks, one demand story</div>', unsafe_allow_html=True)
    st.caption("Each series rebased to 100 at its first available observation in the selected window. This compares direction, not units.")
    indexed = []
    specs = [(infl, "cpi_inflation_yoy", "Inflation"), (conf, "csi", "Confidence"), (gst, "gross_gst_crore", "GST"), (veh, "domestic_sales_units", "Vehicles")]
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
    topic = st.segmented_control("Indicator", ["Inflation", "Confidence", "GST", "Vehicles"], default="Inflation")
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
    else:
        st.altair_chart(line_chart(veh, "date", "domestic_sales_units", "#657B9A"), use_container_width=True)
        st.caption("Domestic wholesale dispatches. This is not VAHAN retail registration data; festive stocking can shift timing.")

elif page == "Relationships":
    st.markdown('<div class="section-title">Aligned monthly signals</div>', unsafe_allow_html=True)
    st.caption("Bi-monthly confidence is forward-filled for one month only. Values are standardized before correlation.")
    merged = infl[["date", "cpi_inflation_yoy"]].merge(gst[["date", "gross_gst_crore"]], on="date", how="outer").merge(veh[["date", "domestic_sales_units"]], on="date", how="outer").merge(conf[["date", "csi"]], on="date", how="outer").sort_values("date")
    merged["csi"] = merged.csi.ffill(limit=1)
    merged = merged.query("date >= @start_ts")
    labels = {"cpi_inflation_yoy":"Inflation", "csi":"Confidence", "gross_gst_crore":"GST", "domestic_sales_units":"Vehicles"}
    corr = merged[list(labels)].corr(min_periods=6).rename(index=labels, columns=labels).round(2)
    corr_long = corr.stack().rename("correlation").reset_index()
    heat = alt.Chart(corr_long).mark_rect(cornerRadius=4).encode(x=alt.X("level_1:N", title=None), y=alt.Y("level_0:N", title=None), color=alt.Color("correlation:Q", scale=alt.Scale(domain=[-1,0,1], range=["#C8583E", "#F4EEE5", "#2D756C"]), title="r"), tooltip=["level_0", "level_1", "correlation"]).properties(height=370)
    text_layer = alt.Chart(corr_long).mark_text(fontSize=15).encode(x="level_1:N", y="level_0:N", text=alt.Text("correlation:Q", format=".2f"), color=alt.condition("abs(datum.correlation) > 0.55", alt.value("white"), alt.value("#18332F")))
    st.altair_chart((heat + text_layer).configure_view(strokeWidth=0), use_container_width=True)
    st.markdown('<div class="callout warn"><b>Not a causal model.</b> The window is short, seasonal effects remain, and releases have different frequencies. Treat coefficients as prompts for investigation.</div>', unsafe_allow_html=True)

else:
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
    cols = st.columns(4)
    for col, (key, label) in zip(cols, [("inflation","Inflation"),("confidence","Confidence"),("gst","GST"),("vehicles","Vehicles")]):
        col.download_button(label, d[key].to_csv(index=False).encode(), file_name=f"india_{key}.csv", mime="text/csv", use_container_width=True)
    st.markdown('<div class="callout warn"><b>July 2026 is not backfilled.</b> As of the snapshot date, no series in this project had a complete, clean official July observation available for inclusion. The dashboard stops each indicator at its latest sourced period.</div>', unsafe_allow_html=True)

