import dash
from dash import dcc,html
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import yfinance as yf
yf.pdr_override()

app = dash.Dash()
# read a .csv file, make a dataframe, and build a list of Dropdown options
nsdq = pd.read_csv('data/nasdaq_screener.csv')
nsdq.set_index('Symbol', inplace=True)
options = []
for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})

light_theme = {
    "main-background": "#ffe7a6",
    "header-text": "#376e00",
    "sub-text": "#0c5703",
}

dark_theme = {
    "main-background": "#000000",
    "header-text": "#ff7575",
    "sub-text": "#ffd175",
}

app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),
    html.Div([
        html.H3('Select stock symbols:', style={'paddingRight':'30px'}),
        # replace dcc.Input with dcc.Options, set options=options
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['TSLA'],
            multi=True
        )
    # widen the Div to fit multiple inputs
    ], style={'display':'inline-block', 
    'verticalAlign':'top', 
    'width':'30%',}),
    html.Div([
        html.H3('Select start and end dates:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':24, 'marginLeft':'30px'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='my_graph',
        figure={
            'data': [
                {'x': [1,2], 'y': [1,2]}
            ]
        }
    )
], style={'backgroundColor':'#1E1E1E', 'color': '#FFFFFF'},)
@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    print('*********************************',start,end)
    # since stock_ticker is now a list of symbols, create a list of traces
    # traces = []
    fig = go.Figure()

    for tic in stock_ticker:
        # df = web.DataReader(tic,'iex',start,end)
        df = web.get_data_yahoo(tic, start=start, end=end)
        fig.add_trace(go.Scatter(
        x=df.index,
        y=df.Close,
        mode='lines',
        showlegend=False
    ))
        # traces.append({'x':df.index, 'y': df.Close, 'name':tic})
    # fig = {
    #     # set data equal to traces
    #     'data': traces,
    #     # use string formatting to include all symbols in the chart title
    #     'layout': {'title':', '.join(stock_ticker)+' Closing Prices', 'template':'plotly_dark'}
    # }
        fig.update_layout(
        title=', '.join(stock_ticker)+' Closing Prices',
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )
    return fig

if __name__ == '__main__':
    app.run_server()