import dash.html as html
import dash.dcc as dcc
from dash import dash_table
import dash_bootstrap_components as dbc
from .data import  student_list, upcoming_deadlines
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart

# HEADER
title = html.H1(
    'Synced Support',
    style={
        'backgroundColor': '#437DC2',
        'color': 'white',
        'font-size': '20px',
        'margin' : '0',
        'padding': '15px'}
)

info_button = dbc.Button(
    "Learn More!",
    id="info-button",
    outline=False,
    style={
        'width': '100px',
        'background-color': 'black',
        'color': 'white'}
)

# MAIN CONTENT 
def create_tabs():
    return dcc.Tabs(id='tabs', value='student-tab', children=[
        dcc.Tab(label='Student View', value='student-tab'),
        dcc.Tab(label='Task View', value='task-tab')
    ])

# Default Values - student tab
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

# Default values - task tab 
default_student_tasks = [{'Due': None, 'Task': None, 'Course': None, 'Teacher': None, 'Block': None }]


# Student Tab 
student_tab = html.Div([
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
                            style_cell={'textAlign':'left'}, 
                            style_header={'fontWeight': 'bold'}
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

# Task Tab 
task_tab = html.Div([
    html.Div([
        # COLUMN 1 
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
                    data=upcoming_deadlines(), 
                    style_cell={'textAlign':'center'}, 
                    style_header={'fontWeight': 'bold'}, 
                )
            ])
        ], style={'flex': '1', 'padding': '10px'}
        ),
             
        # COLUMN 2
        html.Div([
            html.Div(id={'type': 'dynamic-input', 'index': 'dynamic-t2-col2'})
        ], style={'flex': '3', 'padding': '10px'}        
        )
        
    ], style={'display': 'flex', 'gap': '10px', 'align-items': 'flex-start', 'paddingTop':'25px'}
    )
    ])

# User input - attendance/workhabit
# user input - tasks enter/remove

# FOOTER
footer =  html.H3(
    '<enter info> ',
    style={
        'backgroundColor': '#437DC2',
        'color': 'white',
        'font-size': '15px',
        'margin' : '0',
        'align-text': 'center',
        'padding': '15px'}, 
)

