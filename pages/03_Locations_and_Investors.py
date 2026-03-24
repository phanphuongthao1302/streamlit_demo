import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Unicorn Locations & Investors",
    layout="wide",
)

df=st.session_state.get("unicorns_df")
if df is None:
    st.stop()

st.title("Locations & Investors")

st.sidebar.header("Location filters")
country_sel = st.sidebar.multiselect(
    "Country", options=sorted(df["country"].dropna().unique()), default=[]
)

filtered = df.copy()
if country_sel:
    filtered = filtered[filtered["country"].isin(country_sel)]

st.markdown("### Unicorn hubs by geography")

country_counts = (
    filtered.groupby(["country", "industry"])
    .size()
    .reset_index(name="count")
)

fig_country = px.treemap(
    country_counts,
    path=["country", "industry"],
    values="count",
    title="Unicorn hubs by country and industry",
    color="count",
    color_continuous_scale="Tealgrn",
)
st.plotly_chart(fig_country, use_container_width=True)

st.markdown(
    """
**Insight – Where:** Larger blocks in the treemap highlight **countries and industries where unicorn activity is concentrated**.  
**Action:** Use these hubs as **priority locations** for expansion, hiring, or ecosystem partnerships.
"""
)

city_counts = (
    filtered.groupby(["city", "industry"])
    .size()
    .reset_index(name="count")
)

st.markdown("#### Top country–industry hubs")
st.dataframe(
    country_counts.sort_values("count", ascending=False).head(25),
    use_container_width=True,
)

st.markdown(
    """
**Action:** Filter this table to create a **shortlist of target city–industry pairs** for on‑the‑ground research or events.
"""
)

st.markdown("### Top investors")

all_investors = (
    filtered["investors"]
    .str.split(",")
    .explode()
    .str.strip()
    .dropna()
    .value_counts()
)

top_n = st.selectbox("Number of investors to display", [10, 20, 30], index=0)
top_investors = (
    all_investors.head(top_n)
    .reset_index()
)

col1, col2 = st.columns((2, 1))
with col1:
    fig_inv = px.bar(
        top_investors,
        x="investors",
        y="count",
        title="Top investors by unicorn count",
        labels={"investor": "Investor", "count": "Number of unicorns"},
        color="count",
        color_continuous_scale="Blues",
    )
    fig_inv.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_inv, use_container_width=True)
with col2:
    st.dataframe(top_investors, use_container_width=True, height=350)

st.markdown(
    """
**Insight – Why:** Investors with the highest counts are **central players** in the unicorn ecosystem and often shape funding norms and valuations.  
**Action:** Use this list to **identify potential lead investors or syndicate partners**, or to map where your pipeline overlaps with top funds.
"""
)

st.markdown("### Detailed unicorn list")

col_country, col_city, col_ind = st.columns(3)
with col_country:
    country_filter = st.selectbox(
        "Country", options=["All"] + sorted(filtered["country"].dropna().unique())
    )
with col_city:
    city_filter = st.selectbox(
        "City", options=["All"] + sorted(filtered["city"].dropna().unique())
    )
with col_ind:
    industry_filter = st.selectbox(
        "Industry", options=["All"] + sorted(filtered["industry"].dropna().unique())
    )

detail = filtered.copy()
if country_filter != "All":
    detail = detail[detail["country"] == country_filter]
if city_filter != "All":
    detail = detail[detail["city"] == city_filter]
if industry_filter != "All":
    detail = detail[detail["industry"] == industry_filter]

cols = [
    "company",
    "country",
    "city",
    "industry",
    "valuation",
    "funding",
    "year_founded",
    "date_joined",
]
st.dataframe(
    detail[cols].sort_values("valuation", ascending=False),
    use_container_width=True,
    height=450,
)

st.markdown(
    """
**Insight – Now what:** This filtered table is your **action list** of companies that match your geographic and industry criteria.  
**Action:** Export or copy this subset to drive **outreach, due diligence, or partnership conversations** focused on the highest‑value targets first.
"""
)