import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide",page_title='Startup Analysis')

df=pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month


def load_overall_analysis():
    st.title('Overall Analysis')
    #total invested amount
    total=round(df['amount'].sum())
    #maximum amount infused in a startyup
    max_funding=df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    #average
    avg_funding=df.groupby('startup')['amount'].sum().mean()
    #total funding
    total_funding=df['startup'].nunique()

    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.metric('Total',str(total) + 'Cr')
    with col2:
         st.metric('Max', str(max_funding) + 'Cr')
    with col3:
        st.metric('Average',str(avg_funding)+'Cr')
    with col4:
        st.metric('Funded Startups',str( total_funding)+'Cr')
    st.header('MoM graph')
    select_option=st.selectbox('Select Type',['Toatl','Count'])
    if select_option=='Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
    fig = px.line(
        temp_df,
        x='x_axis',
        y='amount',
        labels={'x_axis': 'Month-Year', 'amount': 'Total Investment Amount'},
        title='Month-on-Month Investment Trend'
    )
    st.plotly_chart(fig)

def load_startup_details(startup_name):
    st.title(startup_name)
    st.subheader("Startup Funding Details")

    startup_df = df[df['startup'] == startup_name]

    # Metrics
    total_raised = startup_df['amount'].sum()
    total_rounds = startup_df.shape[0]
    unique_investors = set(','.join(startup_df['investors'].dropna()).split(','))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Funding Raised", f"₹{total_raised:,.0f}")
    col2.metric("Funding Rounds", total_rounds)
    col3.metric("Unique Investors", len(unique_investors))

    # Show recent rounds
    st.subheader("Funding Rounds")
    st.dataframe(startup_df[['date', 'round', 'amount', 'investors', 'city']].sort_values(by='date', ascending=False))

    # Year-wise line chart
    if not startup_df.empty:
        yearwise = startup_df.groupby('year')['amount'].sum()
        fig = px.line(
            x=yearwise.index,
            y=yearwise.values,
            labels={'x': 'Year', 'y': 'Funding Amount'},
            title=f"Year-wise Funding for {startup_name}"
        )
        st.plotly_chart(fig)

    # Optional: Show Investors Pie
    st.subheader("Investor Contribution Breakdown")
    investor_series = startup_df.groupby('investors')['amount'].sum()
    fig_pie = px.pie(
        names=investor_series.index,
        values=investor_series.values,
        title="Funding by Investors"
    )
    st.plotly_chart(fig_pie)

    # Raw Data
    with st.expander("Show Raw Data"):
        st.dataframe(startup_df.reset_index(drop=True))


def load_investor_details(investor):
    st.title(investor)
    #load the current recent 5 investors
    last5_df=df[df['investors'].str.contains(investor)].head()[['date','startup','vertical','city','round','amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)



    # Title
    st.title(" Startup Funding Analysis")

    # Sidebar
    st.sidebar.title(' Filter Investments')
    investor = st.sidebar.selectbox("Select Investor", df['investors'].dropna().unique())

    # Filter Data
    filtered_df = df[df['investors'].str.contains(investor, na=False)]

    # Metrics Row
    st.markdown(" Investor Insights")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total Invested", f"₹{filtered_df['amount'].sum():,.0f}")
    col_m2.metric("No. of Startups", filtered_df['startup'].nunique())

    # First Row
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Biggest Investments"):
            top_investments = filtered_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(5)
            fig_bar = px.bar(
                top_investments,
                x=top_investments.index,
                y=top_investments.values,
                labels={'x': 'Startup', 'y': 'Amount'},
                color=top_investments.values,
                title="Top 5 Biggest Investments"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        with st.expander(" Sectors Invested In"):
            vertical_series = filtered_df.groupby('vertical')['amount'].sum()
            fig_pie = px.pie(
                names=vertical_series.index,
                values=vertical_series.values,
                title="Sector Distribution",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Second Row
    col3, col4 = st.columns(2)

    with col3:
        with st.expander(" City-wise Investments"):
            city_series = filtered_df.groupby('city')['amount'].sum().sort_values(ascending=False).head(5)
            fig_city = px.bar(
                city_series,
                x=city_series.index,
                y=city_series.values,
                labels={'x': 'City', 'y': 'Amount'},
                color=city_series.values,
                title="Top Cities by Investment"
            )
            st.plotly_chart(fig_city, use_container_width=True)

    with col4:
        with st.expander(" Funding Rounds"):
            round_series = filtered_df.groupby('round')['amount'].sum()
            fig_rounds = px.pie(
                names=round_series.index,
                values=round_series.values,
                title="Funding Round Distribution",
                hole=0.3
            )
            st.plotly_chart(fig_rounds, use_container_width=True)

    # Optional: Show raw data
    with st.expander(" View Raw Data"):
        st.dataframe(filtered_df.reset_index(drop=True))

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year

    # Get the Series, don't plot yet
    year_series = df[df['investors'].str.contains(investor, na=False)] \
        .groupby('year')['amount'].sum()

    # Now use Plotly to plot
    fig = px.line(
        x=year_series.index,
        y=year_series.values,
        labels={'x': 'Year', 'y': 'Total Investment Amount'},
        title=f"Year-wise Investment by {investor}"
    )
    st.plotly_chart(fig)



option=st.sidebar.selectbox('Select one',['Overall Analysis','Startup','Investor'])
if option=='Overall Analysis':
    load_overall_analysis()

elif option == 'Startup':
    selected_startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find Startup Details')
    if btn1:
        load_startup_details(selected_startup)

else:
    select_investor=st.sidebar.selectbox('Select Startup',sorted(set(df['investors'].str.split(',').sum())))
    btn2=st.sidebar.button('Find Investor  Details')
    if btn2:
        load_investor_details(select_investor)
