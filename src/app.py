import dash as d
import dash.html as html
import dash.dcc as dcc
from dash.dependencies import Input, Output
from .components import *
from .callbacks import * 

# Initialize app 
app = d.Dash(__name__)

# Define layout
app.layout = html.Div([
    create_tabs(), 
    html.Div(id='tab-content')
])

# register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)