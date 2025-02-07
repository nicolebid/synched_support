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

def attendance_barchart(selected_student=None, overall=True):
    """Fuction to generate bar charts for the selected student's attendance record, either one
    single accumulated attendance bar chart or a bar chart for each course..
    
    Parameter
    ---------
    selected_student : str
        User selected student from dropdown, to calculate the attendance count for.
    overall: bool
        If true, generates a single bar chart for the accumulated attendance. If False, a bar chart
        for each course is returned. 
    
    Returns
    -------
    fig : plotly obj 
        Plotly figure of the attendance barchart.
    """

    # Initial Chart 
    if selected_student == None: 
        attend_percent_t = [[0], [0], [0], [0]]
        ordered_subjects=['']
        attend_counts_t  = [[0], [0], [0], [0]]   
        gap = 0    
    else:    
        # Import and set up data to plot 
        attendance = pd.read_csv(ATTEND_CLASS_DATA)
        attendance_student = attendance[attendance['Student'] == selected_student]
            
        student_attendance_dict = {}
        totals = {'P': 0, 'L': 0, 'AE': 0, 'A': 0}   

        # get attendance for each course
        for course in attendance_student['Course'].unique():
                
            attendance_course = attendance_student[attendance_student['Course'] == course]
            attendance_col = attendance_course['Attendance']
            attendance_counts = attendance_col.value_counts().to_dict()

            for key, value in totals.items():
                attendance_counts.setdefault(key, value)
                student_attendance_dict[course] = attendance_counts

        ordered_subjects = sorted(student_attendance_dict.keys(), reverse=True)
        ordered_status = ['P', 'L', 'AE', 'A']    

        # SET UP FOR OVERALL CHART   
        if overall:
            # Totals across courses 
            for key, value in student_attendance_dict.items():
                for key in totals:
                    totals[key] += value.get(key, 0) 
                
            attend_counts=[totals[status] for status in ordered_status]
            attend_counts_t=[[x] for x in attend_counts]
            attend_percent_t=[[x/sum(attend_counts)*100 if sum(attend_counts) != 0 else 0] for x in attend_counts]
            ordered_subjects=['']

            # bar gap
            gap = 0.7
        else:
        # SET UP FOR COURSE SPECIFIC CHARTS
            attend_counts = [[student_attendance_dict[subject][status] for status in ordered_status] for subject in ordered_subjects]
            attend_counts_t = [list(row) for row in zip(*attend_counts)]
            attend_percent = [[round(x/sum(lst)*100, 2) if sum(lst) != 0 else 0 for x in lst] for lst in attend_counts]
            attend_percent_t = [list(row) for row in zip(*attend_percent)]

            # bar gap
            gap = 0.2 
        
    # Plot 
    status = ['Present', 'Late', 'Excused', 'Absent']
    colors =['rgba(41, 118, 74, 0.8)', 'rgba(33, 42, 168, 0.8)', 
                'rgba(239, 164, 107, 0.8)', 'rgba(194, 27, 24, 0.8)']
        
    # plot barcharts 
    fig = go.Figure()

    for n, xd in enumerate(attend_percent_t):
        fig.add_trace(go.Bar(
            y=ordered_subjects, 
            x=xd, 
            name=status[n],
            orientation='h',
            marker=dict(
                color=colors[n],
                line=dict( width=1)
            ), 
            customdata=attend_counts_t[n], 
            hovertemplate=f'{status[n]}: %{{x:.0f}}% - %{{customdata}} time(s)<extra></extra>' 
        )) 

    fig.update_layout(
        barmode='stack', 
        template="plotly_white", 
        margin=dict(l=20, r=20, t=20, b=20), 
        xaxis=dict(
            tickvals=[0, 20, 40, 60, 80, 100], 
            ticktext=['0%', '20%', '40%', '60%', '80%', '100%'], 
        ),
        bargap=gap, 
        height=300, 
        autosize=True,
        legend=dict(
            orientation='h', 
            yanchor='top', 
            y=-0.2, 
            xanchor='left',
            x=0,
            itemwidth=30, 
            traceorder='normal'
        ),
    )
    return fig 

def attendance_barchart_none(selected_student=None):
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
        line=dict(dash='dot', color='rgba(41, 118, 74, 0.8)'),
        hovertemplate="<b>Date:</b> %{x|%b-%d}<br><b>Habit:</b> %{y}<br><extra></extra>" 
    )), 

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
            fig.add_vline(x=nan_date, line=dict(color='rgba(194, 27, 24, 0.8)', width=1 ))
                # Add an annotation with hover text
            fig.add_annotation(
                x=nan_date,
                y=len(habit_categories) - 0.5,  
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

def timespent_barchart(selected_student=None):
    """Fuction to generate a bar chart for the selected student's time spent.
    
    Parameter
    ---------
    selected_student : str
        User selected student from dropdown to generate the graph for.
    
    Returns
    -------
    fig : plotly obj 
        Plotly figure of the student's time spent.
    """
    df = pd.read_csv(ATTEND_SUPPORT_DATA)
    df_student = df[df['Student'] == selected_student]
    subjects = df_student['Work']
    all_subjects = ["Art", "English", "French", "Math", "Science", "Socials", "Other"]
    counts = subjects.value_counts()    
    all_counts = pd.Series(subjects).value_counts().reindex(all_subjects, fill_value=0)
    subject_proportion = (all_counts/counts.sum())

    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=all_subjects, 
        y=subject_proportion, 
        marker_color=colors, 
        hovertemplate=(
        "<b>%{x}</b><br>"                 
        "Count: %{customdata}<br>"     
        "Percentage: %{y:.0%}<br>"       
        "<extra></extra>"                
    ),
    customdata=all_counts.values
    ))
    fig.update_layout(
        title=None, 
        xaxis_title='Subject Worked On',
        template='plotly_white', 
        margin=dict(l=5, r=5, t=10, b=35), 
    )
    fig.update_yaxes(tickformat=".0%", 
                     title="Percentage of Time Spent",
                     range=[0,1], 
                     dtick=0.25) 
    return fig 