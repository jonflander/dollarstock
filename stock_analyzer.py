import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import argparse
import calendar

def get_stock_data(symbol, start_date, end_date):
    """
    Fetch stock data from Yahoo Finance
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def create_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end):
    """
    Create volume comparison graph for two specific periods
    """
    # Create figure
    fig = go.Figure()
    
    # Colors from the reference image
    colors = {
        f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})': '#000000',
        f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})': '#40B4A6'
    }
    
    # Function to calculate days since period start
    def days_since_start(date, start_date):
        return (date.date() - start_date.date()).days
    
    # Add traces for each period
    periods = [
        (f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})', first_period_start, first_period_end),
        (f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})', second_period_start, second_period_end)
    ]
    
    for period_name, start_date, end_date in periods:
        period_data = df[(df.index >= start_date) & (df.index <= end_date)]
        if not period_data.empty:
            # Calculate days since period start
            x_values = [days_since_start(d, start_date) for d in period_data.index]
            
            fig.add_trace(go.Scatter(
                x=x_values,
                y=period_data[('Volume', symbol)],
                name=period_name,
                mode='lines',
                line=dict(color=colors[period_name]),
                hovertemplate='%{text}<br>Volume: %{y:,.0f}<extra></extra>',
                text=[d.strftime('%B %d, %Y') for d in period_data.index],
            ))
    
    # Create month labels for x-axis
    month_ticks = []
    month_labels = []
    if len(periods[0]) > 0:
        current_date = periods[0][1]
        end_date = periods[0][2]
        while current_date <= end_date:
            days = days_since_start(current_date, periods[0][1])
            month_ticks.append(days)
            month_labels.append(current_date.strftime('%B'))
            # Move to next month
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
            current_date = datetime(next_year, next_month, 1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} - Trading Volume Comparison',
        xaxis_title='Days Since Period Start',
        yaxis_title='Volume',
        hovermode='x unified',
        xaxis=dict(
            ticktext=month_labels,
            tickvals=month_ticks,
            tickangle=45,
            showgrid=True,
        ),
        yaxis=dict(
            tickformat=',d',
            showgrid=True,
        ),
        showlegend=True,
        plot_bgcolor='white',
    )
    
    # Save the plot
    fig.write_html(f'{symbol}_volume_comparison.html')
    print(f"Graph has been saved as {symbol}_volume_comparison.html")
    
    # Print date range information
    print("\nData range information:")
    for period_name, start_date, end_date in periods:
        period_data = df[(df.index >= start_date) & (df.index <= end_date)]
        if not period_data.empty:
            print(f"{period_name}: {period_data.index[0]} to {period_data.index[-1]}")

def create_dollar_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end):
    """
    Create dollar volume comparison graph for two specific periods
    """
    # Create figure
    fig = go.Figure()
    
    # Colors from the reference image
    colors = {
        f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})': '#000000',
        f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})': '#40B4A6'
    }
    
    # Function to calculate days since period start
    def days_since_start(date, start_date):
        return (date.date() - start_date.date()).days
    
    # Calculate dollar volume
    dollar_volume = df[('Close', symbol)] * df[('Volume', symbol)]
    df_with_dollar = df.copy()
    df_with_dollar[('DollarVolume', symbol)] = dollar_volume
    
    # Add traces for each period
    periods = [
        (f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})', first_period_start, first_period_end),
        (f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})', second_period_start, second_period_end)
    ]
    
    for period_name, start_date, end_date in periods:
        period_data = df_with_dollar[(df_with_dollar.index >= start_date) & (df_with_dollar.index <= end_date)]
        if not period_data.empty:
            # Calculate days since period start
            x_values = [days_since_start(d, start_date) for d in period_data.index]
            
            fig.add_trace(go.Scatter(
                x=x_values,
                y=period_data[('DollarVolume', symbol)],
                name=period_name,
                mode='lines',
                line=dict(color=colors[period_name]),
                hovertemplate='%{text}<br>Dollar Volume: $%{y:,.2f}<br>Price: $%{customdata[0]:.2f}<br>Volume: %{customdata[1]:,.0f}<extra></extra>',
                text=[d.strftime('%B %d, %Y') for d in period_data.index],
                customdata=list(zip(period_data[('Close', symbol)], period_data[('Volume', symbol)]))
            ))
    
    # Create month labels for x-axis
    month_ticks = []
    month_labels = []
    if len(periods[0]) > 0:
        current_date = periods[0][1]
        end_date = periods[0][2]
        while current_date <= end_date:
            days = days_since_start(current_date, periods[0][1])
            month_ticks.append(days)
            month_labels.append(current_date.strftime('%B'))
            # Move to next month
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
            current_date = datetime(next_year, next_month, 1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} - Trading Dollar Volume Comparison',
        xaxis_title='Days Since Period Start',
        yaxis_title='Dollar Volume ($)',
        hovermode='x unified',
        xaxis=dict(
            ticktext=month_labels,
            tickvals=month_ticks,
            tickangle=45,
            showgrid=True,
        ),
        yaxis=dict(
            tickformat='$,.0f',
            showgrid=True,
        ),
        showlegend=True,
        plot_bgcolor='white',
    )
    
    # Save the plot
    fig.write_html(f'{symbol}_dollar_volume_comparison.html')
    print(f"Dollar volume graph has been saved as {symbol}_dollar_volume_comparison.html")

def create_monthly_dollar_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end):
    """
    Create monthly aggregated dollar volume comparison for two specific periods
    """
    # Calculate dollar volume
    dollar_volume = df[('Close', symbol)] * df[('Volume', symbol)]
    df_with_dollar = df.copy()
    df_with_dollar[('DollarVolume', symbol)] = dollar_volume
    
    # Create monthly aggregation for each period
    periods = [
        (f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})', first_period_start, first_period_end),
        (f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})', second_period_start, second_period_end)
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Colors from the reference image
    colors = {
        f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})': '#000000',
        f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})': '#40B4A6'
    }
    
    for period_name, start_date, end_date in periods:
        period_data = df_with_dollar[(df_with_dollar.index >= start_date) & (df_with_dollar.index <= end_date)]
        if not period_data.empty:
            monthly_data = period_data.groupby([period_data.index.year, period_data.index.month]).agg({('DollarVolume', symbol): 'sum'})
            months = [calendar.month_name[m] for y, m in monthly_data.index]
            
            fig.add_trace(go.Bar(
                x=months,
                y=monthly_data[('DollarVolume', symbol)].values,
                name=period_name,
                marker_color=colors[period_name],
                hovertemplate='%{x}<br>Dollar Volume: $%{y:,.2f}<extra></extra>',
            ))
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} - Monthly Trading Dollar Volume Comparison',
        xaxis_title='Month',
        yaxis_title='Dollar Volume ($)',
        hovermode='x unified',
        barmode='group',
        yaxis=dict(
            tickformat='$,.0f',
            showgrid=True,
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        plot_bgcolor='white',
    )
    
    # Save the plot
    fig.write_html(f'{symbol}_monthly_dollar_volume_comparison.html')
    print(f"Monthly dollar volume graph has been saved as {symbol}_monthly_dollar_volume_comparison.html")

def generate_summary_table(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end):
    """
    Generate summary statistics for two specific periods
    """
    # Calculate dollar volume
    dollar_volume = df[('Close', symbol)] * df[('Volume', symbol)]
    df_with_dollar = df.copy()
    df_with_dollar[('DollarVolume', symbol)] = dollar_volume
    
    periods = [
        (f'Period 1 ({first_period_start.strftime("%Y-%m-%d")} to {first_period_end.strftime("%Y-%m-%d")})', first_period_start, first_period_end),
        (f'Period 2 ({second_period_start.strftime("%Y-%m-%d")} to {second_period_end.strftime("%Y-%m-%d")})', second_period_start, second_period_end)
    ]
    
    # Create period summaries
    period_summary = []
    monthly_summary = []
    
    for period_name, start_date, end_date in periods:
        period_data = df_with_dollar[(df_with_dollar.index >= start_date) & (df_with_dollar.index <= end_date)]
        if not period_data.empty:
            # Period summary
            period_summary.append({
                'Period': period_name,
                'Date Range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'Total Volume': period_data[('Volume', symbol)].sum(),
                'Average Price': period_data[('Close', symbol)].mean(),
                'Total Dollar Volume': period_data[('DollarVolume', symbol)].sum(),
            })
            
            # Monthly data
            monthly_data = period_data.groupby([period_data.index.year, period_data.index.month]).agg({
                ('Volume', symbol): 'sum',
                ('Close', symbol): 'mean',
                ('DollarVolume', symbol): 'sum'
            })
            
            for (year, month), data in monthly_data.iterrows():
                monthly_summary.append({
                    'Period': period_name,
                    'Year': year,
                    'Month': calendar.month_name[month],
                    'Total Volume': data[('Volume', symbol)],
                    'Average Price': data[('Close', symbol)],
                    'Total Dollar Volume': data[('DollarVolume', symbol)],
                })
    
    # Create HTML table
    html_content = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #40B4A6; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .summary-section {{ margin-bottom: 30px; }}
            .section-title {{ color: #000000; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>{symbol} Trading Summary</h1>
        
        <div class="summary-section">
            <h2 class="section-title">Period Summary</h2>
            <table>
                <tr>
                    <th>Period</th>
                    <th>Date Range</th>
                    <th>Total Volume</th>
                    <th>Average Price</th>
                    <th>Total Dollar Volume</th>
                </tr>
    """
    
    for summary in period_summary:
        html_content += f"""
            <tr>
                <td>{summary['Period']}</td>
                <td>{summary['Date Range']}</td>
                <td>{summary['Total Volume']:,.0f}</td>
                <td>${summary['Average Price']:.2f}</td>
                <td>${summary['Total Dollar Volume']:,.2f}</td>
            </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="summary-section">
            <h2 class="section-title">Monthly Breakdown</h2>
            <table>
                <tr>
                    <th>Period</th>
                    <th>Year</th>
                    <th>Month</th>
                    <th>Total Volume</th>
                    <th>Average Price</th>
                    <th>Total Dollar Volume</th>
                </tr>
    """
    
    for summary in monthly_summary:
        html_content += f"""
            <tr>
                <td>{summary['Period']}</td>
                <td>{summary['Year']}</td>
                <td>{summary['Month']}</td>
                <td>{summary['Total Volume']:,.0f}</td>
                <td>${summary['Average Price']:.2f}</td>
                <td>${summary['Total Dollar Volume']:,.2f}</td>
            </tr>
        """
    
    html_content += """
            </table>
        </div>
    </body>
    </html>
    """
    
    # Save to file
    with open(f'{symbol}_trading_summary.html', 'w') as f:
        f.write(html_content)
    
    print(f"Trading summary has been saved as {symbol}_trading_summary.html")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze stock data')
    parser.add_argument('symbol', help='Stock symbol (e.g., AAPL)')
    parser.add_argument('--first-period-start', type=str, help='Start date for first period (YYYY-MM-DD)')
    parser.add_argument('--first-period-end', type=str, help='End date for first period (YYYY-MM-DD)')
    parser.add_argument('--second-period-start', type=str, help='Start date for second period (YYYY-MM-DD)')
    parser.add_argument('--second-period-end', type=str, help='End date for second period (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    symbol = args.symbol
    first_period_start = datetime.strptime(args.first_period_start, '%Y-%m-%d')
    first_period_end = datetime.strptime(args.first_period_end, '%Y-%m-%d')
    second_period_start = datetime.strptime(args.second_period_start, '%Y-%m-%d')
    second_period_end = datetime.strptime(args.second_period_end, '%Y-%m-%d')
    
    # Get the earlier start date and later end date for data fetching
    start_date = min(first_period_start, second_period_start)
    end_date = max(first_period_end, second_period_end)
    
    print(f"\nFetching data for {symbol} from {start_date.date()} to {end_date.date()}...")
    
    # Download the data
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    
    if df is not None and not df.empty:
        print("Data retrieved successfully!")
        print("\nData columns:", df.columns.tolist())
        print("\nFirst few rows of data:")
        print(df.head())
        
        create_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end)
        create_dollar_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end)
        create_monthly_dollar_volume_comparison(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end)
        generate_summary_table(df, symbol, first_period_start, first_period_end, second_period_start, second_period_end)
    else:
        print("No data available for the specified symbol and date range.")

if __name__ == "__main__":
    main()
