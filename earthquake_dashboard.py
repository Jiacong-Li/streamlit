import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

#-------Preparation-----
st.set_page_config(page_title='Earthquake Data Dashboard',
                  page_icon=':bar_chart:',
                  layout='wide')

file_path = "earthquake_2019-2024.xlsx"
data = pd.read_excel(file_path)

# Plot the Logo
st.image('RSG.png')
# Header of the Dashboard
st.title("Earthquake Data Dashboard :bar_chart:")
st.markdown(
    """
    <p style='font-size:12px'>
    Data source: <a href="https://earthquake.usgs.gov/earthquakes/search/">https://earthquake.usgs.gov/earthquakes/search/</a>
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown('----')
#------Filter--------
# Filter data using dropdown menus for three columns
st.sidebar.subheader(":pushpin: Filter Your Data:")
columns = data.columns.tolist()

# Create three dropdown menus
selected_column1 = columns[9]
selected_column2 = columns[10]
selected_column3 = columns[14]

# Get unique values for each selected column and create multiselect widgets
unique_values1 = data[selected_column1].unique()
unique_values2 = data[selected_column2].unique()
unique_values3 = data[selected_column3].unique()

selected_values1 = st.sidebar.multiselect(f"Select values for **{selected_column1}**", unique_values1)
selected_values2 = st.sidebar.multiselect(f"Select values for **{selected_column2}**", unique_values2)
selected_values3 = st.sidebar.multiselect(f"Select values for **{selected_column3}**", unique_values3)

# Date range selector
st.sidebar.subheader(":calendar: Select Date Range:")
start_date = pd.to_datetime(st.sidebar.date_input("Start date",
                                          value=pd.to_datetime(data['Date']).min(),
                                          min_value=pd.to_datetime(data['Date']).min(),
                                          max_value=pd.to_datetime(data['Date']).max()))
end_date = pd.to_datetime(st.sidebar.date_input("End date", 
                                          value=pd.to_datetime(data['Date']).max(),
                                          min_value=pd.to_datetime(data['Date']).min(),
                                          max_value=pd.to_datetime(data['Date']).max()))

# Filter the data based on the selected values
filtered_data = data.copy()

if selected_values1:
    filtered_data = filtered_data[filtered_data[selected_column1].isin(selected_values1)]
if selected_values2:
    filtered_data = filtered_data[filtered_data[selected_column2].isin(selected_values2)]
if selected_values3:
    filtered_data = filtered_data[filtered_data[selected_column3].isin(selected_values3)]

# Filter by date range
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
filtered_data = filtered_data[(filtered_data['Date'] >= start_date) & (filtered_data['Date'] <= end_date)]

st.subheader("Preivew of Selected Data")
st.dataframe(filtered_data.head())
st.markdown('----')

#-------Main-------
# 1. Basic Stats
mag_mean = filtered_data['Mag'].mean().round(2)
mag_max = filtered_data['Mag'].max()
mag_min = filtered_data['Mag'].min()

dep_mean = filtered_data['Depth'].mean().round(2)
dep_max = filtered_data['Depth'].max()
dep_min = filtered_data['Depth'].min()

col1,col2 = st.columns(2)
with col1:
 st.subheader("**Average Magnitude:**")
 st.markdown(f"**{mag_mean}**")
 st.subheader("**Range of Magnitude:**")
 st.markdown(f"**({mag_min} , {mag_max})**")
with col2:
 st.subheader("**Average Magnitude:**")
 st.markdown(f"**{dep_mean}**")
 st.subheader("**Range of Depth:**")
 st.markdown(f"**({dep_min} , {dep_max})**")

max_date = filtered_data[filtered_data['Mag']==mag_max]['Date'].unique()[0]
dis_date = filtered_data[filtered_data['Mag']==mag_max]['Date'].dt.date.to_list()[0]
max_loc = filtered_data[(filtered_data['Date']==max_date) & (filtered_data['Mag'] == mag_max)]['Area'].unique()
max_loc_str = ', '.join(max_loc)

st.write(f":mag: The highest magnitude earthquake happened on &nbsp; **{dis_date}**  &nbsp; at &nbsp; **{max_loc_str}**.")
st.markdown('---')

# 2. Distribution of Mag and Dep
st.subheader('Distribution of Earthquake Magnitude & Depth')
col1, col2 = st.columns(2)

# First column: Magnitude Histogram
with col1:
    fig1 = px.histogram(filtered_data, x='Mag', nbins=50, 
                        labels={'Mag':'Magnitude'},
                        template='plotly_dark')
    fig1.update_layout(yaxis_title='Frequency')
    fig1.update_traces(marker_line_color='black', marker_line_width=1.5)
    st.plotly_chart(fig1, use_container_width=True)

# Second column: Depth Histogram
with col2:
    fig2 = px.histogram(filtered_data, x='Depth', nbins=50, 
                        template='plotly_dark')
    fig2.update_layout(yaxis_title='Frequency')
    fig2.update_traces(marker_line_color='black', marker_line_width=1.5)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('---')

# 3. Top 15 Area with most earthquake
st.subheader("Top 15 Areas by Earthquake Frequency")
mag_count_list = filtered_data.groupby(by=['Area'],dropna=True,as_index=False).count()[['Area','Mag']].sort_values(by='Mag',ascending=False).iloc[0:14]
mag_count_list.sort_values(by='Mag',ascending=True,inplace=True)
top_area_fig = px.bar(mag_count_list,x='Mag',y='Area',orientation='h',color_discrete_sequence=['CadetBlue'])

top_area_fig.update_layout(
    xaxis_title='Number of Earthquakes',
    yaxis_title='Area'
)

st.plotly_chart(top_area_fig)
st.markdown("---")

# 4.Pie Chart -- Show percentage of differenct type
st.subheader("Proportion of Earthquake Magnitude Types")
magtype_list = filtered_data.groupby(by=['Magtype'],dropna=True,as_index=False).count()[['Magtype','Mag']].sort_values(by='Mag',ascending=False)
magtype_pie_fig = px.pie(magtype_list, values='Mag', names='Magtype')
st.plotly_chart(magtype_pie_fig)


#-------END------
# Definitions for each columns
st.markdown('----')
whole_columns = data.columns.to_list()
column_definitions = {
    "Column Name": whole_columns,
    "Definition": [
    "Time when the event occurred ",
    "The depth where the earthquake begins to rupture",
    "The magnitude for the event",
    "The method or algorithm used to calculate the preferred magnitude for the event.",
    "The total number of seismic stations used to determine earthquake location.",
    "The largest azimuthal gap between azimuthally adjacent stations (in degrees).In general, the smaller this number, the more reliable is the calculated horizontal position of the earthquake.  ",
    "Horizontal distance from the epicenter to the nearest station (in degrees). 1 degree is approximately 111.2 kilometers. In general, the smaller this number, the more reliable is the calculated depth of the earthquake.",
    "The root-mean-square (RMS) travel time residual, in sec, using all weights.",
    "The ID of a data contributor. Identifies the network considered to be the preferred source of information for this event.",
    "Area where the event occurred",
    "Type of the event",
    "Uncertainty of reported depth of the event in kilometers.",
    "Uncertainty of reported magnitude of the event.",
    "The total number of seismic stations used to calculate the magnitude for this earthquake.",
    "Indicates whether the event has been reviewed by a human.",
    "The network that originally authored the reported location of this event.",
    "Network that originally authored the reported magnitude for this event."
    ]
}

st.markdown(
    """
    <style>
    .small-text table {
        font-size: 12px ;
        color: grey
    }
    </style>
    """,
    unsafe_allow_html=True
)

columns_def = pd.DataFrame(column_definitions)
# Convert the DataFrame to HTML
columns_def_html = columns_def.to_html(index=False)

# Inject custom CSS and HTML


# Display the definitions table at the end of the dashboard with custom styling
st.write("Column Definition")
st.markdown(f'<div class="small-text">{columns_def_html}</div>', unsafe_allow_html=True)

