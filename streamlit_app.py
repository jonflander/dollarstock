import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import calendar

st.set_page_config(page_title="Stock Volume Analysis", layout="wide")

st.title("Stock Volume Analysis")

# Sidebar inputs
with st.sidebar:
    st.header("Input Parameters")
    
    # Stock symbol input
    symbol = st.text_input("Stock Symbol", value="AAPL").upper()
    
    # Date range inputs
    st.subheader("Period 1")
    first_period_start = st.date_input("Start Date (Period 1)", value=datetime(2023, 1, 1).date())
    first_period_end = st.date_input("End Date (Period 1)", value=datetime(2023, 12, 31).date())
    
    st.subheader("Period 2")
    second_period_start = st.date_input("Start Date (Period 2)", value=datetime(2024, 1, 1).date())
    second_period_end = st.date_input("End Date (Period 2)", value=datetime(2024, 12, 31).date())

    analyze_button = st.button("Analyze Stock", type="primary")

# Main content
if analyze_button:
    # Show loading message
    with st.spinner(f'Fetching data for {symbol}...'):
        try:
            # Get the earlier start date and later end date for data fetching
            start_date = min(first_period_start, second_period_start)
            end_date = max(first_period_end, second_period_end)
            
            # Download the data
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                # Calculate Dollar Volume
                df['DollarVolume'] = df['Close'] * df['Volume']
                
                st.success("Data retrieved successfully!")
                
                # Create tabs for different visualizations
                tab1, tab2, tab3, tab4 = st.tabs(["Volume Comparison", "Dollar Volume Comparison", 
                                                "Monthly Dollar Volume", "Summary Statistics"])
                
                # Colors for the periods
                colors = {
                    f'Period 1 ({first_period_start} to {first_period_end})': '#000000',
                    f'Period 2 ({second_period_start} to {second_period_end})': '#40B4A6'
                }
                
                # Function to calculate days since period start
                def days_since_start(date, start_date):
                    return (date - start_date).days
                
                # Volume Comparison Tab
                with tab1:
                    fig = go.Figure()
                    periods = [
                        (f'Period 1 ({first_period_start} to {first_period_end})', first_period_start, first_period_end),
                        (f'Period 2 ({second_period_start} to {second_period_end})', second_period_start, second_period_end)
                    ]
                    
                    for period_name, start_date, end_date in periods:
                        period_data = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                        if not period_data.empty:
                            x_values = [days_since_start(d.date(), start_date) for d in period_data.index]
                            
                            fig.add_trace(go.Scatter(
                                x=x_values,
                                y=period_data['Volume'],
                                name=period_name,
                                mode='lines',
                                line=dict(color=colors[period_name]),
                                hovertemplate='%{text}<br>Volume: %{y:,.0f}<extra></extra>',
                                text=[d.strftime('%B %d, %Y') for d in period_data.index],
                            ))
                    
                    fig.update_layout(
                        title=f'{symbol} - Trading Volume Comparison',
                        xaxis_title='Days Since Period Start',
                        yaxis_title='Volume',
                        hovermode='x unified',
                        showlegend=True,
                        plot_bgcolor='white',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Dollar Volume Comparison Tab
                with tab2:
                    fig = go.Figure()
                    
                    for period_name, start_date, end_date in periods:
                        period_data = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                        if not period_data.empty:
                            x_values = [days_since_start(d.date(), start_date) for d in period_data.index]
                            
                            fig.add_trace(go.Scatter(
                                x=x_values,
                                y=period_data['DollarVolume'],
                                name=period_name,
                                mode='lines',
                                line=dict(color=colors[period_name]),
                                hovertemplate='%{text}<br>Dollar Volume: $%{y:,.2f}<br>Price: $%{customdata[0]:.2f}<br>Volume: %{customdata[1]:,.0f}<extra></extra>',
                                text=[d.strftime('%B %d, %Y') for d in period_data.index],
                                customdata=list(zip(period_data['Close'], period_data['Volume']))
                            ))
                    
                    fig.update_layout(
                        title=f'{symbol} - Trading Dollar Volume Comparison',
                        xaxis_title='Days Since Period Start',
                        yaxis_title='Dollar Volume ($)',
                        hovermode='x unified',
                        showlegend=True,
                        plot_bgcolor='white',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Monthly Dollar Volume Tab
                with tab3:
                    monthly_data_all = []
                    for period_name, start_date, end_date in periods:
                        period_data = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                        if not period_data.empty:
                            # Calculate monthly aggregates
                            period_data = period_data.reset_index()
                            period_data['Year'] = period_data['Date'].dt.year
                            period_data['Month'] = period_data['Date'].dt.month
                            monthly_data = period_data.groupby(['Year', 'Month']).agg({
                                'Volume': 'sum',
                                'Close': 'mean',
                                'DollarVolume': 'sum'
                            }).reset_index()
                            
                            monthly_data['Period'] = period_name
                            monthly_data['MonthLabel'] = monthly_data.apply(
                                lambda x: f"{calendar.month_name[x['Month']]} {x['Year']}", axis=1)
                            monthly_data_all.append(monthly_data)
                    
                    if monthly_data_all:
                        monthly_df = pd.concat(monthly_data_all, ignore_index=True)
                        fig = go.Figure()
                        
                        # Sort the data by Year, Month to ensure consistent ordering
                        monthly_df = monthly_df.sort_values(['Year', 'Month'])
                        
                        # Create a common x-axis label for both periods
                        unique_months = monthly_df.drop_duplicates(['Year', 'Month'])[['Year', 'Month']]
                        unique_months = unique_months.sort_values(['Year', 'Month'])
                        month_labels = [calendar.month_name[m] for _, m in zip(unique_months['Year'], unique_months['Month'])]
                        
                        # Plot bars for each period
                        for period_name in colors:
                            period_data = monthly_df[monthly_df['Period'] == period_name]
                            if not period_data.empty:
                                fig.add_trace(go.Bar(
                                    x=month_labels,
                                    y=period_data['DollarVolume'],
                                    name=period_name,
                                    marker_color=colors[period_name],
                                    hovertemplate='%{text}<br>Dollar Volume: $%{y:,.2f}<extra></extra>',
                                    text=period_data.apply(lambda x: f"{calendar.month_name[x['Month']]} {x['Year']}", axis=1)  # Keep full date in hover
                                ))
                        
                        fig.update_layout(
                            title=f'{symbol} - Monthly Trading Dollar Volume Comparison',
                            xaxis_title='Month',
                            yaxis_title='Dollar Volume ($)',
                            xaxis=dict(
                                tickangle=45,
                                type='category'
                            ),
                            hovermode='x unified',
                            barmode='group',
                            bargap=0.15,
                            bargroupgap=0.1,
                            showlegend=True,
                            plot_bgcolor='white',
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Summary Statistics Tab
                with tab4:
                    st.header("Period Summary")
                    
                    summary_data = []
                    for period_name, start_date, end_date in periods:
                        period_data = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                        if not period_data.empty:
                            total_volume = int(period_data['Volume'].sum())
                            avg_price = float(period_data['Close'].mean())
                            total_dollar_volume = float(period_data['DollarVolume'].sum())
                            summary_data.append({
                                'Period': period_name,
                                'Total Volume': f"{total_volume:,}",
                                'Average Price': f"${avg_price:.2f}",
                                'Total Dollar Volume': f"${total_dollar_volume:,.2f}",
                            })
                    
                    if summary_data:
                        st.dataframe(pd.DataFrame(summary_data), hide_index=True)
                    
                    st.header("Monthly Breakdown")
                    if monthly_data_all:
                        monthly_breakdown = []
                        for monthly_data in monthly_data_all:
                            for _, row in monthly_data.iterrows():
                                monthly_breakdown.append({
                                    'Period': row['Period'],
                                    'Year': str(int(row['Year'])),  # Convert to int and then string to remove comma
                                    'Month': calendar.month_name[row['Month']],
                                    'Total Volume': f"{int(row['Volume']):,}",
                                    'Average Price': f"${float(row['Close']):.2f}",
                                    'Total Dollar Volume': f"${float(row['DollarVolume']):,.2f}",
                                })
                        
                        if monthly_breakdown:
                            st.dataframe(pd.DataFrame(monthly_breakdown), hide_index=True)
            else:
                st.error(f"No data available for {symbol} in the specified date range.")
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
