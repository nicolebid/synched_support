from dash.dependencies import Input, Output, State
from dash import dash_table
import dash.html as html
import dash.dcc as dcc
from .data import student_list, student_schedule
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart

from dash import callback_context

# Default Values
default_schedule = [{'Block': '1-1', 'Course': None, 'Teacher': None},
                    {'Block': '1-2', 'Course': None, 'Teacher': None},
                    {'Block': '1-3', 'Course': None, 'Teacher': None},
                    {'Block': '1-4', 'Course': None, 'Teacher': None},
                    {'Block': '2-1', 'Course': None, 'Teacher': None},
                    {'Block': '2-2', 'Course': None, 'Teacher': None},
                    {'Block': '2-3', 'Course': None, 'Teacher': None},
                    {'Block': '2-4', 'Course': None, 'Teacher': None}]
initial_attendance_graph = attendance_barchart()  
initial_workhabit_graph = workhabit_timeline()
initial_timespent_graph = timespent_barchart()

# MAIN CONTENT LAYOUT
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
                    # Tab 1 - Column 1
                    html.H3('Column 1'),

                    # Student Selection
                    html.Label('Select Student'),
                    dcc.Dropdown(
                        id={'type': 'dynamic-input', 'index': 'student-select'},
                        options=student_list(), 
                        value='A' 
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
                            data=default_schedule
                        )
                    ]), 
                    # Attendance Bar Chart 
                    html.Div([
                        html.H4("Student Attendance"),
                        dcc.Graph(
                            id={'type': 'dynamic-output', 'index': 'attendance-graph'},
                            figure=initial_attendance_graph,
                            config={'displayModeBar': False} 
                        )
                    ])
                ], style={'flex': '1', 'padding': '10px'}),  

                # Tab 1 - Column 2
                html.Div([
                    html.H3('Column 2'),
                    html.Div(id={'type': 'dynamic-output', 'index': 'output-text'}),   
                    html.Div([
                        dcc.RadioItems(
                            id={'type': 'dynamic-input', 'index': 'graph-toggle'},
                            options=[
                                {'label': 'Work Habit Timeline', 'value': 'timeline'},
                                {'label': 'Time Spent Bar Chart', 'value': 'barchart'}
                            ],
                            value='timeline', 
                            labelStyle={'display':'inline-block'}
                        ),
                        dcc.Graph(
                            id={'type': 'dynamic-output', 'index': 'graph-output'},
                            config={'displayModeBar':False}
                        )
                    ], style={'padding':'10px'}
                    ),                    
                ], style={'flex': '2', 'padding': '10px'})  
                
            ], style={'display': 'flex', 'justify-content': 'space-between'}) 

        elif tab == 'teacher-tab':
            return html.Div([
                html.H3('Teacher View Content'),
                html.P('This is the content specifically for the Teacher View. Add your components here.')
            ]) 

    # COMPONENT UPDATES 
    # Update the output when the submit button is clicked
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'output-text'}, 'children'),
        [Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')], 
        [State({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_output(n_clicks, selected_student):
        if n_clicks > 0:
            return f'Student: {selected_student}'
        return 'Student:'
    
    # Update the course table when the submit button is clicked
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'course-table'}, 'data'), 
        [Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')],  
        [State({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_schedule(n_clicks, selected_student):
        # Display default data when the app loads or if no button has been clicked
        if n_clicks == 0 or selected_student == None:
            return default_schedule 
        return student_schedule(selected_student)

    # Update the attendance graph when submit button is clicked
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'attendance-graph'}, 'figure'), 
        [Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')],  
        [State({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_attendance_bar_chart(n_clicks, selected_student):
        if n_clicks == 0 or not selected_student:
            return attendance_barchart() 
        return attendance_barchart(selected_student)
        
    # Update the timeline/barchart graphs 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'graph-output'}, 'figure'),
        [Input({'type': 'dynamic-input', 'index': 'graph-toggle'}, 'value'),
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value'),
        Input({'type': 'dynamic-input', 'index': 'submit-student'}, 'n_clicks')]  
    )
    def update_graph(selected_graph, selected_student, n_clicks):
        if n_clicks == 0 or not selected_student:
            if selected_graph == 'timeline':
                figure = workhabit_timeline()  
            else:
                figure = timespent_barchart()  
        else:
            # Update graph based on selected student
            if selected_graph == 'timeline':
                figure = workhabit_timeline(selected_student)
            elif selected_graph == 'barchart':
                figure = timespent_barchart(selected_student)
        return figure