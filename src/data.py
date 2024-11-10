import pandas as pd
from .config import STUDENT_DATA

# load student data
def student_list():
    """Retrieves the list of student names in the CSV file then formats them into a list
    to use in the drop down selection component. 
    
    Returns:
    -------- 
    list : A list of dictionaries containing labels and values to correspond to each 
            student in the dataset, to be used as the dropdown options."""

    df = pd.read_csv(STUDENT_DATA)
    student_names = df['Student'].unique()

    # Drop down options
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




    