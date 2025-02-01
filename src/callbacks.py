from dash.dependencies import Input, Output, State
from dash import dash_table
import dash.html as html
import dash.dcc as dcc
from .data import student_list, student_schedule, teacher_list, course_list, deadlines, master_deadlines, upcoming_deadlines
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
                placeholder='Sort by...', 
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
                        {'name': 'Due Dates', 'id': 'Due'}, 
                        {'name': 'Task', 'id': 'Task'},  
                        {'name': 'Course', 'id': 'Course'}, 
                        {'name': 'Teacher', 'id': 'Teacher'},
                        {'name': 'Block', 'id': 'Block'}
                    ],
                    data=upcoming
                )
            ])
        ], style={
            'width': '15%', 
            'display': 'inline-block', 
            'padding-right': '2px', 
            'box-sizing': 'border-box'
        }),


                    
        # TAB 2 - COLUMN 2
        html.Div([
            html.Div(id={'type': 'dynamic-input', 'index': 'dynamic-t2-col2'})
        ], style={'width': '48%', 'display': 'inline-block'}
        
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

    # Update the attendance graph when student is selected
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'attendance-graph'}, 'figure'), 
        [Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')]  
    )
    def update_attendance_bar_chart(selected_student):
        if selected_student:
            return attendance_barchart(selected_student)
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
    

    @app.callback(
        Output({'type': 'dynamic-input', 'index': 'dynamic-t2-col2'}, 'children'), 
        Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value')
    )
    def update_content_t2col2(role):
        print(f'role selencted: {role}')
        if role == 'Student':
            return html.Div([
                html.H3('Student Infromation Table')
            ])
        elif role == 'Teacher': 
            return html.Div([
                html.H3('Teacher Infromation Table')
            ])
        else:
            return html.Div([
                html.H3('Select a role')
            ])
    
 










 # html.Div([  
        #     html.Div([
        #         html.H1("Course Assignments Dash Grid", style={
        #             'text-align': 'left',  
        #             'margin': '1',   
        #         }),
        #         dash_table.DataTable(
        #             data=data,
        #             columns=column_names,
        #             style_table={'width': '100%', 'margin': '0','padding': '0'},
        #             style_cell={'textAlign': 'left', 'padding': '5px'},
        #             style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0', 'textAlign': 'left'},
        #             style_data={'whiteSpace': 'pre-line','height': 'auto'}
        #         )
        #     ], style={'width': '100%', 'textAlign': 'left', 'margin': '0','padding': '0'}
        #     )
        # ], style={'width': '85%', 'box-sizing': 'border-box','textAlign': 'left', 'margin': '0', 'padding-right': '10px' }
        # )







    # Update the deadlines table when second dropdown is selected
    # @app.callback(
    #     Output({'type': 'dynamic-output', 'index': 'deadlines-table'}, 'data'), 
    #     Output({'type': 'dynamic-output', 'index': 'deadlines-table'}, 'columns'),
    #     [Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value'), 
    #     Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value')]
    # )
    # def update_deadlines(selected_item, selected_type):
    #     if selected_type == 'Teacher' and selected_item is not None:
    #         columns = [{'name': 'Course', 'id': 'Course'},
    #                 {'name': 'Task', 'id': 'Task'}, 
    #                 {'name': 'Block', 'id': 'Block'}, 
    #                 {'name': 'Due', 'id': 'Due'}]
    #         data = deadlines(teacher_name=selected_item)
    #     elif selected_type == 'Course' and selected_item is not None: 
    #         columns = [{'name': 'Teacher', 'id': 'Teacher'}, 
    #                 {'name': 'Task', 'id': 'Task'},
    #                 {'name': 'Block', 'id': 'Block'}, 
    #                 {'name': 'Due', 'id': 'Due'}]
    #         data = deadlines(course_name=selected_item)
    #     else:
    #         columns = [{'name': 'Task', 'id': 'Task'},
    #                 {'name': 'Course', 'id': 'Course'},
    #                 {'name': 'Teacher', 'id': 'Teacher'},
    #                 {'name': 'Block', 'id': 'Block'},
    #                 {'name': 'Due', 'id': 'Due'}]
    #         data = default_deadlines
        
    #     return data, columns


