import dash
from dash import dcc,html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd
import yfinance as yf
yf.pdr_override()
import plotly.io as pio

# Set the plotly template to 'plotly_dark'
pio.templates.default = "plotly_dark"

# app = dash.Dash()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], suppress_callback_exceptions=True)

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20rem',
    'padding': '2rem 1rem',
    'background-color': '#DA70D6',
    'font_family': 'Helvetica Neue',
    'overflowY': 'auto',
}

CONTENT_STYLE = {
    'margin-left': '20rem',
    'margin-right': '0rem',
    'margin-bottom': '0rem',
    'padding': '2rem 1rem',
    'backgroundColor':'#1E1E1E', 
    'font_family': 'Helvetica Neue',
    'color': '#FFFFFF',
}

style_cell = {
    'font_family': 'Helvetica Neue',
    'font_size': '5px',
    'text_align': 'center'
}

light_theme = {
    'main-background': '#ffe7a6',
    'header-text': '#376e00',
    'sub-text': '#0c5703',
}

dark_theme = {
    'main-background': '#000000',
    'header-text': '#ff7575',
    'sub-text': '#ffd175',
}            

nsdq = pd.read_csv('data/nasdaq_screener.csv')
nsdq.set_index('Symbol', inplace=True)
options = []

for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})

sidebar = html.Div([
    html.Div([
        html.H5('Select stock symbols:', 
        style={'paddingRight':'30px', 
               'font_family':'Helvetica Neue',
               'font-size': '14px',
               'font-weight': 'bold'}),
        # replace dcc.Input with dcc.Options, set options=options
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['TSLA'],
            multi=True,
            style={'font-family': 'Helvetica Neue',
                   'font-size': '14px',  # Adjust the font size as needed
                   'margin-bottom': '10px',  # Adjust the space between options
                   'width': '285px', # Adjust the width of the dropdown
                   'height':'30px'
               },  
    )], style={'display':'inline-block', 
               'verticalAlign':'top', 
               'font_family': 'Helvetica Neue',
               'font_size': '10px',
               'text_align': 'center'
    }),

    html.Div([
        html.H5('Select start and end dates:', 
        style={'paddingRight':'30px', 
               'font_family': 'Helvetica Neue',
               'font-size': '14px', 
               'display':'inline-block',
               'font-weight': 'bold'}),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today(),
            className='datepicker-range',
            style={'fontSize':5,'display':'inline-block'}
        )
    ],style={'marginTop':'20px', 
             'font_family':'Helvetica Neue',}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':20, 
                   'marginLeft':'100px', 
                   'marginTop':'30px', 
                   'font_family': 'Helvetica Neue',}
        ),
    ]),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    html.Div([
        html.H1('Stock Dashboard', style={'backgroundColor':'#1E1E1E', 
                                                'font_family': 'Helvetica Neue',
                                                'color': '#FFFFFF'}),
        dcc.Graph(
        id='my_graph',
        figure={'data': [{'x': [1], 'y': [1]}],
                'layout': go.Layout(template='plotly_dark')
        })]),
    html.Div([
        # html.H1('Average Volume', style={'backgroundColor':'#1E1E1E', 
        #                                  'font_family': 'Helvetica Neue',
        #                                  'color': '#FFFFFF'}),
        dcc.Graph(id='my_graph_volume', 
        figure=go.Figure())]),
            ], style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id='url'), sidebar, content])
# app.layout = html.Div([
#     dbc.Row([
#         dbc.Col(sidebar, width=3),
#         dbc.Col(maindiv, width=9)
#     ])
# ])

@app.callback(
    Output('my_graph', 'figure'),
    Output('my_graph_volume', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    print('*********************************',start,end)

    fig_close  = go.Figure()
    # fig_volume = go.Figure()
    fig_volume = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

    labels = []
    vol_values = []
    clo_values = []
    
    for tic in stock_ticker:
        df = web.get_data_yahoo(tic, start=start, end=end)
        labels.append(tic)
        vol_values.append(df.Volume.mean())
        clo_values.append(df.Close.mean())

        fig_close.add_trace(go.Scatter(
        x=df.index,
        y=df.Close,
        mode='lines',
        showlegend=False
    ))

    fig_close.update_layout(
        title=', '.join(stock_ticker)+' Closing Prices',
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF')
    )

    fig_volume.add_trace(go.Pie(labels=labels, values=vol_values, 
    hole=.5, hoverinfo="label+percent+name", name='Volume Average'),1,1)
    fig_volume.add_trace(go.Pie(labels=labels, values=clo_values, 
    hole=.5, hoverinfo="label+percent+name", name='Closing Price Average'),1,2)

    # fig_volume.add_trace(go.Pie(labels=labels, values=values, hole=.5))

    fig_volume.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'))

    return fig_close, fig_volume

if __name__ == '__main__':
    app.run_server()