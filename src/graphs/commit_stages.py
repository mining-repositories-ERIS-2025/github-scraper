import plotly.graph_objects as go

data = {
    "stage 1": 1318263,
    "stage 2": 197408,
    "stage 3": 197408,
    "stage 4": 2468,
    "stage 5": 1069,
}

# Extract stages (x-axis) and values (y-axis) from the dictionary
stages = list(data.keys())
values = list(data.values())

# Create the line graph
fig = go.Figure(data=go.Scatter(x=stages, y=values, mode='lines+markers'))

# Add titles and labels, and set y-axis to logarithmic scale
fig.update_layout(
    title='Stage Data Line Graph (Logarithmic Y-Axis)',
    xaxis_title='Stage',
    yaxis_title='Value (Log Scale)',
    yaxis_type='log',  # <--- This line sets the y-axis to logarithmic
    hovermode='x unified'
)

# Make the graph visually appealing
fig.update_traces(marker=dict(size=8), line=dict(width=3))

# Show the graph
fig.write_image("stage_graph_log.png")