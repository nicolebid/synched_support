import pandas as pd
import datetime
from .config import STUDENT_DATA, DEADLINES_DATA


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
    list : A list of dictionaries containing tasks due within 2 weeks. 
    """
    df = pd.read_csv(DEADLINES_DATA)
    df['Due'] = pd.to_datetime(df['Due'])
    today = datetime.datetime.today()
    two_weeks = today + datetime.timedelta(weeks=2)
    df_upcoming = df[(df['Due'] >= today) & ((df['Due'] <= two_weeks))].copy()
    df_upcoming['Due'] = df_upcoming['Due'].dt.strftime('%Y-%m-%d')
    return df_upcoming.to_dict('records') 

def student_deadlines(student):
    """Retrieves the tasks in the deadlines CSV file for the given student. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing tasks for the student. 
    """
    df_deadlines = pd.read_csv(DEADLINES_DATA)
    df_student = pd.read_csv(STUDENT_DATA)
    df_merged = pd.merge(df_deadlines, df_student, on=['Course', 'Teacher', 'Block'])
    df_student_deadlines = df_merged[df_merged['Student'] == student]
    df_return = df_student_deadlines[['Due', 'Task', 'Course', 'Teacher', 'Block']]
    return df_return.to_dict('records')

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
        df_clean_dict[col] = df_pivot[col].dropna().tolist()
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






# FUNCTION CURRENTLY NOT BEING USED 
def deadlines(course_name=None, teacher_name=None):
    """Retrieves the deadlines (task, course, block, due date) from the deadlines.csv filtered by 
    the given course or teacher.
    
    Parameters
    ----------
    course_name: str
            The name of the course to fetch the deadlines for.
    teacher_name: str
        The name of the teacher to fetch the deadlines for.
    
    Returns
    -------
    list: List of dictionaties containing the task, course or teacher, block, and due date. 
    """
    df = pd.read_csv(DEADLINES_DATA)
    if course_name is not None and teacher_name == None: 
        df_course =df[df['Course'] == course_name]
        deadlines = df_course[['Task', 'Teacher', 'Block', 'Due' ]]
        deadlines = deadlines.sort_values(by='Due')
        return deadlines.to_dict('records')
    else: 
        df_teacher = df[df['Teacher'] == teacher_name]
        deadlines = df_teacher[['Task', 'Course', 'Block', 'Due' ]]
        deadlines = deadlines.sort_values(by='Due')
        return deadlines.to_dict('records')   




# FUNCTION CURRENTLY NOT BEING USED 
def master_deadlines():
    """Retrieves the data from, deadlines.csv, to populate the deadline master table. 
    
    Returns
    -------
    list: List of data to populate the table. 
    """
    df_student = pd.read_csv(STUDENT_DATA)
    df_student = df_student[~df_student['Course'].str.contains('Support', regex=True)]
    df_deadlines = pd.read_csv(DEADLINES_DATA)
    
    # Table structure 
    courses = df_deadlines['Course'].unique()
    column_names = [{"name": course, "id": course, "presentation": "markdown"} for course in courses]
    teacher_rows = []  
    course_columns = {course: [] for course in courses} 

    grouped = df_deadlines.groupby(['Course', 'Teacher'])
    
    for (course, teacher), teacher_data in grouped:
        tasks = []
        block = teacher_data['Block'].iloc[0] 
        for _, row in teacher_data.iterrows():
            task = row['Task']
            due_date = row['Due']
            tasks.append(f"{task} (Due: {due_date})")
        
        teacher_entry = f"**{teacher}** - {block}\n" + "\n".join(tasks)
        course_columns[course].append(teacher_entry)

    # Compact data
    max_teachers_per_row = max(len(teacher_list) for teacher_list in course_columns.values())
    for row_idx in range(max_teachers_per_row):
        row_data = {}
        for course, teachers in course_columns.items():
            if row_idx < len(teachers):
                row_data[course] = teachers[row_idx]
            else:
                row_data[course] = "" 
        teacher_rows.append(row_data)

    return teacher_rows, column_names