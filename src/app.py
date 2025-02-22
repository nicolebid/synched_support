import dash as d
import dash.html as html
import dash.dcc as dcc
import dash_bootstrap_components as dbc
from dash import Dash
from dash.dependencies import Input, Output
from .components import *
from .callbacks import * 

# Initialize app 
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], title="Synced Support")
server = app.server

# App Layout
app.layout = dbc.Container([
    
    # Header
    dbc.Row([ 
        dbc.Col(title), dbc.Col(html.Div(info_button), 
                                className="text-right", 
                                width="auto", 
                                style={'background-color': '#387c9f', 
                                       'padding-right': '12px',
                                       'padding-top': '12px',                                                                                     
                                       'padding-bottom': '12px'})
        ], style={'flex': '0 0 auto', 'width': '100vw', 'margin': 0, 'padding': 0, 'background-color': '#387c9f' }),

    # Main Content
    dbc.Row([
        html.Div([
            create_tabs(), 
            html.Div(id='tab-content', style={'flex': '1', 'overflow': 'auto'})
        ], style={ 'display': 'flex', 'flex-direction': 'column', 
                    'height': 'calc(100vh - 65px - 30px)',  #pg - header - footer
                    'width': '100%'
            }
        ),
    ],  style={'flex': '1', 'width': '100%', 'margin': 0, 'padding': 0
               }), 
    
    # Footer
    dbc.Row([footer], 
            style={ 'position': 'fixed',  
                    'bottom': '0',
                    'width': '100vw',
                    'height': '30px',  
                    'background-color': '#387c9f',
                    'padding': '0px',
                    'flex': '0 0 auto',
                    'align-text': 'center',
                    'margin': 0  }), 
    ], 
    fluid=True,   
    style={'display': 'flex', 'flex-direction': 'column', 'height': '100vh', 'margin': 0, 'padding': 0
           })

# register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
