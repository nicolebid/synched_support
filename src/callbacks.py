from dash.dependencies import Input, Output, State
import dash.html as html
import dash.dcc as dcc
from .data import student_list, student_schedule
from dash import dash_table

def register_callbacks(app):
    # Callback for active tab
    @app.callback(
        Output('tab-content', 'children'),
        [Input('tabs', 'value')]
    )
    def render_content(tab):
        if tab == 'student-tab':
            return html.Div([
                html.Div([
                    html.H3('Column 1'),

                    # Student Selection
                    html.Label('Select Student'),
                    dcc.Dropdown(
                        id={'type': 'dynamic-input', 'index': 'student-select'},
                        options=student_list(), # students names from dataset 
                        value='A'  # Default value
                    ),
                    html.Button('Submit', id={'type': 'dynamic-input', 'index': 'submit-student'}, n_clicks=0),
                    
                    # Student Schedule 
                    html.Div([
                        html.H4("Student Schedule"),
                        dash_table.DataTable(
                            id={'type': 'dynamic-output', 'index': 'course-table'},
                            columns=[
                                {'name': 'Block', 'id': 'Block'},
                                {'name': 'Course', 'id': 'Course'},
                                {'name': 'Teacher', 'id': 'Teacher'}
                                
                            ],
                            data=[]
                        )
                    ])
                ], style={'width': '25%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.H3('Column 2'),
                    html.Div(id={'type': 'dynamic-output', 'index': 'output-text'})
                ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'})
            ], style={'display': 'flex', 'justify-content': 'space-between'})

        elif tab == 'teacher-tab':
            return html.Div([
                html.H3('Teacher View Content'),
                html.P('This is the content specifically for the Teacher View. Add your components here.')
            ])

    # Callback to update the output when the submit button is clicked
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'output-text'}, 'children'),
        [Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')], 
        [State({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_output(n_clicks, selected_student):
        # updates on button click 
        if n_clicks > 0:
            return f'Student: {selected_student}'
        return 'Student:'
    

    # Callback to update the course table when the submit button is clicked
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'course-table'}, 'data'), 
        [Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')],  
        [State({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_schedule(n_clicks, selected_student):
        # Check if n_clicks is None or 0
        if n_clicks is None or n_clicks == 0:
            return [] 
        schedule = student_schedule(selected_student)
        return schedule 
     