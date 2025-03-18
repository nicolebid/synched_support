import dash
from dash import ctx
import dash.html as html
import dash.dcc as dcc
import datetime
import os
from dash.dependencies import Input, Output, State
from dash import dash_table
from .data import student_list, student_schedule, teacher_list, student_deadlines, teacher_roster, teacher_tasks, get_student_note, save_student_note, save_workhabits_data, save_deadlines_data, save_deleted_changes, save_checked_changes
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart
from dash import callback_context
from .components import *
from .config import * 

def register_callbacks(app):

    # Opening about popup
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'about-modal'}, 'is_open'),
        Input({'type': 'button', 'index': 'open-modal'}, 'n_clicks'),
        State({'type': 'dynamic-output', 'index': 'about-modal'}, 'is_open'),
        prevent_initial_call=True
    )
    def toggle_modal(open_clicks, is_open):
        return not is_open 

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
    # Updating student schedule when the student is selected 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'course-table'}, 'data'), 
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value') 
    )
    def update_schedule(selected_student):
        if selected_student:
            return student_schedule(selected_student)
        return default_schedule

    # Updating attendance graph based on student and graph type 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'attendance-graph'}, 'figure'), 
        [
            Input({'type': 'dynamic-input', 'index': 'attendance-toggle'}, 'value'),
            Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')
        ]  
    )
    def update_attendance_bar_chart(selected_graph, selected_student):
        if not selected_student:
            return attendance_barchart()
        if selected_graph == 'overall-attend':
            return attendance_barchart(selected_student, True)
        elif selected_graph == 'course-attend':
            return attendance_barchart(selected_student, False)
        return attendance_barchart()
        
    # Updating timeline/barchart graph based on student and graph selection 
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
    
    # Update Notes when student is selected
    @app.callback(
        Output({'type': 'note-input', 'index': 'teacher-notes'}, 'value'), 
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')
    )
    def update_notes(student_selected):
        if not student_selected:
            return "Select a student to view/edit notes..."
        else:
            # get to display
            student_note = get_student_note(student_selected)
            if student_note:
                return student_note
            return f"Type your notes for {student_selected} here..."

    # Update student notes in CSV when save is clicked
    @app.callback(
        [
            Output({'type':'dynamic-output','index':'output-msg-note'}, 'children'),
            Output({'type': 'dynamic-input', 'index': 'save-note-button'}, 'n_clicks')
        ],
        [   
            Input({'type': 'note-input', 'index': 'teacher-notes'}, 'value'),  
            Input({'type': 'dynamic-input', 'index': 'save-note-button'},'n_clicks'),
            Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')
        ], 
        State({'type': 'note-input', 'index': 'teacher-notes'}, 'value')      
    )

    def save_notes(note_value, n_clicks, student_selected, current_note_value):
        if student_selected is None or note_value != current_note_value: 
            return '', 0  # clears output message and resets button
        
        if n_clicks > 0: 

            if student_selected and note_value:
                save_student_note(student_selected, note_value)
                return "Note saved.", 0 
        return '', 0 
    
    # Work Habit Data - User input 
    @app.callback(
        [
            Output({'type': 'user-input', 'index': 'workhabit-table'}, 'rowData'),
            Output({'type': 'dynamic-output', 'index': 'output-msg'}, 'children')
        ],
        [
            Input({'type': 'dynamic-input', 'index': 'add-row-btn'}, 'n_clicks'),
            Input({'type': 'dynamic-input', 'index': 'submit-btn'}, 'n_clicks'),
            Input({'type': 'dynamic-input', 'index': 'date-picker'}, 'date'),
            Input({'type': 'user-input', 'index': 'workhabit-table'}, 'cellValueChanged')
        ],
        State({'type': 'user-input', 'index': 'workhabit-table'}, 'rowData'),
        prevent_initial_call=True
    )
    def update_table(add_clicks, submit_clicks, date, cell_changed, existing_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            return existing_data, ''

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Clear message when a cell is edited
        if 'workhabit-table' in triggered_id and cell_changed:
            return dash.no_update, ''

        # Add blank row when clicked
        if 'add-row-btn' in triggered_id:
            existing_data.append({'Student': '', 'Workhabit Score': '', 'Focus': '', 'Support Attendance': ''})
            return existing_data, ''

        # Save submitted data
        elif 'submit-btn' in triggered_id:
    
            cleaned_data = [row for row in existing_data if any(row.values())] # remove empty rows
            
            # error message for no valid data 
            if not cleaned_data:
                return existing_data, 'No valid data to save.'
            
            saved_message = save_workhabits_data(cleaned_data, date)
            reset_data = [{'Student': '', 'Workhabit Score': '', 'Focus': '', 'Support Attendance': ''}]
            return reset_data, saved_message

        return existing_data, ''
      
    # TAB 2
    # Update 2nd Dropdown when first dropdown is selected
    @app.callback(
        [
            Output({'type': 'dynamic-input', 'index': 'select-item'}, 'options'),
            Output({'type': 'dynamic-input', 'index': 'select-item'}, 'placeholder')
        ],
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
    task_default_df = pd.DataFrame([['','','','']]*3)

    @app.callback(
        Output({'type': 'dynamic-input', 'index': 'dynamic-task-tables'}, 'children'), 
        [
            Input({'type': 'dynamic-input', 'index': 'select-type'}, 'value'), 
            Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value')
        ]
    )
    def update_content_t2col2(role, name):

        if role == 'Student' and name:
            table_data, selected_indicies = student_deadlines(name)

            return html.Div([
                html.H5(f'{name} - Tasks'),
                dash_table.DataTable(
                    id={'type':'dynamic-input', 'index':'student-task-table'}, 
                    columns=[{'name':'Due', 'id':'Due'}, 
                             {'name':'Task', 'id':'Task'}, 
                             {'name':'Course', 'id':'Course'}, 
                             {'name':'Teacher', 'id':'Teacher'}, 
                             {'name':'Block', 'id':'Block'}], 
                    data=table_data,
                    style_cell={'textAlign':'center'},
                    style_header={'fontWeight': 'bold'}, 
                    row_selectable='multi', 
                    row_deletable=True, 
                    selected_rows=selected_indicies
                ), 

                html.Div([
                    # Output message
                    html.Div(id={'type':'dynamic-output','index':'output-student-task'}),

                    # Save button
                    dbc.Button('Save', id={'type': 'dynamic-input', 'index': 'save-student-tasks'}, n_clicks=0, 
                            style={'marginTop': '10px'})
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-end'})     
            ])

        elif role == 'Teacher' and name: 
            teacher_roster_dict = teacher_roster(name)
            teacher_task_dict = teacher_tasks(name)
            return html.Div([
            html.H5(f'{name} - Assigned Tasks'), 
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
                html.H5('Tasks'), 
                dash_table.DataTable(
                    id='default-table',
                    columns=[{'name': '', 'id': ''}, {'name': '', 'id': ''}, {'name': '', 'id': ''}],
                    data=task_default_df.to_dict('records'),
                    style_table={'height': '200px', 'width': '100%'
                    },
                )
            ])
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'output-student-task'}, 'children'),
        Input({'type': 'dynamic-input', 'index': 'save-student-tasks'}, 'n_clicks'),
        State({'type': 'dynamic-input', 'index': 'student-task-table'}, 'data'),
        State({'type': 'dynamic-input', 'index': 'student-task-table'}, 'derived_virtual_selected_rows'),
        State({'type': 'dynamic-input', 'index': 'select-item'}, 'value'), 
        prevent_initial_call=True
    )
    def save_task_updates(n_clicks, data, selected_rows_ind, student_name):
        # current csv
        df_tasks = pd.read_csv(STUDENT_TASKS)
        df_student_tasks  = df_tasks[df_tasks['Student'] == student_name]
        msg = ""
                
        # update status of deleted rows in csv
        if len(df_student_tasks) > len(data):
            msg = save_deleted_changes(data, student_name)
        
        # update status of selected rows in csv
        if selected_rows_ind is not None:
            selected_rows_data = [data[i] for i in selected_rows_ind]
            msg = save_checked_changes(selected_rows_data, student_name)
        return msg

    # Task Deadlines - User input
    # Add row/submit data/append to csv/reset table
    @app.callback(
        [
            Output({'type': 'user-input', 'index': 'deadlines-table'}, 'rowData'),
            Output({'type': 'dynamic-output', 'index': 'output-msg-deadlines'}, 'children')    
        ], 
        [
            Input({'type': 'dynamic-input', 'index': 'add-row-deadlines'}, 'n_clicks'),
            Input({'type': 'dynamic-input', 'index': 'submit-deadlines'}, 'n_clicks'), 
            Input({'type': 'user-input', 'index': 'deadlines-table'}, 'cellValueChanged')
       ], 
        State({'type': 'user-input', 'index': 'deadlines-table'}, 'rowData'),
        prevent_initial_call=True
    )
    def update_deadlines_table(add_clicks, submit_clicks, cell_change, existing_data):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] 

        # add row
        if 'add-row-deadlines' in triggered_id: 
            existing_data.append({'Task': '', 'Course': '', 'Block': '', 'Teacher': '', 'Due':''})
            return existing_data, ''
        
        # clear message when cell edited
        if 'deadlines-table' in triggered_id and cell_change:
            return dash.no_update, ''
        
        # save submitted data
        elif 'submit-deadlines' in triggered_id:

            cleaned_data = [row for row in existing_data if any(row.values())] 

            if not cleaned_data:
                return existing_data, 'No valid data to save.'

            saved = save_deadlines_data(cleaned_data)
           
            # reset data
            reset_data = [{'Task': '', 'Course': '', 'Block': '', 'Teacher': '', 'Due':''}]
            return reset_data, saved
        return existing_data, ''
        




    # Task Deadlines - User input 
    # Add new row/submit data/append to csv/reset table - OLD 
    # @app.callback(
    #     [
    #         Output({'type': 'user-input', 'index': 'deadlines-table'}, "data"),
    #         Output({'type': 'dynamic-output', 'index': 'output-msg-deadlines'}, "children")    
    #     ], 
    #     [
    #         Input({'type': 'dynamic-input', 'index': 'add-row-deadlines'}, "n_clicks"),
    #         Input({'type': 'dynamic-input', 'index': 'submit-deadlines'}, "n_clicks"), 
    #    ], 
    #     State({'type': 'user-input', 'index': 'deadlines-table'}, "data"),
    #     prevent_initial_call=True
    # )

    # def update_table(add_clicks, submit_clicks, existing_data):
    #     ctx = dash.callback_context
    #     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] 
        
    #     # add blank row when clicked
    #     if 'add-row-deadlines' in triggered_id: 
    #         existing_data.append({"Task": "", "Course": "", "Block": "", "Teacher": "", "Due":""})
    #         return existing_data, ""
        
    #     # save submitted data
    #     elif 'submit-deadlines' in triggered_id:
    #         saved = save_deadlines_data(existing_data)
           
    #         # reset data
    #         reset_data = [{"Task": "", "Course": "", "Block": "", "Teacher": "", "Due":""}]
    #         return reset_data, saved
    #     return existing_data, ""
   


        
    
