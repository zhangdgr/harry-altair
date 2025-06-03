import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(page_title="Inside Airbnb Dashboard", layout="wide")
listings_data = pd.read_csv('listings.csv')

# Data cleaning
listings_data['price'] = listings_data['price'].replace('[\$,]', '', regex=True).astype(float)
filtered_data = listings_data[
    (listings_data['estimated_revenue_l365d'].notnull()) &
    (listings_data['estimated_revenue_l365d'] > 0) &
    (listings_data['price'].notnull()) &
    (listings_data['review_scores_rating'].notnull())
]

# Sidebar
st.sidebar.header("🔍 Filters")
neighborhood = st.sidebar.selectbox("Select Neighbourhood", ["All"] + sorted(filtered_data['neighbourhood_cleansed'].unique()))
room_type = st.sidebar.selectbox("Select Room Type", ["All"] + sorted(filtered_data['room_type'].unique()))
review_score_range = st.sidebar.slider("Select Review Score Range", 0.0, 5.0, (3.5, 5.0))
revenue_range = st.sidebar.slider("Select Revenue Range", int(filtered_data['estimated_revenue_l365d'].min()), int(filtered_data['estimated_revenue_l365d'].max()), (1000, 100000))

# Filters
filtered = filtered_data[
    (filtered_data['review_scores_rating'].between(*review_score_range)) &
    (filtered_data['estimated_revenue_l365d'].between(*revenue_range))
]
if neighborhood != "All":
    filtered = filtered[filtered['neighbourhood_cleansed'] == neighborhood]
if room_type != "All":
    filtered = filtered[filtered['room_type'] == room_type]

# Stacked Bar Chart, Average Revenue by Neighborhood and Room Type
st.subheader("Average Revenue by Neighbourhood and Room Type")
mean_revenue = filtered.groupby(['neighbourhood_cleansed', 'room_type'])['estimated_revenue_l365d'].mean().reset_index()
bar_chart = alt.Chart(mean_revenue).mark_bar().encode(
    x=alt.X('neighbourhood_cleansed:N', sort='-y', title='Neighbourhood'),
    y=alt.Y('estimated_revenue_l365d:Q', title='Avg Revenue'),
    color=alt.Color('room_type:N', title='Room Type'),
    tooltip=['neighbourhood_cleansed', 'room_type', 'estimated_revenue_l365d']
)
st.altair_chart(bar_chart, use_container_width=True)

# Review Score vs Revenue
st.subheader("Review Score vs Estimated Revenue")
scatter1 = alt.Chart(filtered).mark_circle(opacity=0.4, size=60).encode(
    x=alt.X('review_scores_rating:Q', scale=alt.Scale(domain=[3.5, 5.0]), title='Review Score'),
    y=alt.Y('estimated_revenue_l365d:Q', scale=alt.Scale(type='log'), title='Log(Revenue)'),
    color='room_type:N',
    tooltip=['name', 'neighbourhood_cleansed', 'room_type', 'review_scores_rating', 'estimated_revenue_l365d']
)
st.altair_chart(scatter1, use_container_width=True)

# Accommodates vs Revenue
st.subheader("Accommodates vs Estimated Revenue")
scatter2 = alt.Chart(filtered).mark_circle(opacity=0.4, size=60).encode(
    x='accommodates:Q',
    y=alt.Y('estimated_revenue_l365d:Q', scale=alt.Scale(type='log'), title='Log(Revenue)'),
    color='neighbourhood_cleansed:N',
    tooltip=['name', 'neighbourhood_cleansed', 'room_type', 'accommodates', 'estimated_revenue_l365d']
)
st.altair_chart(scatter2, use_container_width=True)
