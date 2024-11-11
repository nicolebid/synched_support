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
        )
    )

    fig.update_layout(
        barmode='stack', 
        title=None,
        xaxis_title='Occurences',
        yaxis_title=None,  
        template="plotly_white",  
        xaxis=dict(
            tickvals=tick_values, 
            ticktext=[str(i) for i in tick_values],
            tickangle=0
        ),
        autosize=True, 
        height=160,
        legend=dict(
            orientation='h', 
            yanchor='top', 
            y=-0.8, 
            xanchor='left',
            x=-0.2,
            itemwidth=30,
            tracegroupgap=0
        ), 
        margin=dict(l=0, r=5, t=10, b=30)
        )
    return fig 

def workhabit_timeline(selected_student=None):
    """Fuction to generate a line chart for the selected student's work habits.
    
    Parameter
    ---------
    selected_student : str
        User selected student from dropdown to generate the graph for.
    
    Returns
    -------
    fig : plotly obj 
        Plotly figure of the student's work habits.
    """
    attendance_data = pd.read_csv(ATTEND_SUPPORT_DATA)
    attendance_data['Date'] = pd.to_datetime(attendance_data['Date'])
    attendance_data = attendance_data.sort_values(by='Date')

    if selected_student == None:
        date_range_start = attendance_data['Date'].min()
        date_range_end = attendance_data['Date'].max() 
        placeholder_dates = pd.date_range(start=date_range_start, end=date_range_end, freq='D')
        attendance_filter = pd.DataFrame({'Date': placeholder_dates, 'Habit': [None] * len(placeholder_dates)})
    
    else:
        attendance_filter = attendance_data[attendance_data['Student'] == selected_student]
        # separate NaNs
        nan_dates = attendance_filter.loc[attendance_data['Habit'].isna(), 'Date']
        attendance_filter = attendance_filter.dropna(subset=['Habit'])
    
    attendance_filter = attendance_filter[['Date', 'Habit']]

    # Ordinal Categories 
    habit_categories = ['Off-task', 'Mostly Off-task', 'Mostly On-task', 'On-task', 'Excellent']
    attendance_filter['Habit'] = pd.Categorical(attendance_filter['Habit'], categories=habit_categories, ordered=True)

    # plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=attendance_filter['Date'], 
        y=attendance_filter['Habit'].cat.codes, 
        mode='lines+markers',
        line=dict(dash='dot'),
        hovertemplate="<b>Date:</b> %{x|%b-%d}<br><b>Habit:</b> %{y}<br><extra></extra>" 
    ))

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(habit_categories))), 
            ticktext=habit_categories, 
            range=[-0.5, len(habit_categories)-0.5]  
        ),
        title=None,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False, 
        xaxis=dict(
            dtick="D1", 
            tickformat="%b-%d",  
            ticks="inside",  
            showgrid=True, 
            tickangle=45 
        ),
        margin=dict(l=10, r=10, t=20, b=10), 
        template="plotly_white"
    )
    if selected_student != None:
        # red line for each NaN value
        for nan_date in nan_dates:
            fig.add_vline(x=nan_date, line=dict(color="red", width=1 ))
                # Add an annotation with hover text
            fig.add_annotation(
                x=nan_date,
                y=len(habit_categories) - 0.5,  # Position the annotation above the plot
                text="Absent",
                showarrow=True,
                ax=0,  
                ay=-10,  
                font=dict(size=12, color="red"),
                align="center",
                arrowcolor="red",
                opacity=0.7
            )
    return fig 