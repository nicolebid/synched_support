import pandas as pd
import datetime
import math
from .config import STUDENT_DATA, DEADLINES_DATA, STUDENT_NOTE, ATTEND_DATA, STUDENT_TASKS
import os

# TAB 1 - DATA 
def student_list():
    """Retrieves the list of student names in the CSV file then formats them into a list
    to use in the drop down selection component. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing labels and values to correspond to each 
            student in the dataset, to be used as the dropdown options.
    """
    df = pd.read_csv(STUDENT_DATA)
    student_names = df['Student'].unique()
    options = [{'label': name, 'value': name} for name in student_names]
    return options 

def student_schedule(student_name):
    """Retrieves the student schedule (course, block, and teacher) from the CSV file for a given student.
    
    Parameters
    ----------
    student_name: str
        The name of the student to fetch the schedule for
    
    Returns
    -------
    list: List of dictionaties containing the course, teacher and block. 
    """
    df = pd.read_csv(STUDENT_DATA)
    df_student = df[df['Student'] == student_name]
    schedule = df_student[['Block', 'Course', 'Teacher' ]]
    schedule = schedule.sort_values(by='Block')
    return schedule.to_dict('records')

def workhabit_trend(student_name):
    """Calculuate trend in given student's work habit score over the past 6 days, and provides a message
    describing the increase, decrease or consistency in their worhabits. 
    
    Parameters
    ----------
    student_name: str
        The name of the student to determine the workhabit trend for. 
    
    Returns
    -------
    message: str
        The description of the students trend in work habits over the past 6 classes. 
    
    recent_avg: np.float
        The student's average work habit score for their 3 most recent classes. 
    """
    # set up data
    workhabit_scores = {'Off-task': 0, 'Mostly Off-task': 1,'Equally On/Off-task': 2, 'Mostly On-task': 3,'On-task': 4}
    df_workhabits = pd.read_csv(ATTEND_DATA)
    df_student = df_workhabits[df_workhabits['Student'] == student_name]
    df_student = df_student[df_student['Course'].str.contains('Support', regex=True)]
    df_student = df_student[df_student['Habit'].notna()]
    df_student['Score'] = df_student['Habit'].apply(lambda x: workhabit_scores.get(x))
    df_student.sort_values(by='Date', ascending=False, inplace=True)

    # Check if enougth data exists
    if len(df_student) < 5:
       return "insufficient data", "∅", "∅"

    # Calculate percent change
    recent = df_student.head(3)
    recent_avg = float(recent['Score'].mean())
    previous = df_student.iloc[3:6]
    previous_avg = float(previous['Score'].mean())
    per_change = round(((recent_avg - previous_avg)/previous_avg)*100, 1)
    mag_change = abs(per_change)
  
    # provide a message 
    if math.isclose(mag_change, 0, abs_tol=1e-5):
       return "consistent", round(recent_avg,1) , "🔁" 
   
    if mag_change > 0 and mag_change <= 5:
        mag = "small"
    elif mag_change > 5 and mag_change <= 10:
       mag = "moderate"
    elif mag_change > 10:
       mag = "large"

    if per_change > 0:
      trend = "increase"
      icon = "✅"
    else:
      trend = "decrease"
      icon = "⚠️"

    message = mag + ' ' + trend 
    return message, round(recent_avg,1), icon  

def get_student_note(student_name):
    """Retrieves the note from the CSV file for the given student.
    
    Parameters
    ----------
    student_name: str
        The name of the student to fetch the note for.
    
    Returns
    -------
    note: str
        The note for the given student.  
    """
    if os.path.exists(STUDENT_NOTE):
        df = pd.read_csv(STUDENT_NOTE)
        student_note = df[df['Student'] == student_name]['Note']
        if not student_note.empty:
            note = student_note.iloc[0]
        else:
            note = None
    return note

def save_student_note(student_name, note):
    """Updates (or saves) note in the csv file with the new note for the given student. 
    
    Parameters
    ----------
    student_name: str
        The name of the student to update the the note for.  
    note: str
        The note to save for the given student.   
    
    Returns
    -------
    str: Verified message.  
    """
    if os.path.exists(STUDENT_NOTE):
        df = pd.read_csv(STUDENT_NOTE)
        
        # override previous note
        if student_name in df['Student'].values:
            df.loc[df['Student'] == student_name, 'Note'] = note
        else:
            # create a new note
            new = pd.DataFrame({'Student': [student_name], 'Note' : [note]})
            df = pd.concat([df, new], ignore_index=True)

        df.to_csv(STUDENT_NOTE, index=False)

    else:
        # create dataframe
        df = pd.DataFrame({'Student': [student_name], 'Note': [note]})
        df.to_csv(STUDENT_NOTE, index=False)

    return "Note Saved."

def save_workhabits_data(data, date):
    """Updates attendance_habits.csv file to include user entered data.
    
    Parameters
    ----------
    data: list
        A list of dictionaries obtained from the the dash table.

    date: str
        The date for the data entry obtained from the dash datepicker component. 


    Returns
    -------
    str: Verified message.  
        
    """
    df_student = pd.read_csv(STUDENT_DATA)
    clean_data = []
    workhabit_scores = {'0':'Off-task', '1':'Mostly Off-task', '2':'Equally On/Off-task', '3':'Mostly On-task', '4':'On-task'}




    
    for data_pt in data:

        # Set up
        temp_pt = {}
        df_course_block = df_student[df_student['Student'] == data_pt['Student']] # data for pulling Course, Block, Teacher
        support_row = df_course_block[df_course_block['Course'].str.contains('Support')]

        # obtain values
        temp_pt['Student'] = data_pt['Student']
        temp_pt['Date'] = date
        temp_pt['Course'] = support_row['Course'].iloc[0]
        temp_pt['Block'] = support_row['Block'].iloc[0]
        temp_pt['Attendance'] = data_pt['Support Attendance']
        temp_pt['Teacher'] = support_row['Teacher'].iloc[0]
        temp_pt['Habit'] = workhabit_scores[data_pt['Workhabit Score']]
        temp_pt['Work'] = data_pt['Focus']

        clean_data.append(temp_pt)

    # Save data
    current_data = pd.read_csv(ATTEND_DATA)
    df_clean = pd.DataFrame(clean_data)
    df_updated = pd.concat([current_data, df_clean], ignore_index=True)
    df_updated = df_updated.sort_values(by=['Student', 'Date'], ascending=[True, True])
    df_updated.to_csv(ATTEND_DATA, index=False)
    return "Data Saved."

# TAB 2 - DATA
def teacher_list():
    """Retrieves the list of teacher's names in the CSV file then formats them into a list
    to use in the drop down selection component. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing labels and values to correspond to each 
            teacher in the dataset, to be used as the dropdown options.
    """
    df = pd.read_csv(STUDENT_DATA)
    df = df[~df['Course'].str.contains('Support', regex=True)]
    teachers = df['Teacher'].unique()
    options = [{'label': name, 'value': name} for name in teachers]
    return options 

def course_list():
    """Retrieves the list of courses in the CSV file then formats them into a list
    to use in the drop down selection component. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing labels and values to correspond to each 
            course in the dataset, to be used as the dropdown options.
    """
    df = pd.read_csv(STUDENT_DATA)
    df = df[~df['Course'].str.contains('Support', regex=True)]
    courses = df['Course'].unique()
    options = [{'label': name, 'value': name} for name in courses]
    return options 

def upcoming_deadlines():
    """Retrieves the tasks in the deadlines CSV file that are due within 2 weeks of the current
    date and returns the values in a list. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing tasks due within 4 weeks. 
    """
    df = pd.read_csv(DEADLINES_DATA)
    df['Due'] = pd.to_datetime(df['Due'])
    today = datetime.datetime.today()
    upcoming_weeks = today + datetime.timedelta(weeks=4)
    df_upcoming = df[(df['Due'] >= today) & ((df['Due'] <= upcoming_weeks))].copy()
    df_upcoming = df_upcoming.sort_values(by='Due')
    df_upcoming['Due'] = df_upcoming['Due'].dt.strftime('%b %d')  
    return df_upcoming.to_dict('records') 

def student_deadlines(student):
    """Retrieves the tasks in the deadlines CSV file for the given student, keeping hidden or selected
    rows consistent from previous session. 
    
    Returns:
    -------- 
    format_dict : list
        A list of dictionaries containing tasks for the student.
    selected_rows : list
        A list of indicies of rows to display with check marks for completed tasks. 

    """
    df_tasks = pd.read_csv(STUDENT_TASKS)
    df_tasks_student = df_tasks[df_tasks['Student'] == student].copy()
    df_tasks_student['Due'] = pd.to_datetime(df_tasks_student['Due']).dt.strftime('%b %d')
    
    # display unhidden rows
    df_filter = df_tasks_student[df_tasks_student['Hidden'] != True]  

    # keep previously selected rows checked 
    df_filter_reset = df_filter.reset_index(drop=True)
    selected_rows = df_filter_reset.index[df_filter_reset['Completed'] == True].tolist()

    # format for displaying 
    df_format = df_filter[['Due', 'Task', 'Course', 'Teacher', 'Block']]
    format_dict = df_format.to_dict('records')
    return format_dict, selected_rows

def teacher_roster(teacher):
    """Retrieves the students in each of the teachers classes. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing the courses and student lists. 
    """
    df_deadlines = pd.read_csv(DEADLINES_DATA)
    df_student = pd.read_csv(STUDENT_DATA)
    df_merged = pd.merge(df_deadlines, df_student, on=['Course', 'Teacher', 'Block'])
    df_teacher = df_merged[df_merged['Teacher'] == teacher].copy()
    df_teacher['Course_block'] = df_teacher['Course'] + " (" + df_teacher['Block'] + ")"
    df_pivot = df_teacher.pivot(columns='Course_block', values='Student')
    df_clean_dict = {}
    for col in df_pivot.columns:
        df_clean_dict[col] = list(set(df_pivot[col].dropna()))
    return df_clean_dict

def teacher_tasks(teacher):
    """Retrieves the assignments/tests for each course the given teacher teaches. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing the courses as keys and a list of assignments/tests as items. 
    """
    df_deadlines = pd.read_csv(DEADLINES_DATA)
    df_student = pd.read_csv(STUDENT_DATA)
    df_merged = pd.merge(df_deadlines, df_student, on=['Course', 'Teacher', 'Block'])
    df_teacher = df_merged[df_merged['Teacher'] == teacher].copy()
    df_teacher['Due_display'] = pd.to_datetime(df_teacher['Due']).dt.strftime('%b %d')  
    df_teacher['Task_due'] = df_teacher['Task'].str.cat(df_teacher['Due_display'], sep=' - ')
    df_teacher['Course_block'] = df_teacher['Course'] + " (" + df_teacher['Block'] + ")"
    df_pivot = df_teacher.pivot(columns='Course_block', values='Task_due')    
    df_clean_dict = {}
    for col in df_pivot.columns:
        df_clean_dict[col] = list(set(df_pivot[col].dropna()))
    return df_clean_dict

def student_tasks_update():
    """Generates and updates student_tasks.csv to include newly entered deadlines. 
    """
    # load data
    df_master = pd.read_csv(DEADLINES_DATA)
    student_schedule = pd.read_csv(STUDENT_DATA)
    
    # create file 
    if not os.path.isfile(STUDENT_TASKS):
        columns = ['Student', 'Task', 'Course', 'Block', 'Teacher', 'Grade', 'Due', 'Completed', 'Hidden']
        pd.DataFrame(columns=columns).to_csv(STUDENT_TASKS, index=False)
    
    df_student_tasks = pd.read_csv(STUDENT_TASKS) 
    
    # obtain new tasks to include    
    match_cols=['Task', 'Course', 'Block', 'Teacher', 'Due']
    merged = df_master.merge(df_student_tasks[match_cols].drop_duplicates(), on=match_cols, how='left', indicator=True)
    new_tasks = merged[merged['_merge'] == 'left_only'].drop(columns='_merge')

    # match with students and format
    new_data = pd.merge(student_schedule, new_tasks, on=['Course', 'Teacher', 'Block'], how='inner')
    new_data['Completed'] = False
    new_data['Hidden'] = False
    new_data = new_data[['Student', 'Task', 'Course', 'Block', 'Teacher', 'Grade', 'Due', 'Completed', 'Hidden']]

    # save new data
    new_data.to_csv(STUDENT_TASKS, mode='a', header=False, index=False)  

def save_deadlines_data(data):
    """Updates master_deadlines.csv to include user entered data. Then calls student_task_updates() to 
    update student_tasks.csv with newly entered tasks. 
    
    Parameters
    ----------
    data: list
        A list of dictionaries obtained from the the dash table.

    Returns
    -------
    str: Verified message.  
    """
    clean_data = []
    
    for data_pt in data:        
        temp_pt = {}
        
        # obtain values
        temp_pt['Task'] = data_pt['Task'].strip()
        temp_pt['Course'] = data_pt['Course'].strip()
        temp_pt['Block'] = data_pt['Block'].strip()
        temp_pt['Teacher'] = data_pt['Teacher'].strip()
        temp_pt['Due'] = data_pt['Due'].strip()
        clean_data.append(temp_pt)

    # Save data
    current_data = pd.read_csv(DEADLINES_DATA)
    df_clean = pd.DataFrame(clean_data)
    df_updated = pd.concat([current_data, df_clean], ignore_index=True)
    df_updated = df_updated.sort_values(by=['Due', 'Teacher'], ascending=[True, True])
    df_updated.to_csv(DEADLINES_DATA, index=False)
    
    # update student_tasks.csv
    student_tasks_update()

    return "Data saved successfully."

def save_deleted_changes(data, student_name):
    """Updates student_tasks.csv to includes changes to 'Hidden' column when user deletes
    rows in student task table.
    
    Parameters
    ----------
    data: list
        A list of dictionaries obtained from the the dash table.
    
    student_name: string  
        The name of the students data to edit. 

    Returns
    -------
    str: Verified message.  
    """
    df_tasks = pd.read_csv(STUDENT_TASKS)
    df_student_tasks = df_tasks[df_tasks['Student'] == student_name]
  
    # find deleted rows 
    data_compare = [{k: v for k, v in row.items() if k != 'Due'} for row in data] 
    for ind, row in df_student_tasks.iterrows():
        row_dict = row[['Task', 'Course', 'Teacher', 'Block']].to_dict()
        if row_dict not in data_compare:
            df_student_tasks.at[ind, 'Hidden'] = True
    
    # Save changes
    df_tasks.update(df_student_tasks)
    df_tasks.to_csv(STUDENT_TASKS, index=False)
    return "Changes saved successfully."

def save_checked_changes(selected_rows_data, student_name):
    """Updates student_tasks.csv to include changes to 'Completed' column when user checks
    rows in student task table.
    
    Parameters
    ----------
    selected_rows_ind: list
        A list of indicies of selected rows obtained from the the dash table.
    
    student_name: string  
        The name of the students data to edit. 

    Returns
    -------
    str: Verified message.  
    """
    df_tasks = pd.read_csv(STUDENT_TASKS)
    df_student_tasks = df_tasks[df_tasks['Student'] == student_name].copy()

    # handle unchecking
    df_student_tasks['Completed'] = False

    # find checked rows
    data_compare = [{k: v for k, v in row.items() if k != 'Due'} for row in selected_rows_data] 
    for ind, row in df_student_tasks.iterrows():
        row_dict = row[['Task', 'Course', 'Teacher', 'Block']].to_dict()
        if row_dict in data_compare:
            df_student_tasks.at[ind, 'Completed'] = True
    
    # Save changes
    df_tasks.update(df_student_tasks)
    df_tasks.to_csv(STUDENT_TASKS, index=False)
    return "Changes saved successfully."