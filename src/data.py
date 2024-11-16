import pandas as pd
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
    courses = df['Course'].unique()
    options = [{'label': name, 'value': name} for name in courses]
    return options 

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