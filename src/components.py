import dash.html as html
import dash.dcc as dcc

def create_tabs():
    return dcc.Tabs(id='tabs', value='student-tab', children=[
        dcc.Tab(label='Student View', value='student-tab'),
        dcc.Tab(label='Teacher View', value='teacher-tab')
    ])

