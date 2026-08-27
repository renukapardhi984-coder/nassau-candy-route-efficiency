import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Route Efficiency", layout="wide")
st.title("🚚 Nassau Candy Distributor: Route Efficiency Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

df = load_data()

st.sidebar.header("Filter Options")
regions = ['All'] + list(df['Region'].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", regions)

ship_modes = ['All'] + list(df['Ship Mode'].dropna().unique())
selected_mode = st.sidebar.selectbox("Select Ship Mode", ship_modes)

threshold = st.sidebar.slider("Delay Threshold (Days)", min_value=1, max_value=30, value=7)

filtered_df = df.copy()
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

if selected_mode != 'All':
    filtered_df = filtered_df[filtered_df['Ship Mode'] == selected_mode]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", f"{len(filtered_df):,}")
col2.metric("Avg Lead Time", f"{filtered_df['Shipping_Lead_Time'].mean():.1f} Days")

delayed_count = (filtered_df['Shipping_Lead_Time'] > threshold).sum()
delay_freq = (delayed_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
col3.metric("Delay Frequency", f"{delay_freq:.1f}%")

efficiency_score = max(0, 100 - (filtered_df['Shipping_Lead_Time'].mean() * 3))
col4.metric("Route Efficiency Score", f"{efficiency_score:.1f}/100")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Route Overview", "🗺️ Geographic Heatmap", "🚢 Ship Mode Performance"])

with tab1:
    st.subheader("Route Efficiency Leaderboard")
    route_stats = filtered_df.groupby('Route').agg(
        Avg_Lead_Time=('Shipping_Lead_Time', 'mean'),
        Total_Orders=('Shipping_Lead_Time', 'count')
    ).reset_index()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Top 10 Fastest Routes")
        st.dataframe(route_stats.sort_values(by='Avg_Lead_Time').head(10))
    with col_b:
        st.write("### Bottom 10 Slowest Routes")
        st.dataframe(route_stats.sort_values(by='Avg_Lead_Time', ascending=False).head(10))

with tab2:
    st.subheader("US Shipping Efficiency Heatmap")
    state_df = filtered_df.groupby('State/Province')['Shipping_Lead_Time'].mean().reset_index()
    fig_map = px.choropleth(
        state_df,
        locations='State/Province',
        locationmode="USA-states",
        color='Shipping_Lead_Time',
        scope="usa",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.subheader("Ship Mode Performance")
    fig_box = px.box(filtered_df, x='Ship Mode', y='Shipping_Lead_Time', color='Ship Mode')
    st.plotly_chart(fig_box, use_container_width=True)
