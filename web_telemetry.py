import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt
import Track_plot
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go

pio.renderers.default = "browser"

session_race = fastf1.get_session(2025, 'silverstone','Q')
session_race.load()
# Get the overall fastest lap of the session (regardless of driver)
fastest_lap = session_race.laps.pick_fastest()
fastest_driver = fastest_lap['Driver']
telemetry_driver = fastest_lap.get_telemetry().add_distance()



# Create the figure
fig = go.Figure()

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    subplot_titles=("Speed (km/h)", "Throttle (%)")
)

# Add speed trace
fig.add_trace(go.Scatter(
    x=telemetry_driver['Distance'],
    y=telemetry_driver['Speed'],
    mode='lines',
    name='Speed',
    line=dict(color='#FF2E63', width=2),  # You can change the color/style
    hovertemplate='Distance: %{x:.1f} m<br>Speed: %{y:.1f} km/h<extra></extra>'
),row=1, col=1)

fig.add_trace(go.Scatter(
    x=telemetry_driver['Distance'],
    y=telemetry_driver['Throttle'],
    mode='lines',
    name='Throttle (%)',
    line=dict(color="#70FF2E", width=2),  # You can change the color/style
    hovertemplate='Distance: %{x:.1f} m<br>Speed: %{y:.1f} km/h<extra></extra>'
),row=2, col=1)

# Update layout
fig.update_layout(
    template='plotly_dark',  # Dark background
    height=600,
    margin=dict(l=60, r=30, t=50, b=40),
    showlegend=False,
    xaxis2_title='Distance (m)'  # x-axis label on the bottom subplot
)


# Show plot
fig.show()