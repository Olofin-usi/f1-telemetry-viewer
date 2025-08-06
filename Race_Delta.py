import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'  # Use web browser to display plot


session_race = fastf1.get_session(2021, 'Abu Dhabi', 'Q')
session_race.load()
# We choose the driver and obtain his best lap
driver_1 = session_race.laps.pick_drivers('VER').pick_fastest()
driver_2 = session_race.laps.pick_drivers('HAM').pick_fastest()

driver_1_telemetry = driver_1.get_telemetry().add_distance()
driver_2_telemetry = driver_2.get_telemetry().add_distance()

time_driver_1 = driver_1_telemetry['Time'] / np.timedelta64(1, 's')    # Time as a float variable
time_driver_2 = driver_2_telemetry['Time'] / np.timedelta64(1, 's')    # Time as a float variable

if driver_1_telemetry['Time'].iloc[-1] < driver_2_telemetry['Time'].iloc[-1]:
    baseline = driver_1
    comparison = driver_2
    label = "Driver 2 vs Driver 1"
else:
    baseline = driver_2
    comparison = driver_1
    
baseline_telemetry = baseline.get_telemetry().add_distance()
comparison_telemetry = comparison.get_telemetry().add_distance()

baseline_time = baseline_telemetry['Time'].dt.total_seconds()
comparison_time = comparison_telemetry['Time'].dt.total_seconds()




# delta = Time_driver1_at_distance - Time_driver2_at_distance
common_distance = np.linspace(0, min(baseline_telemetry['Distance'].max(), comparison_telemetry['Distance'].max()), num=1000)
baseline_interp = np.interp(common_distance, baseline_telemetry['Distance'], baseline_time)
comparison_interp = np.interp(common_distance, comparison_telemetry['Distance'], comparison_time)

# Calculate delta
delta_time = comparison_interp - baseline_interp

fig = go.Figure()


fig.add_trace(go.Scatter(x=common_distance, y=delta_time, mode='lines', name=f'Lap Delta ({comparison["Driver"]} - {baseline["Driver"]})', line=dict(color='blue')))


fig.update_layout(
    title="Interactive Lap Time and Delta Plot",
    xaxis_title="Distance (m)",
    yaxis_title="Time (s) / Delta (s)",
    hovermode="x unified",
    template="plotly_white",
    shapes=[
        dict(
            type='line',
            xref='x',
            yref='y',
            x0=common_distance[0],
            x1=common_distance[-1],
            y0=0,
            y1=0,
            line=dict(color='black', width=2)
        )
    ]
)

fig.show()

