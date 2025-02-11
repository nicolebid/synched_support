import dash as d
import dash.html as html
import dash.dcc as dcc
import dash_bootstrap_components as dbc
from dash import Dash
from dash.dependencies import Input, Output
from .components import *
from .callbacks import * 


# Initialize app 
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title="Synced Support")
server = app.server

# Define layout
app.layout = dbc.Container([
    dbc.Row([ 
        dbc.Col(title), dbc.Col(html.Div(info_button), 
                                className="text-right", 
                                width="auto", 
                                style={'background-color': 'transparent', 
                                       'padding-right': '24px',
                                       'padding-top': '12px',                                                                                     
                                        'padding-bottom': '12px'})
                ]            
    ), 
    dbc.Row([
        html.Div([
            create_tabs(), 
            html.Div(id='tab-content')
        ]), 
    dbc.Row([footer])
    ])
], 
    fluid=True,
    style={'margin': 0, 'padding': 0}
)

# register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
