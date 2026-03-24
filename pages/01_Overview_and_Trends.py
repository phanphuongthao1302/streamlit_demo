import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(
    page_title='Unicorn Overview and Trends',  
    layout='wide'
)

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Overview & Growth Trends')

st.sidebar.header('Overview filters')
years = st.sidebar.slider(
    'Year joined_range', 
    int(df['date_joined'].min()),
    int(df['date_joined'].max()), 
    (int(df['date_joined'].min()),int(df['date_joined'].max()))
) #-> [2008, 2022]

country_sel = st.sidebar.multiselect(
    'Country',
    options=sorted(df['country'].dropna().unique()),
    default=[]
) # -> ['France', 'Austria']

filtered = df.copy() 
filtered = filtered[(filtered['date_joined'] >= years[0]) & (filtered['date_joined'] <= years[1])]
if country_sel: 
    filtered  = filtered[filtered['country'].isin(country_sel)]

st.markdown('### Global snapshot')

col1, col2, col3, col4 = st.columns(4)
with col1: 
    st.metric('Unicorns', f'{len(filtered):,}')
with col2: 
    st.metric('Total valuation ($B):', f"{filtered['valuation'].sum():,.1f}")
with col3: 
    st.metric('Median valuation ($B):', f"{filtered['valuation'].median():,.1f}")
with col4:
    avg_growth = (filtered["date_joined"] - filtered["year_founded"]).dropna()
    avg_growth_years = float(np.round(avg_growth.mean(), 1)) if len(avg_growth) else np.nan
    st.metric("Avg. years to unicorn", avg_growth_years if not np.isnan(avg_growth_years) else "N/A")

st.markdown(
    """
***Insight -What:** This snapshot shows the **overall size and maturity** of the unicorn universe for your selected years and countries
***Action:** Use these KPIs to quickly benchmark the unicorn landscape against other datasets and time periods.
"""
)    

st.markdown('### Unicorn creation overtime')

year_counts=(
    filtered.groupby('date_joined') 
    .size() 
    .reset_index(name='count') 
    .sort_values('date_joined')
)

fig_year = px.area(
    year_counts, 
    x='date_joined', 
    y='count', 
    title='Number of unicorns joinning per year', 
    labels={'date_joined':'Year Joined', 'count':'Number of unicorns'}, 
    color_discrete_sequence=["#0F766E"]
)
fig_year.update_traces(mode="lines+markers", marker=dict(size=6))
st.plotly_chart(fig_year, use_container_width=True)

st.markdown(
    """
***Insight -How:**Peaks or slowdowns in this chart reveal **aceleration or coooling*** in unicorns creation over time
***Action:** Focus deeper analysis on periods with sharp changes (e.g. boom years) to understand drivers such as funding cycles or marco events
   """
)

st.markdown('### Unicorn count by continent')

cont_year = (
    filtered.groupby(['date_joined', 'continent'])
    .size() 
    .reset_index(name='count')
)

fig_cont = px.line(
    cont_year, 
    x='date_joined', 
    y='count',
    color='continent', 
    title='Unicorns count over time by continent', 
    labels={'date_joined':'Year Joined', 'count':'Number of unicorns'}, 
    color_discrete_sequence=["#0F766E"]
)

st.plotly_chart(fig_cont, use_container_width=True)

st.markdown(
    """
***Insight -Why (geopraphy):** Differences between continent highlight ** regional strength ** in building unicorns
***Action:** Use this view to prioritize ** scouting, hiring and expansion ** into regions with sustained growth ** or to identify under-served regions with merging potentials
   """
)

st.markdown('### Top investing industry')

recent_year = st.slider(
    'Focus year for industry view', 
    int(filtered['date_joined'].min()), 
    int(filtered['date_joined'].max()), 
    int(filtered['date_joined'].max())
)

recent = filtered[filtered['date_joined'] == recent_year]

ind_val = (
    recent.groupby('industry')['valuation']
    .sum()
    .reset_index()
    .sort_values('valuation', ascending=False)
)
if not ind_val.empty: 
    top_n = st.selectbox('Number of industries to display', options=[5,10,15], index=0)
    int_val_top = ind_val.head(top_n)

    col_a, col_b = st.columns((2,1))
    with col_a: 
        fig_ind = px.bar(
            int_val_top.sort_values('valuation'),  
            x='valuation', 
            y='industry',
            orientation = 'h', 
            title=f'Top industry by valuation in {recent_year}', 
            labels={'valuation':'Total valuation ($B)', 'industry':'Industry'}, 
            color_discrete_sequence=["#F97316"]
        )
        st.plotly_chart(fig_ind, use_container_width=True)
    with col_b: 
        st.dataframe(
            int_val_top.reset_index(drop=True),
            use_container_width=True,
            height=300
        )
        st.markdown(
    """
***Insight -Why (industry):** In {recent_year}, the leading industry by valuation reveal where **capital and growth expectations** are concentrated
***Action:** Target these industries for** deal flow, partnership or product offerings** if they align with your strategy** or look at lagging industries for contrarian opportunities
   """
   )
else:
  st.info('No unicorns for the selected year range')