import os

# Directories
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# file paths 
STUDENT_DATA = os.path.join(DATA_DIR, 'student.csv')
ATTEND_DATA = os.path.join(DATA_DIR, 'attendance_class_data_edit.csv')
# ATTEND_SUPPORT_DATA = os.path.join(DATA_DIR, 'attendance_class_data_edit.csv')
DEADLINES_DATA = os.path.join(DATA_DIR, 'deadlines.csv')
