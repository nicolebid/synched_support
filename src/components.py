import dash.html as html
import dash.dcc as dcc
import dash_bootstrap_components as dbc
import datetime
import pandas as pd 
import dash_ag_grid as dag
from collections import OrderedDict
from dash import dash_table
from .data import  student_list, upcoming_deadlines, save_workhabits_data
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart

# HEADER
title = html.H5(
    'Synced Support',
    style={
        'background-color': '#387c9f',
        'color': 'white',
        'padding': '0.4rem', 
        'margin': '0'
        }
)

info_button = dbc.Button(
    "About",
    id={'type': 'button', 'index': 'open-modal'},
    outline=True,
    n_clicks=0,
    style={
        'background-color': '#387c9f', 
        'color': 'white', 
        'border-radius': '1rem', 
        'font-size': '1rem', 
        'padding':'0.4rem'
        }
)

info_section = dbc.Modal([
        dbc.ModalHeader("About This App", close_button=True), 
        dbc.ModalBody("This is an app that tracks student work habits and progress."),
    ],
    id={'type': 'dynamic-output', 'index': 'about-modal'},
    is_open=False,
)

# MAIN CONTENT 
def create_tabs():
    return dcc.Tabs(
    id='tabs',
    value='student-tab',
    children=[
        dcc.Tab(
            label='Student View', 
            value='student-tab', 
            style={'paddingTop': '0.7rem'},
            selected_style={'paddingTop': '0.7rem'}  
        ),
        dcc.Tab(
            label='Task View', 
            value='task-tab', 
            style={'paddingTop': '0.7rem'},
            selected_style={'paddingTop': '0.7rem'}  
        )
    ],
    style={'height': '3rem'}
)

# Default Values - student tab
default_schedule = [{'Block': '1-1', 'Course': None, 'Teacher': None},
                    {'Block': '1-2', 'Course': None, 'Teacher': None},
                    {'Block': '1-3', 'Course': None, 'Teacher': None},
                    {'Block': '1-4', 'Course': None, 'Teacher': None},
                    {'Block': '2-1', 'Course': None, 'Teacher': None},
                    {'Block': '2-2', 'Course': None, 'Teacher': None},
                    {'Block': '2-3', 'Course': None, 'Teacher': None},
                    {'Block': '2-4', 'Course': None, 'Teacher': None}]

# Default values 
initial_attendance_graph = attendance_barchart()  
initial_workhabit_graph = workhabit_timeline()
initial_timespent_graph = timespent_barchart()
initial_workhabit_data = [{'Student': '', 'Workhabit Score': '', 'Focus': '', 'Support Attendance': ''}]

default_student_tasks = [{'Due': None, 'Task': None, 'Course': None, 'Teacher': None, 'Block': None }]
initial_deadlines_data = [{'Task': '', 'Course': '', 'Block': '', 'Teacher': '', 'Due':''}]

# Student Tab 
student_tab = dbc.Row([
    # COLUMN 1
    dbc.Col([   
    # Student Selection
        dcc.Dropdown(
            id={'type': 'dynamic-input', 'index': 'student-select'},
            options=student_list(), 
            value='A', 
            placeholder='Select a student...', 
            style={
                'marginBottom': '0.5rem', 
                'fontSize': '0.8rem'
            } 
        ),  
        # Student Schedule 
        html.Div([
            html.H6("Schedule"),
            dash_table.DataTable(
                id={'type': 'dynamic-output', 'index': 'course-table'},
                columns=[
                    {'name': 'Block', 'id': 'Block'},
                    {'name': 'Course', 'id': 'Course'},
                    {'name': 'Teacher', 'id': 'Teacher'}       
                ],
                data=default_schedule, 
                style_cell={'textAlign':'center', 
                            'fontSize':'0.7rem'
                            }, 
                style_header={
                    'fontWeight': 'bold', 
                    'textAlign':'center'
                    },                      
            )
        ], 
        style={
                'border': '0.1rem solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px', 
                'marginBottom': '0.5rem', 
                'flex-grow': '1',
                'height': 'auto'
        }
        ),
        # Work habit Cards 
        html.Div([
            html.H6("Work Habit Insights"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("6-day Trend",  style={'textAlign': 'center', 'fontSize':'0.7rem'}),
                                dbc.CardBody(
                                    [
                                        html.H3("", 
                                                id={'type': 'dynamic-output', 'index': 'work-habit-icon'}, 
                                                style={'textAlign': 'center'}),                                     
                                        html.Div(
                                            "Trend",
                                            id={"type": "dynamic-output", "index": "work-habit-message"},
                                            style={'textAlign': 'center', 'fontSize':'0.8rem'}
                                        ),

                                    ]
                                ),
                            ],
                            outline=True,
                        ),
                        width=6  
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Current Average",  style={'textAlign': 'center', 'fontSize':'0.7rem'}),
                                dbc.CardBody(
                                    [
                                        html.H3("",
                                                id={'type': 'dynamic-output', 'index': 'work-habit-avg'},
                                                style={'textAlign':'center'},
                                                className="card-title"),
                                        html.Div('Out of 4',  style={'textAlign':'center', 'fontSize':'0.8rem'})
                                    ]
                                ),
                            ],
                            outline=True,
                        ),
                        width=6  
                    )
                ],
                className="g-2"  
            )],
            style={
                'border': '0.1rem solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px', 
                'marginBottom': '0.8rem', 
                'flex-grow': '1', 
        } 
        )

    ], width=3,style={'display': 'flex','flex-direction': 'column'}), 
    # COLUMN 2 
    dbc.Col([
        # Workhabits Graphs 
        html.Div([
            html.Div([
                html.H6("Study Habits"),
                html.Div([
                        html.Div("Work Habits ", style={'display': 'inline-block', 'whiteSpace': 'nowrap', 'marginRight': '9px'}),
                        dbc.Switch(
                            id={'type': 'dynamic-input', 'index': 'graph-toggle'},
                            value=False, 
                            style={"width": "auto", 'paddingTop': '3px'} 
                        ),
                        html.Div("Time Spent", style={'display': 'inline-block', 'whiteSpace': 'nowrap', 'marginLeft': '3px'}),
                ],
                    style={'fontSize': '0.8rem', 'display': 'flex', 'alignItems': 'center'}
                ),
            ], 
                style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'width': '100%'}),
            dcc.Graph(
                id={'type': 'dynamic-output', 'index': 'graph-output'},
                config={'displayModeBar':False},
                style={'width':'100%', 'height':'35.5vh'} 
            ), 
        ], 
            style={
                'border': '2px solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px', 
                 'marginBottom': '0.5rem'
            }
        ),

        # Notes input 
        html.Div([
            html.H6("Notes", style={'marginBottom':'10px'}), 
            dbc.Textarea(
                id={'type': 'note-input', 'index': 'teacher-notes'}, 
                placeholder='Type your notes here...', 
                style={'width':'100%', 'fontSize':'0.8rem', 'height':'100%'}
            ), 
           html.Div([
               # Output message
                html.Div(id={'type':'dynamic-output','index':'output-msg-note'}, 
                        style={'fontSize':'0.7rem', 'marginTop':'10px', 'marginRight':'10px'}),
                dbc.Button(
                    'Save', 
                    id={'type': 'dynamic-input', 'index': 'save-note-button'},
                    n_clicks=0, 
                    style={'fontSize':'0.7rem', 'marginTop':'10px'} 
                ),   
            ], 
            style={
                'display': 'flex',               
                'justifyContent': 'flex-end',      
                'alignItems': 'center',            
                'width': '100%', 
                'marginLeft':'auto'                  
            })
        ],  
            style={
                'border': '2px solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px', 
                'display': 'flex',  
                'flex-direction': 'column',  
                'align-items': 'flex-start', 
                'height':'35.5vh' 
            } 
        )
    ], width=5, style={'display': 'flex', 'flex-direction': 'column'}),

    # COLUMN 3
    dbc.Col([
        # Attendance Bar Chart 
        html.Div([
            html.Div([
                html.H6("Attendance", style={'margin-right': '50px'}),
                # Graph Type 
                html.Div([
                        html.Div("Overall ", style={'display': 'inline-block', 'whiteSpace': 'nowrap', 'marginRight': '9px'}),
                        dbc.Switch(
                            id={'type': 'dynamic-input', 'index': 'attendance-toggle'},
                            value=False, 
                            style={"width": "auto", 'paddingTop': '3px'} 
                        ),
                        html.Div("Courses", style={'display': 'inline-block', 'whiteSpace': 'nowrap', 'marginLeft': '3px'}),
                ],
                    style={'fontSize': '0.8rem', 'display': 'flex', 'alignItems': 'center'}
                ),
            ], 
            style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'width': '100%'}), 
            dcc.Graph(
                id={'type': 'dynamic-output', 'index': 'attendance-graph'},
                figure=initial_attendance_graph,
                config={'displayModeBar': False},
                style={'flex-grow': '1', 'height':'35.5vh'}  
            )
        ], 
            style={'border': '2px solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px', 
                'marginBottom':'0.5rem'
            }
        ),
      
        # Work Habit Data - User input 
        html.Div([
            html.Div([
                html.H6("Daily Work Habits"), 
                # Date 
                dcc.DatePickerSingle(
                    id={'type':'dynamic-input', 'index':'date-picker'}, 
                    placeholder="Select date", date=datetime.date.today(), 
                    style={'marginBottom':'10px'}
                )
            ], 
                style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'width': '100%'}  
            ), 

            # input table
            dag.AgGrid(
                id={'type': 'user-input', 'index': 'workhabit-table'},
                columnDefs=[
                    {'headerName': 'Student', 'field': 'Student', 'editable': True, 'flex': 1},
                    {'headerName': 'WH Score', 'field': 'Workhabit Score', 'editable': True, 'flex': 1},
                    {'headerName': 'Subject Focus', 'field': 'Focus', 'editable': True, 'flex': 1},
                    {'headerName': 'Attendance', 'field': 'Support Attendance', 'editable': True, 'flex': 1}
                ],
                rowData=initial_workhabit_data, 
                defaultColDef={'sortable': False, 
                               'filter': False, 
                               'resizable': False, 
                               'wrapHeaderText': True, 
                               'suppressMovable': True, 
                               'cellStyle': {'fontSize': '0.7rem'},
                               "autoHeaderHeight": True,
                },
                style={'width': '100%', 'height':'150px'}, 
            ),

            # Button - add row/submit data
            html.Div([
                # Output message
                html.Div(id={'index':'output-msg','type':'dynamic-output'}, style={'fontSize':'0.7rem', 'marginRight':'10px'}),
                dbc.Button("Add Row", id={'type': 'dynamic-input', 'index': 'add-row-btn'}, n_clicks=0, style={'marginRight':'10px', 'marginTop':'10px', 'fontSize':'0.7rem'}),
                dbc.Button("Submit", id={'type': 'dynamic-input', 'index': 'submit-btn'}, n_clicks=0, style={'marginTop':'10px', 'fontSize':'0.7rem'})
            ], 
                style={
                    'display': 'flex',               
                    'justifyContent': 'flex-end',      
                    'alignItems': 'center',            
                    'width': '100%', 
                    'marginLeft':'auto'                  
                }
            ),
        ], 
            style={
                'border': '2px solid #387c9f', 
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding':'10px',
                'overflow': 'visible'                             
            }                             
        ),                           
    ], 
        width=4, style={'flex-direction': 'column'}
    )
],
class_name='g-2',
style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap', 'paddingTop':'0.5rem', 'width': '100%'}
)

# Task Tab 
task_tab = dbc.Row([
        # COLUMN 1 
        dbc.Col([
            # Teacher/Course Selection
            dcc.Dropdown(
                id={'type': 'dynamic-input', 'index': 'select-type'},
                options=[
                    {'label': 'Student', 'value': 'Student'},
                    {'label': 'Teacher', 'value': 'Teacher'}
                ],
                placeholder='Select Student or Teacher...', 
                style={'marginBottom': '0.5rem', 'marginTop': '0'}
            ),
            dcc.Dropdown(
                id={'type': 'dynamic-input', 'index': 'select-item'}, 
                placeholder='select item',
                style={'marginBottom': '0.5rem', 'marginTop': '0'} 
            ),
            # Upcoming Deadlines
            html.Div([
                html.H6("Upcoming Deadlines"),
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
                    style_cell={'textAlign':'center', 'fontSize':'0.7rem'}, 
                    style_header={'fontWeight': 'bold', 'textAlign':'center'}, 
                )
            ], 
                style={'border': 
                      '2px solid #387c9f', 
                      'border-radius': '8px', 
                      'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                      'padding':'10px', 
                      'minHeight': '60vh'
                }
            )
        ], 
            style={'flex': '1','fontSize': '0.8rem'}
        ),
             
        # COLUMN 2
        dbc.Col([
            # Task Display Table
            html.Div([
                html.Div(id={'type': 'dynamic-input', 'index': 'dynamic-task-tables'}),
            ], style={
                'border': '2px solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding': '10px', 
                'marginBottom': '10px', 
                'minHeight': '35vh'
            }),

            # Task Deadlines - User input 
            html.Div([
                html.H6("New Tasks", style={'marginBottom':'10px'}), 
                # Table input
                dag.AgGrid(
                    id={'type': 'user-input', 'index': 'deadlines-table'}, 
                    columnDefs=[
                        {'headerName': 'Task', 'field': 'Task', 'editable': True, 'flex':3},
                        {'headerName': 'Course', 'field': 'Course', 'editable': True, 'flex':3},
                        {'headerName': 'Block', 'field': 'Block', 'editable': True, 'flex':1},
                        {'headerName': 'Teacher', 'field': 'Teacher', 'editable': True, 'flex':3},
                        {'headerName': 'Due', 'field': 'Due', 'editable': True, 'flex':1} 
                    ], 
                    rowData=initial_deadlines_data, 
                    defaultColDef={'sortable': False, 
                               'filter': False, 
                               'resizable': False, 
                               'wrapHeaderText': True, 
                               'suppressMovable': True,
                               'cellStyle': {'fontSize': '0.7rem'}, 
                               'autoHeaderHeight': True},
                    style={'width': '100%', 'height':'150px'} 
                ),

                # Button - add row/submit data
                html.Div([
                    # Output message
                    html.Div(id={'index':'output-msg-deadlines','type':'dynamic-output'}, style={'marginRight':'10px', 'fontSize':'0.7rem'}), 
                    dbc.Button("Add Row", id={'type': 'dynamic-input', 'index': 'add-row-deadlines'}, n_clicks=0, style={'marginRight':'10px', 'fontSize':'0.7rem'}),
                    dbc.Button("Submit", id={'type': 'dynamic-input', 'index': 'submit-deadlines'}, n_clicks=0, style={'fontSize':'0.7rem'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'flex-end',  
                    'marginTop': '10px', 
                    'alignItems': 'center'} 
                ),                     
            ], style={
                'border': '2px solid #387c9f',
                'border-radius': '8px', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding': '10px', 
                'marginBottom': '20px', 
                'minHeight': '35vh'
            }),

        ], 
        style={
            'flex': '3',  
            'display': 'flex',  
            'flex-direction': 'column'
        }
        )

], 
class_name='g-2',
style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap', 'paddingTop':'0.5rem', 'width': '100%'}
)

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


