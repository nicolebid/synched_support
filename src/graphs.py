import pandas as pd
import plotly.graph_objects as go
from .config import *

def attendance_counts(selected_student=None):
    """Fuction to calculate the number of times a student was present (P), late (L), 
    absent (A) and absent-excused (AE).
    
    Parameter
    ---------
    selected_student : str
        User selected student from dropdown, to calculate the attendance count for.
    
    Returns
    -------
    attendance : dict
        Dictionary of the attendance counts.
    """
    if selected_student == None:
        return {'P': 0, 'L': 0, 'A': 0, 'AE': 0}  
    
    df = pd.read_csv(ATTEND_CLASS_DATA)
    df_student = df[df['Student'] == selected_student]
    student_attendance = df_student['Attendance']
    attendance = student_attendance.value_counts().to_dict()
    required = {'P': 0, 'L': 0, 'A': 0, 'AE': 0}   
    for key, value in required.items():
        attendance.setdefault(key, value)
    return attendance

def attendance_barchart(selected_student=None):
    """Fuction to generate a barchart for the selected student's attendance record.
    
    Parameter
    ---------
    selected_student : str
        User selected student from dropdown, to calculate the attendance count for.
    
    Returns
    -------
    fig : plotly obj 
        Plotly figure of the attendance barchart.
    """
    # obtain student attendance
    attendance = attendance_counts(selected_student)

    # Categories and their corresponding values
    categories = ['P', 'L', 'A', 'AE']
    values = [attendance[category] for category in categories]
    labels = {'P': 'Present', 'L': 'Late', 'A': 'Absent', 'AE': 'Excused'}

    # ticks
    total_classes = sum(attendance.values())
    tick_values = list(range(0, total_classes+1, 2)) 

    fig = go.Figure()

    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            x=[attendance[category]], 
            y=['']*len(categories), 
            name=labels[category], 
            hoverinfo='x+name', 
            orientation='h', 
            legendgroup=category
        ))

    fig.update_layout(
        barmode='stack', 
        title=None,
        xaxis_title=None,
        yaxis_title=None,  
        template="plotly_white",  
        xaxis=dict(
            tickvals=tick_values, 
            ticktext=[str(i) for i in tick_values],
            tickangle=0
        ),
        height=250,
        width=500, 
        legend=dict(
            orientation='h', 
            yanchor='top', 
            y=-0.5, 
            xanchor='left',
            x=-0.02,
            itemwidth=30,
            tracegroupgap=0
        )
    )

    return fig 
