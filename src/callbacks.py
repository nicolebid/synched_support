from dash.dependencies import Input, Output, State
from dash import dash_table
import dash.html as html
import dash.dcc as dcc
from .data import student_list, student_schedule, teacher_list, course_list, deadlines
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart
import datetime

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
default_deadlines = [{'Task': None, 'Course':None, 'Teacher': None, 'Block': None, 'Due': None}]

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
                    # TAB 1 - COLUMN 1 
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

                # TAB 1 - COLUMN 2
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
                html.Div([
                    # TAB 2 - COLUMN 1
                    html.Div([
                        html.H3("Column 1"),   
                        # Teacher/Course Selection
                        dcc.Dropdown(
                            id={'type': 'dynamic-input', 'index': 'select-type'},
                            options=[
                                {'label': 'Teacher', 'value': 'Teacher'},
                                {'label': 'Course', 'value': 'Course'}
                            ],
                            placeholder='Select by...'
                        ),
                        dcc.Dropdown(
                            id={'type': 'dynamic-input', 'index': 'select-item'}, 
                            placeholder='Select item'
                        ),
                        # Upcoming Deadlines
                        html.Div([
                        html.H4("Upcoming Deadlines"),
                        dash_table.DataTable(
                            id={'type': 'dynamic-output', 'index': 'deadlines-table'},
                            columns=[
                                {'name': 'Task', 'id': 'Task'},
                                {'name': 'Course', 'id': 'Course'},
                                {'name': 'Block', 'id': 'Block'},
                                {'name': 'Teacher', 'id': 'Teacher'},
                                {'name': 'Due', 'id': 'Due'}      
                            ],
                            data=default_deadlines, 
                            row_selectable = 'multi', 
                            selected_rows = []
                        )
                    ])


                    ], style={'width': '25%', 'display': 'inline-block', 'padding-right':'20px'} ),
                    
                    # TAB 2 - COLUMN 2
                    html.Div([
                            html.H3("Column 2"),  

                    ], style={'width': '50%', 'display': 'inline-block', 'padding-left':'20px'}),
                ])  
            ])

    # TAB 1 - UPDATES 
    # Update student selected when the submit button is clicked
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
    
    # TAB 2 - UPDATES
    # Update 2nd Dropdown when first dropdown is selected
    @app.callback(
        Output({'type': 'dynamic-input', 'index': 'select-item'}, 'options'),
        Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value')
    )
    def update_dropdown(selected_type=None):
        if selected_type == 'Teacher':
            options = teacher_list()
        elif selected_type == 'Course':
            options = course_list()
        else:
            options = []
        return options
    
    # Update the deadlines table when second dropdown is selected
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'deadlines-table'}, 'data'), 
        Output({'type': 'dynamic-output', 'index': 'deadlines-table'}, 'columns'),
        [Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value'), 
        Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value')]
    )
    def update_deadlines(selected_item, selected_type):
        if selected_type == 'Teacher' and selected_item is not None:
            columns = [{'name': 'Course', 'id': 'Course'},
                    {'name': 'Task', 'id': 'Task'}, 
                    {'name': 'Block', 'id': 'Block'}, 
                    {'name': 'Due', 'id': 'Due'}]
            data = deadlines(teacher_name=selected_item)
        elif selected_type == 'Course' and selected_item is not None: 
            columns = [{'name': 'Teacher', 'id': 'Teacher'}, 
                    {'name': 'Task', 'id': 'Task'},
                    {'name': 'Block', 'id': 'Block'}, 
                    {'name': 'Due', 'id': 'Due'}]
            data = deadlines(course_name=selected_item)
        else:
            columns = [{'name': 'Task', 'id': 'Task'},
                    {'name': 'Course', 'id': 'Course'},
                    {'name': 'Teacher', 'id': 'Teacher'},
                    {'name': 'Block', 'id': 'Block'},
                    {'name': 'Due', 'id': 'Due'}]
            data = default_deadlines
        
        return data, columns


