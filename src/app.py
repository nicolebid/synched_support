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
        dbc.Col(title, 
                style={'background-color': '#387c9f', 'display': 'flex', 'align-items': 'center'}),
        dbc.Col(
            html.Div(info_button), 
                className="text-right", 
                width="auto", 
                style={
                    'background-color': '#387c9f', 
                    'display': 'flex', 
                    'align-items': 'center'
                }
        ), 
        info_section
    ], style={
            'flex': '0 0 auto', 
            'height':'2.8rem', 
            'width': '100%', 
            'margin': '0px', 
            'padding': '0px', 
            'background-color': '#387c9f'
        
        }
    ),
    # Main Content
    dbc.Row([
        html.Div([
            create_tabs(), 
            html.Div(id='tab-content', style={'flex': '1', 'overflow': 'auto'})
        ], style={
                'display': 'flex', 
                'flex-direction': 'column', 
                'width': '100%'
            }
        ),
    ],  style={'flex': '1', 'width': '100%', 'margin': 0, 'padding': 0
               }), 
    
    # Footer
    dbc.Row([footer], 
            style={ 'position': 'fixed',  
                    'bottom': '0',
                    'width': '100%',
                    'background-color': '#387c9f',
                    'height':'5%',
                    'padding': '0px',
                    'flex': '0 0 auto',
                    'align-text': 'center',
                    'margin': 0  }), 
    ], 
    fluid=True,   
    style={'display': 'flex', 'flex-direction': 'column', 'height': '100%', 'margin': 0, 'padding': 0
           })

# register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
