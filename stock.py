# stock.py
# use alpha vantage to get stock prices and plot them

import plotly.graph_objects as go
import requests
from datetime import datetime, date
import math

"""
get_stock_fig: get stock figure for a certain stock
params: 
symbol (str): stock symbol for company
interval (str, default='30min'): time interval for stock prices (available: 1min, 5min, 15min, 30min, 60min)
month (str, default='2024-02'): month of interest
specific_dates_range (pair(str, str), default=None): specific date ranges (format: (yyyy-mm-dd, yyyy-mm-dd))
auto_interval (bool, default=True): auto calculate interval from specific dates
stories (stories, default=True): stories to add to the graph

returns:
fig (plotly.graph_objects.Figure): figure for the graph
"""
def get_stock_fig(symbol, interval='30min', month='2024-2',specific_dates_range=None, auto_interval=True, stories=None):
    
    key = "XHDWCYWJPUFFPBQK"
    if (specific_dates_range):
        start_date_str, end_date_str = specific_dates_range

        # error checking
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            if start_date > end_date:
                raise ValueError("start date is later than end date")
        except ValueError:
            raise ValueError("invalid date format")

        delta_days = (end_date - start_date).days
        delta_months = math.ceil(delta_days/30)
        if delta_months > 13:
            raise ValueError("try a shorter time span")
        if start_date.year < 2000:
            raise ValueError("Stock prices before 2000 is not supported")
        if end_date.date() > date.today():
            raise ValueError("Future stock prices are not supported")
        
        if auto_interval:
            posible_intervals = [1, 5, 15, 30, 60]
            total_datapoints = [delta_days*60*16/i for i in posible_intervals]
            interval = f"{next((interval for interval, data_point in zip(posible_intervals, total_datapoints) if data_point < 1000), posible_intervals[-1])}min"
        
        current_date = start_date
        time_series_data = {}
        while current_date <= end_date:
            month = current_date.strftime('%Y-%m')
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&month={month}&apikey={key}'
            r = requests.get(url)
            data = r.json()
            cur_time_series_data = data[f"Time Series ({interval})"]

            # remove data outside specific time
            try:
                if current_date == start_date or current_date == end_date:
                    keys_to_remove = [key for key in cur_time_series_data.keys() if not start_date <= datetime.strptime(key, '%Y-%m-%d %H:%M:%S') <= end_date]
                    for key in keys_to_remove:
                        del cur_time_series_data[key]
            except:
                pass
            time_series_data.update(cur_time_series_data)

            # loop update
            year = current_date.year + int((current_date.month + 1) / 12)
            month = (current_date.month + 1) % 12 or 12
            current_date = current_date.replace(year=year, month=month)
    else:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&month={month}&apikey={key}'
        r = requests.get(url)
        data = r.json()
        time_series_data = data[f"Time Series ({interval})"]

    dates = [entry for entry in time_series_data.keys()]
    opens = [entry["1. open"] for entry in time_series_data.values()]
    highs = [entry["2. high"] for entry in time_series_data.values()]
    lows = [entry["3. low"] for entry in time_series_data.values()]
    closes = [entry["4. close"] for entry in time_series_data.values()]
    volumes = [entry["5. volume"] for entry in time_series_data.values()]

    candlestick = go.Candlestick(x=dates,
                                open=opens,
                                high=highs,
                                low=lows,
                                close=closes)

    # Layout
    layout = go.Layout(title=symbol,
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Price'))

    # Create figure
    fig = go.Figure(data=[candlestick], layout=layout)

    """if stories:
        for story in stories:
            colour_chosen = ""
            fig.update_layout(
                title=story.headline,
                shapes = [dict(
                    x0='2016-12-09', x1='2016-12-09', y0=0, y1=1, xref='x', yref='paper',
                    line_width=2)],
                annotations=[dict(
                    x='2016-12-09', y=0.05, xref='x', yref='paper',
                    showarrow=False, xanchor='left', text=story.headline)]
            )"""

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]), #hide weekends
            dict(bounds=[20, 4], pattern="hour"), # hide hours outside trading
        ]
    )

    return fig

def show_fig(company, stories=None, start_date="2022-01-01", end_date="2022-03-4"):
    symbol = company.stock_symb
    fig = get_stock_fig(symbol, specific_dates_range=(start_date, end_date), stories=stories)
    fig.show()

if __name__ == "__main__":
    
    symbol = "AAPL"
    start_date = "2022-01-01"
    end_date = "2022-03-4"
    fig = get_stock_fig(symbol, specific_dates_range=(start_date, end_date))
    fig.show()
    