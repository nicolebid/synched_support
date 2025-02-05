from dash.dependencies import Input, Output, State
from dash import dash_table
import dash.html as html
import dash.dcc as dcc
from .data import student_list, student_schedule, teacher_list, course_list, deadlines, master_deadlines, upcoming_deadlines, student_deadlines, teacher_roster, teacher_tasks
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart, attendance_barchart_none
import datetime

from dash import callback_context

# DEFAULT VALUES 
# Tab 1
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

# Tab 2
default_student_tasks = [{'Due': None, 'Task': None, 'Course': None, 'Teacher': None, 'Block': None }]


# static components
upcoming = upcoming_deadlines()

# master table
#data, column_names = master_deadlines()

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
                    # Student Selection
                    dcc.Dropdown(
                        id={'type': 'dynamic-input', 'index': 'student-select'},
                        options=student_list(), 
                        value='A', 
                         placeholder='Select Student...' 
                    ),                    
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
                            data=default_schedule, 
                            style_cell={'textAlign':'left'}
                        )
                    ]), 
                    # Attendance Bar Chart 
                    html.Div([
                        html.Div([
                            html.H4("Student Attendance", style={'margin-right': '50px'}),
                            dcc.RadioItems(
                                id={'type': 'dynamic-input', 'index': 'attendance-toggle'},
                                options=[
                                    {'label': 'Overall', 'value': 'overall-attend'},
                                    {'label': 'Course Specific', 'value': 'course-attend'}
                                ],
                                value='overall-attend', 
                                labelStyle={'display':'inline-block'}
                            )
                        ], style={'display': 'flex', 'align-items': 'center'}), 
                        dcc.Graph(
                            id={'type': 'dynamic-output', 'index': 'attendance-graph'},
                            figure=initial_attendance_graph,
                            config={'displayModeBar': False} 
                        )
                    ])
                ], style={'flex': '1', 'padding': '10px', 'minWidth': '100px'}),  

                # TAB 1 - COLUMN 2
                html.Div([
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
                ], style={'flex': '2', 'padding': '10px', 'minWidth': '600px'})  
                
            ], style={'display': 'flex', 'justify-content': 'space-between', 'paddingTop':'25px'}) 

        elif tab == 'teacher-tab':
            return html.Div([
    html.Div([
        # TAB 2 - COLUMN 1
        html.Div([
            # Teacher/Course Selection
            dcc.Dropdown(
                id={'type': 'dynamic-input', 'index': 'select-type'},
                options=[
                    {'label': 'Student', 'value': 'Student'},
                    {'label': 'Teacher', 'value': 'Teacher'}
                ],
                placeholder='Select a Student or Teacher...', 
            ),
            dcc.Dropdown(
                id={'type': 'dynamic-input', 'index': 'select-item'}, 
                placeholder='Select Item'
            ),
            # Upcoming Deadlines
            html.Div([
                html.H4("Upcoming Deadlines"),
                dash_table.DataTable(
                    id={'type': 'dynamic-output', 'index': 'deadlines-table'},
                    columns=[
                        {'name': 'Due', 'id': 'Due'}, 
                        {'name': 'Task', 'id': 'Task'},  
                        {'name': 'Course', 'id': 'Course'}, 
                        {'name': 'Teacher', 'id': 'Teacher'},
                        {'name': 'Block', 'id': 'Block'}
                    ],
                    data=upcoming, 
                    style_cell={'textAlign':'center'}, 
                )
            ])
        ], style={'flex': '1', 'padding': '10px'}
        ),
             
        # TAB 2 - COLUMN 2
        html.Div([
            html.Div(id={'type': 'dynamic-input', 'index': 'dynamic-t2-col2'})
        ], style={'flex': '3', 'padding': '10px'}        
        )
        
    ], style={'display': 'flex', 'gap': '10px', 'align-items': 'flex-start', 'paddingTop':'25px'}
    )
    ])

    # TAB 1 - UPDATES 
    # Update the course table when the student is selected 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'course-table'}, 'data'), 
        [Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')] 
    )
    def update_schedule(selected_student):
        if selected_student:
            return student_schedule(selected_student)
        return default_schedule

    # Update the attendance graph based on student and graph type 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'attendance-graph'}, 'figure'), 
        [Input({'type': 'dynamic-input', 'index': 'attendance-toggle'}, 'value'),
         Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_attendance_bar_chart(selected_graph, selected_student):
        if not selected_student:
            return attendance_barchart()
        if selected_graph == 'overall-attend':
            return attendance_barchart(selected_student, True)
        elif selected_graph == 'course-attend':
            return attendance_barchart(selected_student, False)
        return attendance_barchart()
        
    # Update the timeline/barchart graph based on student and graph type 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'graph-output'}, 'figure'),
        [Input({'type': 'dynamic-input', 'index': 'graph-toggle'}, 'value'),
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')], 
    )
    def update_graph(selected_graph, selected_student):
        if selected_student:
            if selected_graph == 'timeline':
                return workhabit_timeline(selected_student)  
            else:
                return timespent_barchart(selected_student)  
        else:
            # return default graphs 
            if selected_graph == 'timeline':
                return workhabit_timeline(selected_student)
            else:
                return timespent_barchart(selected_student)
    
    # TAB 2 - UPDATES
    # Update 2nd Dropdown when first dropdown is selected
    @app.callback(
        [Output({'type': 'dynamic-input', 'index': 'select-item'}, 'options'),
         Output({'type': 'dynamic-input', 'index': 'select-item'}, 'placeholder')],
        Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value')
    )
    def update_dropdown(selected_type=None):
        if selected_type == 'Teacher':
            options = teacher_list()
            placeholder = "Select a teacher"
        elif selected_type == 'Student':
            options = student_list()
            placeholder = "Select a student"
        else:
            options = []
            placeholder = ""
        return options, placeholder
    
    # Tab 2 - Col 2 task tables 
    @app.callback(
        Output({'type': 'dynamic-input', 'index': 'dynamic-t2-col2'}, 'children'), 
        [Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value'), 
         Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value')]
    )
    def update_content_t2col2(role, name):

        if role == 'Student' and name:
            return html.Div([
                html.H3(f'{name} - Tasks'),
                dash_table.DataTable(
                    id={'type':'dynamic-input', 'index':'student-task-table'}, 
                    columns=[{'name':'Due', 'id':'Due'}, 
                             {'name':'Task', 'id':'Task'}, 
                             {'name':'Course', 'id':'Course'}, 
                             {'name':'Teacher', 'id':'Teacher'}, 
                             {'name':'Block', 'id':'Block'}], 
                    data=student_deadlines(name),
                    style_cell={'textAlign':'center'},
                    editable=True
                )
            ])
        elif role == 'Teacher' and name: 
            teacher_roster_dict = teacher_roster(name)
            teacher_task_dict = teacher_tasks(name)
            return html.Div([
            html.H3(f'{name} - Assigned Tasks'), 
            dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in teacher_roster_dict.keys()], 
                data=[{col: '\n'.join(map(str, students)) for col, students in teacher_roster_dict.items()}, 
                      {col: '\n'.join(map(str, students)) for col, students in teacher_task_dict.items()}],
                style_cell={'padding': '10px', 'textAlign': 'center'},
                style_data={'whiteSpace': 'pre-line'},
                style_header={'fontWeight': 'bold'}
            )
            ])
        else:
            return html.Div([
                html.H3('Select a Student or Teacher')
            ])
