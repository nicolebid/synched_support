import dash.html as html
import dash.dcc as dcc
import datetime
from dash.dependencies import Input, Output, State
from dash import dash_table
from .data import student_list, student_schedule, teacher_list, student_deadlines, teacher_roster, teacher_tasks
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart
from dash import callback_context
from .components import *

def register_callbacks(app):

    # Dropdown button for information
    @app.callback(
        Output({'type': 'dynamic-output', 'index':"info"}, "is_open"),
        [Input({'type': 'dynamic-input', 'index': 'info-button'}, "n_clicks")],
        [State({'type': 'dynamic-state', 'index':'info'}, "is_open")],  
    )
    def toggle_button(n, is_open):
        print(n)  
        print(is_open)  
        if n:
            return not is_open
        return is_open

    
    # Active tab
    @app.callback(
        Output('tab-content', 'children'),
        [Input('tabs', 'value')]
    )
    def render_content(tab): 
        if tab == 'student-tab':
            return student_tab

        elif tab == 'task-tab':
            return task_tab

    # TAB 1 
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
    
    # TAB 2
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
                    style_header={'fontWeight': 'bold'}, 
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
                data=[{col: '\n'.join(map(str, students)) for col, students in teacher_task_dict.items()},
                    {col: '\n'.join(map(str, students)) for col, students in teacher_roster_dict.items()}],
                style_cell={'padding': '10px', 'textAlign': 'center'},
                style_data={'whiteSpace': 'pre-line'},
                style_header={'fontWeight': 'bold'}
            )
            ])
        else:
            return html.Div([
                html.H3('Select a Student or Teacher')
            ])