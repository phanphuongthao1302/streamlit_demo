import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(
    page_title='Valuation and Funding', 
    layout='wide'
)

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Valuation and Funding')

industry_sel = st.sidebar.multiselect(
    'Industry',
    options=sorted(df['industry'].dropna().unique()),
    default=[]
)

country_sel = st.sidebar.multiselect(
    'Country',
    options=sorted(df['country'].dropna().unique()),
    default=[]
) # -> ['France', 'Austria']

filtered = df.copy()
if industry_sel: 
    filtered  = filtered[filtered['industry'].isin(industry_sel)]
if country_sel: 
    filtered  = filtered[filtered['country'].isin(country_sel)]

st.markdown('### Valuation distribution')

bins = [0,1,2,5,10,20,50,100,500]
labels = ['1-2B','2-5B','5-10B','10-20B','20-50B','50-100B','100-500B','500+']
filtered['valuation_band'] = pd.cut(filtered['valuation'], bins = bins, labels = labels)

band_counts = (
    filtered['valuation_band']
    .value_counts(dropna=False)
    .sort_index()
    .rename_axis('valuation_band')
    .reset_index(name='count'))

col1, col2 = st.columns(2)
with col1: 
    fig_band = px.bar(
        band_counts,
        x='count',
        y='valuation_band',
        orientation='h',
        title='Unicorn Count by Valuation Band',\
        labels = {'count':'Number of Unicorns','valuation_band':'Valuation Band'},
        color_discrete_sequence=["#22C55E"]
     )
    st.plotly_chart(fig_band, use_container_width=True)

with col2: 
    fig_pie = px.pie(
     band_counts,
     names='valuation_band',
     values='count',
     title='Unicorn Count by Valuation Band (Pie)',
     color_discrete_sequence=px.colors.sequential.Teal,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

skew_value = float(np.round(stats.skew(filtered['valuation'].dropna().values),2))
st.caption(f'Valuation skewness (positive = right-skewed):{skew_value}')

st.markdown(
    """
**Insight -What:** Most unicorns cluster in the lower valuation band, with a long right-tail or very large company, as indicated by the positive skew

**Action:** When benchmarking a company, compare it to its **valuation band peers** instead of only to extreme outliners
   """
)

st.markdown('### Top unicorns by valuation and ROI')
top_valuation = (
    filtered.nlargest(10, 'valuation')[['company','country', 'industry','valuation']])

filtered['roi'] = filtered['valuation']/filtered['funding']

top_roi = (filtered.nlargest(10, 'roi')[['company','country', 'industry','valuation', 'funding', 'roi']])

tab1, tab2 = st.tabs(['Top by Valuation', "Top by ROI"])

with tab1: 
    col_a, col_b = st.columns((2,1))
    with col_a: 
        fig_top_val = px.bar(
            top_valuation.sort_values('valuation'),
            x='valuation',
            y='company',
            orientation='h',
            title='Top 10 Unicorns by Valuation',
            labels = {'valuation':'Valuation','company':'Company'},
            color_discrete_sequence=["#38BDF8"] 
        )
        st.plotly_chart(fig_top_val, use_container_width=True)
    with col_b: 
       st.dataframe(
        top_valuation.reset_index(drop=True),
        use_container_width=True,
        height=350
       )
with tab2:
    col_c, col_d = st.columns((2, 1))
    with col_c: 
        fig_top_roi = px.bar(
            top_roi.sort_values('roi'),
            x='roi',
            y='company',
            orientation='h',
            title='Top 10 Unicorns by roi',
            labels = {'roi':'Roi','company':'Company'},
            color_discrete_sequence=["#38BDF8"] 
        )
    st.plotly_chart(fig_top_roi, use_container_width=True)
    with col_b: 
       st.dataframe(
        top_valuation.reset_index(drop=True),
        use_container_width=True,
        height=350
       )   
st.markdown(
     """
**Insight -How:** Some unicorns appear in both lists : others are large but capital-inefficient, or small but efficient 

**Action:** Use the **ROI to shortlist capital-efficient companies** for investment or as operational benchmarks, not just the biggest names by valuation
   """
)

st.markdown('### Valuation over time by Industry')

year_range = st.slider(
    'Year joined range', 
    int(filtered['date_joined'].min()), 
    int(filtered['date_joined'].max()), 
    (int(filtered['date_joined'].min()),int(filtered['date_joined'].max()) 
))

mask = (filtered["date_joined"] >= year_range[0]) & (filtered["date_joined"] <= year_range[1])
val_by_ind_year = (
    filtered[mask]
    .groupby(['date_joined', 'industry'])['valuation']
    .sum()
    .reset_index()
    )

tab_heat, tab_line = st.tabs(['Heatmap','Trend Lines'])
with tab_heat: 
   fig_heat = px.density_heatmap(
        val_by_ind_year,
        x='date_joined',
        y='industry',
        z='valuation',
        color_continuous_scale='Viridis',
        title='Total unicorn valuation by industry over years'
   )
   st.plotly_chart(fig_heat, use_container_width=True)
with tab_line: 
    fig_line = px.line(
       val_by_ind_year, 
       x='date_joined', 
       y='valuation',
       color='industry', 
       title='Total unicorns by industry over years',
       labels={"date_joined": "Year joined", "valuation": "Total valuation ($B)"},
       color_discrete_sequence=px.colors.qualitative.Set3,      
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown(
     """
**Insight -Why:** Industries with rapidly rising total valuation are where **capital and expectations are shifting over time**

**Action:** Align sector focus and hiring with **industries whose valuation is aceleration** in yout target region and year range. 
"""
)

st.markdown('### Hypothesis testing: compare industries')

col_i1, col_i2 = st.columns(2)
industries = sorted(df['industry'].dropna().unique())
with col_i1: 
    ind1 = st.selectbox(
    'Industries A',
     industries, 
     index = industries.index('Artificial Inteligence') if 'Artificial Inteligence' in industries else 0,
    )
with col_i2:
    default_b = 0 if industries[0] != ind1 else 1 
    ind2 = st.selectbox("Industry B", industries, index=default_b)  
       
if ind1 == ind2: 
    st.info('Please select two difference industries to run the t-test.')
else: 
     tmp = df.copy()
     tmp['roi'] = tmp['valuation']/tmp['funding']
     tmp['year_to_unicorn'] = tmp['date_joined'] - tmp['year_founded']

     metrics = {
        "Mean valuation ($B)": "valuation",
        "ROI (valuation / funding)": "roi",
        "Years to unicorn": "years_to_unicorn",
    }
     results = []
     for label, col in metrics.items(): 
        vals1 = tmp.loc[tmp['industry']==ind1, 'valuation'].dropna()
        vals2 = tmp.loc[tmp['industry']==ind2, 'valuation'].dropna()
        
        if len(vals1) < 2 or len(vals2) < 2:
            results.append(
                {
                    "Metric": label,
                    f"{ind1} mean": "n<2",
                    f"{ind2} mean": "n<2",
                    "t_stat": None,
                    "p_value": None,
                    "Significant (α=0.05)": "insufficient data",
                }
            )
            continue
    
        t_stat, p_value = ttest_ind(vals1, vals2, equal_var=False)
        alpha = 0.05
        sig = 'yes' if p_value < alpha else 'no'

        results.append(
            {
                "Metric": label,
                f"{ind1} mean": round(float(vals1.mean()), 2),
                f"{ind2} mean": round(float(vals2.mean()), 2),
                "t_stat": round(float(t_stat), 2),
                "p_value": round(float(p_value), 4),
                "Significant (α=0.05)": sig,
            })
        st.dataframe(results, use_container_width=True)

        any_sig = any(r["Significant (α=0.05)"] == "yes" for r in results)

        if any_sig:
            st.success(
            "At least one metric (valuation, ROI, or years to unicorn) shows a "
            f"statistically significant difference between **{ind1}** and **{ind2}**."
        )
            st.markdown(
            """
**Action:** When choosing between these industries, look at **which specific metric**
(valuation level, efficiency, or speed) is significant and align this with your
strategy. For example, prefer the industry with higher ROI if you care about
capital efficiency.
"""
        )
        else:
            st.info(
            "For valuation level, ROI, and years to unicorn, there is **no statistically "
            f"significant difference** between **{ind1}** and **{ind2}** at α = 0.05."
        )

            st.markdown(
            """
**Action:** For these two industries, do **not** prioritize purely on valuation levels.  
Let other factors such as **growth trajectory, risk profile, and unit economics**
drive your investment or product decisions.
""")

st.markdown("### Similar unicorns by industry profile")

industry_encoded = pd.get_dummies(df["industry"])
similarity_matrix = cosine_similarity(industry_encoded)

def recommend_similar(company_name, df_in, sim_matrix, n=5):
    try:
        idx = df_in.index[df_in["company"] == company_name][0]
    except IndexError:
        return pd.DataFrame(columns=["company", "industry", "valuation"])
    similar_indices = np.argsort(sim_matrix[idx])[::-1][1 : n + 1]
    return (
        df_in.loc[similar_indices, ["company", "country", "industry", "valuation"]]
        .reset_index(drop=True)
    )

company_options = sorted(df["company"].unique())
default_company = company_options.index("Stripe") if "Stripe" in company_options else 0
selected_company = st.selectbox(
    "Select a unicorn to find similar companies",
    company_options,
    index=default_company,
)

n_recs = st.slider("Number of similar companies", 3, 10, 5)
recs = recommend_similar(selected_company, df, similarity_matrix, n=n_recs)

col_r1, col_r2 = st.columns([1, 2])
with col_r1:
    st.metric("Selected unicorn", selected_company)
    st.metric("Industry", df.loc[df["company"] == selected_company, "industry"].iloc[0])
    st.metric(
        "Valuation ($B)",
        float(df.loc[df["company"] == selected_company, "valuation"].iloc[0]),
    )
with col_r2:
    st.dataframe(recs, use_container_width=True, height=350)

st.markdown(
    """
**Insight – Now what:** Similar companies often share **investor profiles, business models, or market dynamics**.  
**Action:** Use this list to **build peer groups** for valuation benchmarking, partnership outreach, or competitive analysis around the selected unicorn.
"""
)