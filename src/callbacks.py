import dash
from dash import ctx
import dash.html as html
import dash.dcc as dcc
from datetime import datetime, timedelta
import os
from dash.dependencies import Input, Output, State, MATCH
from dash import dash_table
from .data import student_list, student_schedule, teacher_list, student_deadlines, teacher_roster, teacher_tasks, get_student_note, save_student_note, save_workhabits_data, save_deadlines_data, save_deleted_changes, save_checked_changes, workhabit_trend, upcoming_deadlines
from .graphs import attendance_barchart, workhabit_timeline, timespent_barchart
from dash import callback_context
from .components import *
from .config import * 

# FIX 
#start = datetime.today() - timedelta(weeks=70)
# end = datetime.today() + timedelta(weeks=3)
# start_str = start.strftime('%Y-%m-%d')
# end_str = end.strftime('%Y-%m-%d')
# dcc.Store(id={'type': 'dynamic-input', 'index': 'start-date'}, data=start_str), 
# dcc.Store(id={'type': 'dynamic-input', 'index': 'end-date'}, data=end_str),

def register_callbacks(app):

    # About pop-up
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

    # Update Work habit card
    @app.callback(
        [
            Output({'type': 'dynamic-output', 'index': 'work-habit-message'}, 'children'),
            Output({'type': 'dynamic-output', 'index': 'work-habit-icon'}, 'children'), 
            Output({'type': 'dynamic-output', 'index': 'work-habit-avg'}, 'children')
        ],
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')
    )
    def update_workhabit_card(selected_student):
        if selected_student:
            message, avg, icon = workhabit_trend(selected_student)         
            return message, icon, avg
        return "Trend", "∅", "∅"

    # Update attendance graph based on student and graph type 
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
        if selected_graph:
            return attendance_barchart(selected_student, False)
        else:
            return attendance_barchart(selected_student, True)
        
    # Updating timeline/barchart graph based on student and graph selection 
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'graph-output'}, 'figure'),
        [Input({'type': 'dynamic-input', 'index': 'graph-toggle'}, 'value'),
        Input({'type': 'dynamic-input', 'index': 'student-select'}, 'value')],
    )
    def update_graph(selected_graph, selected_student):      
        if selected_graph:  
            return timespent_barchart(selected_student)
        else:  
            return workhabit_timeline(selected_student)

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
            return f"Type notes for {student_selected} here..."

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
            return existing_data, dash.no_update

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
            Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value'), 
        ],
        prevent_initial_call=True

    )
    def update_content_t2col2(role, name):

        if role == 'Student' and name:
            table_data, selected_indicies = student_deadlines(name)

            return html.Div([
                html.H6(f'{name} - Tasks'),
                dash_table.DataTable(
                    id={'type':'dynamic-input', 'index':'student-task-table'}, 
                    columns=[{'name':'Due', 'id':'Due'}, 
                             {'name':'Task', 'id':'Task'}, 
                             {'name':'Course', 'id':'Course'}, 
                             {'name':'Teacher', 'id':'Teacher'}, 
                             {'name':'Block', 'id':'Block'}], 
                    data=table_data,
                    style_cell={'textAlign':'center', 'fontSize':'0.7rem'}, 
                    style_header={'fontWeight': 'bold', 'textAlign':'center'},                  
                    row_selectable='multi', 
                    row_deletable=True, 
                    selected_rows=selected_indicies
                ), 
                html.Div([
                    # Output message
                    html.Div(id={'type':'dynamic-output','index':'output-student-task'}, style={'marginRight':'10px','fontSize':'0.7rem'}),

                    # Save button
                    dbc.Button('Save', id={'type': 'dynamic-input', 'index': 'save-student-tasks'}, n_clicks=0, 
                            style={'marginTop': '10px','fontSize':'0.7rem'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'flex-end',  
                    'marginTop': '10px', 
                    'alignItems': 'center'
                })     
            ])

        elif role == 'Teacher' and name: 

            teacher_roster_dict = teacher_roster(name)
            start = datetime.today() - timedelta(weeks=70)
            end = datetime.today() + timedelta(weeks=3)

            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')

            teacher_task_dict = teacher_tasks(name, start_str, end_str)
            return html.Div([
                    html.Div([
                        html.H6(f'{name} - Assigned Tasks'), 
                        # Date 
                        dcc.DatePickerRange(
                            id={'type': 'dynamic-input', 'index': 'date-picker-tasks'},
                            start_date_placeholder_text="Start date",
                            end_date_placeholder_text="End date",
                            start_date=start_str,
                            end_date=end_str, 
                            style={'marginBottom':'10px'}
                        ),
                    ], 
                        style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'width': '100%'}  
                    ), 
            # Table
            dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in teacher_roster_dict.keys()], 
                data=[{col: '\n'.join(map(str, students)) for col, students in teacher_task_dict.items()},
                    {col: '\n'.join(map(str, students)) for col, students in teacher_roster_dict.items()}],
                style_data={'whiteSpace': 'pre-line'},
                style_cell={'textAlign':'center', 'fontSize':'0.7rem'}, 
                style_header={'fontWeight': 'bold', 'textAlign':'center'},  
            )
            ])
        else:
            return html.Div([
                html.H6('Tasks'), 
                dash_table.DataTable(
                    id='default-table',
                    columns=[{'name': '', 'id': ''}, {'name': '', 'id': ''}, {'name': '', 'id': ''}],
                    data=task_default_df.to_dict('records'),
                    style_table={'height': '200px', 'width': '100%'},
                )
            ])
# FIX
    # Adjust Teacher Assigned Task table when date range is changed
    # @app.callback(
    #     Output({'type': 'dynamic-input', 'index': 'teacher-task-table'}, 'data'),
    #     [
    #         Input({'type': 'dynamic-input', 'index': 'start-date'}, 'data'),
    #         Input({'type': 'dynamic-input', 'index': 'end-date'}, 'data'),
    #         Input({'type': 'dynamic-input', 'index': 'select-item'}, 'value'),  # Teacher selected
    #     ],
    #     prevent_initial_call=True
    # )
    # def update_teacher_task_table(start_date, end_date, teacher_name):
    #     print('Triggered')
    #     if not teacher_name or not start_date or not end_date:
    #         return dash.no_update  # If no teacher or no dates, do not update

    #     # Fetch and filter teacher task data based on the selected date range
    #     teacher_task_dict = teacher_tasks(teacher_name, start_date, end_date)

    #     # Format the teacher's task data to match the table structure
    #     table_data = [{col: '\n'.join(map(str, students)) for col, students in teacher_task_dict.items()}]

    #     return table_data

        
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
            Output({'type': 'dynamic-output', 'index': 'output-msg-deadlines'}, 'children'), 
            Output({'index':'csv-write-flag','type':'dynamic-output'}, 'data') # to ensure csv is written prior to updating table    
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
        if not ctx.triggered:
            return existing_data, dash.no_update, False
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] 

        # add row
        if 'add-row-deadlines' in triggered_id: 
            existing_data.append({'Task': '', 'Course': '', 'Block': '', 'Teacher': '', 'Due':''})
            return existing_data, '', False
        
        # clear message when cell edited
        if 'deadlines-table' in triggered_id and cell_change:
            return dash.no_update, '', False
        
        # save submitted data
        elif 'submit-deadlines' in triggered_id:

            cleaned_data = [row for row in existing_data if any(row.values())] 

            if not cleaned_data:
                return existing_data, 'No valid data to save.', False

            saved = save_deadlines_data(cleaned_data)
           
            # reset data
            reset_data = [{'Task': '', 'Course': '', 'Block': '', 'Teacher': '', 'Due':''}]
            return reset_data, saved, True
        return existing_data, '', False
    
    # Update Upcoming Deadlines
    @app.callback(
        Output({'type': 'dynamic-output', 'index': 'deadlines-table'}, 'data'),   
        Input({'index':'csv-write-flag','type':'dynamic-output'}, 'data'),
        prevent_initial_call=True
    )    
    def update_upcoming_deadlines(flag):
        if flag:
            return upcoming_deadlines()
        return dash.no_update


    
