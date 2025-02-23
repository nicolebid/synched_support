import dash.html as html
import dash.dcc as dcc
import dash_bootstrap_components as dbc
import datetime
import pandas as pd 
from collections import OrderedDict
from dash import dash_table
from .data import  student_list, upcoming_deadlines
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart

# HEADER
title = html.H1(
    'Synced Support',
    style={
        'background-color': '#387c9f',
        'color': 'white',
        'font-size': '26px',
        'margin' : '0px',
        'padding': '20px'}
)

info_button = dbc.Button(
    "About",
    id={'type': 'button', 'index': 'open-modal'},
    outline=True,
    n_clicks=0,
    style={'background-color': '#387c9f', 'color': 'white', 'border-radius': '20px', 'font-size': '18px'}
)

info_section = dbc.Modal([
        dbc.ModalHeader("About This App", close_button=True),  # Built-in close button
        dbc.ModalBody("This is an app that tracks student work habits and progress."),
    ],
    id={'type': 'dynamic-output', 'index': 'about-modal'},
    is_open=False,
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

# User input options
workhabit_options = OrderedDict([
    ('Student', ['Alice', 'Bob', 'Charlie']),
    ('Workhabit Score', [0, 1, 2, 3]),
    ('Worked On', ['Art', 'English', 'French', 'Math', 'Science', 'Socials', 'Other']), 
    ('Support Attendance', ['P', 'L', 'AE','A'])
])

# Default values - task tab 
default_student_tasks = [{'Due': None, 'Task': None, 'Course': None, 'Teacher': None, 'Block': None }]

# Student Tab 
student_tab = dbc.Row([
                dbc.Col([
                    # COLUMN 1 
                    # Student Selection
                    dcc.Dropdown(
                        id={'type': 'dynamic-input', 'index': 'student-select'},
                        options=student_list(), 
                        value='A', 
                        placeholder='Select Student...', 
                        style={'marginBottom': '30px'} 
                    ),                    
                    # User Input - Student Workhabits
                    html.Div([
                        html.H3("Enter Daily Workhabits", style={'marginBottom':'10px'}),

                        # Date 
                        html.Label("Date", style={'marginRight': '15px'}),
                        dcc.DatePickerSingle(id="date-picker", placeholder="Select date", date=datetime.date.today(), style={'marginBottom':'10px'}),
                        
                        # input table
                        dash_table.DataTable(
                            id={'type': 'user-input', 'index': 'workhabit-table'},
                            data=[{'Student': "", 'Workhabit Score': "", 'Worked On': "", 'Support Attendance':""}], 
                            columns=[
                                {'id': 'Student', 'name': 'Student', 'presentation': 'dropdown'},
                                {'id': 'Workhabit Score', 'name': 'Workhabit Score', 'presentation':'dropdown'},
                                {'id': 'Worked On', 'name': 'Worked On', 'presentation': 'dropdown'},
                                {'id': 'Support Attendance', 'name': 'Support Attendance', 'presentation': 'dropdown'}
                            ],
                            editable=True,
                            row_deletable=True,
                            dropdown={
                                'Student': {'options': [{'label': i, 'value': i} for i in workhabit_options['Student']]},
                                'Workhabit Score': {'options': [{'label': str(i), 'value': str(i)} for i in workhabit_options['Workhabit Score']]},
                                'Worked On': {'options': [{'label': i, 'value': i} for i in workhabit_options['Worked On']]},
                                'Support Attendance': {'options': [{'label': i, 'value': i} for i in workhabit_options['Support Attendance']]}
                            }, 
                            style_cell={'textAlign':'left', 'overflow':'visible'}, 
                            style_header={'white-space': 'normal', 'word-wrap': 'break-word','text-align': 'center', 'fontWeight': 'bold'}
                        ),
                                
                    # Buttons for adding rows/submitting data
                    html.Button("Add Row", id={'type': 'dynamic-input', 'index': 'add-row-btn'}, n_clicks=0),
                    html.Button("Submit", id="submit-btn", n_clicks=0, style={"margin-left": "10px"}),

                    # Output message
                    html.Div(id="output-msg", style={"margin-top": "10px"})
                ])            
            ], width=3), 

                # COLUMN 2 
                dbc.Col([

                    # Student Schedule 
                    html.Div([
                        html.H5("Schedule"),
                        dash_table.DataTable(
                            id={'type': 'dynamic-output', 'index': 'course-table'},
                            columns=[
                                {'name': 'Block', 'id': 'Block'},
                                {'name': 'Course', 'id': 'Course'},
                                {'name': 'Teacher', 'id': 'Teacher'}       
                            ],
                            data=default_schedule, 
                            style_cell={'textAlign':'left'}, 
                            style_header={'fontWeight': 'bold'}, 
                        )
                    ], style={
                        'border': '2px solid #387c9f',
                        'border-radius': '8px', 
                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                        'padding':'10px', 
                        'marginBottom': '20px' 
                        }
                    ), 

                    # Attendance Bar Chart 
                    html.Div([
                        html.Div([
                            html.H5("Attendance", style={'margin-right': '50px'}),
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
                    ], style={'border': '2px solid #387c9f',
                          'border-radius': '8px', 
                          'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                          'padding':'10px'}),                         
                ], width=4),  

                dbc.Col([
                    # Workhabits Graphs 
                    html.Div([
                        html.H5("Study Habits", style={'margin-right': '50px'}),
                        dcc.RadioItems(
                            id={'type': 'dynamic-input', 'index': 'graph-toggle'},
                            options=[
                                {'label': ' Work Habit Timeline', 'value': 'timeline'},
                                {'label': ' Time Spent Bar Chart', 'value': 'barchart'}
                            ],
                            value='timeline', 
                            labelStyle={'display':'inline-block', 'padding': '10px'}
                        ),
                        dcc.Graph(
                            id={'type': 'dynamic-output', 'index': 'graph-output'},
                            config={'displayModeBar':False}
                        )
                    ], style={'padding':'10px', 'border': '2px solid #387c9f',
                        'border-radius': '8px', 
                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                        'padding':'10px' }
                    ),             

                ], width=5)
            ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap', 'paddingTop':'20px', 'max-width': '100%'}
            ) 

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
                placeholder='Select a Student or Teacher...'
            ),
            html.Br(),
            dcc.Dropdown(
                id={'type': 'dynamic-input', 'index': 'select-item'}, 
                placeholder='Select Item', 
            ),
            html.Br(),
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

footer_info = [
    html.A('Source Code on GitHub.', href='<link>', style={'font-size': '14px', 'margin-bottom': '10px', 'color': 'white'}),
    html.P('Last updated on <date>', style={'font-size': '12px', 'margin-bottom': '10px'}),   
]

footer =  html.H3(
    footer_info,
    style={
        'backgroundColor': '#387c9f',
        'color': 'white',
        'font-size': '15px',
        'margin' : '0',
        'padding': '0px',
        'text-align': 'center'},  
)


