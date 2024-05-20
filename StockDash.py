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
    'background-color': '#6495ED',
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
    # 'display': 'flex', 
    # 'justifyContent': 'center'
}           

nsdq = pd.read_csv('data/nasdaq_screener.csv')
nsdq.set_index('Symbol', inplace=True)
options = []

for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})

sidebar = html.Div([
    html.Div([
        html.H5('Change the plots sizes:', 
        style={'paddingRight':'30px', 
               'font_family':'Helvetica Neue',
               'font-size': '14px',
               'font-weight': 'bold'}),
    dcc.Slider(1, 5, 1,
               value=2,
               id='my-slider'),
               ]),
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
                   'height':'100px', # Adjust the height of the dropdown
                   'overflowY': 'auto',
               },  
    )], style={
               'verticalAlign':'top', 
               'font_family': 'Helvetica Neue',
               'font_size': '10px',
               'text_align': 'center',
            #    'overflowY': 'auto',
               'maxHeight': '500px',
               'minHeight': '100px',
               'zIndex': 1000,
               'marginBottom': '20px'
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
    ], style={'marginTop':'20px', 
             'font_family':'Helvetica Neue',
             'flex':1}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':20, 
                   'marginLeft':'100px', 
                   'marginTop':'30px', 
                   'font_family': 'Helvetica Neue',
                   'flex':1}
        ),
    ]),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    html.Div([
        html.H2('Stock Dashboard', style={'backgroundColor':'#1E1E1E', 
                                          'font_family': 'Helvetica Neue',
                                          'color': '#FFFFFF'}),
        dcc.Graph(
        id='my_graph',
        figure={'data': [{'x': [1], 'y': [1]}],
                'layout': go.Layout(template='plotly_dark')
        })
        ], id='scatter_plot', style={'flex':2}),
    html.Div([
        # html.H1('Average Volume', style={'backgroundColor':'#1E1E1E', 
        #                                  'font_family': 'Helvetica Neue',
        #                                  'color': '#FFFFFF'}),
        dcc.Graph(id='my_graph_volume', 
                  figure=go.Figure())], 
                  id= 'pi_plot',
                  style={'flex':1, 
                         'marginTop':'30px', 'marginLeft':'0px'}),
               ], className='body', 
                  style=CONTENT_STYLE)

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
    Output('scatter_plot', 'style'),
    [Input('submit-button', 'n_clicks')],
    [Input('my-slider', 'value')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, step, stock_ticker, start_date, end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')

    fig_close  = go.Figure()
    fig_volume = make_subplots(rows=2, 
                               cols=1,
                               vertical_spacing=0.3,
                               subplot_titles=("Volume Average", "Closing Price Average"),
                               specs=[[{'type':'domain'}], [{'type':'domain'}]])

    labels = []
    vol_values = []
    clo_values = []

    for tic in stock_ticker:
        df = web.get_data_yahoo(tic, start=start, end=end)
        labels.append(tic)
        vol_values.append(round(df.Volume.mean()))
        clo_values.append(round(df.Close.mean()))

        fig_close.add_trace(go.Scatter(x=df.index,
                                       y=df.Close,
                                       mode='lines',
                                       showlegend=True,
                                       name=tic))

    fig_close.update_layout(
        title=', '.join(stock_ticker),
        xaxis_title="Date",
        yaxis_title="Closing Prices",
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(
        family="Helvetica Neue",
        size=15,
        color="#FFFFFF"),
        showlegend=False
    )

    fig_close.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, showgrid=False)
    fig_close.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True, showgrid=False)

    fig_volume.add_trace(go.Pie(labels=labels, 
                                values=vol_values, 
                                hole=.5, 
                                hoverinfo="label+percent+name", 
                                textinfo='value'),1,1)

    fig_volume.add_trace(go.Pie(labels=labels, 
                                values=clo_values, 
                                hole=.5, 
                                hoverinfo="label+percent+name", 
                                textinfo='value'),2,1)

    fig_volume.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(
        family="Helvetica Neue",
        size=15,
        color="#FFFFFF"))

    fig_volume.layout.annotations[0].update(y=1.1,x=1.01)
    fig_volume.layout.annotations[1].update(y=.4,x=1.1)
    fig_volume.update_annotations(font=dict(family="Helvetica Neue", size=15))
    
    print(step)
    return fig_close, fig_volume, {'flex':int(step), 'marginTop':'5px', 'marginRight':'0px'}

if __name__ == '__main__':
    app.run_server(debug=True)