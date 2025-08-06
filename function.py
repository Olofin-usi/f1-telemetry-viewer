import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt
import Track_plot
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"

session_race = fastf1.get_session(2025, 'silverstone','Q')
session_race.load()
# Get the overall fastest lap of the session (regardless of driver)
fastest_lap = session_race.laps.pick_fastest()
fastest_driver = fastest_lap['Driver']
telemetry_driver = fastest_lap.get_telemetry().add_distance()

def plot_speed(ax, telemetry_driver):
    ax.plot(telemetry_driver['Distance'], telemetry_driver['Speed'], linewidth=2, color='cyan')
    ax.set(xlabel="Distance (m)", ylabel="Speed (km/h)")
    
def plot_longitudinal_acceleration(ax, telemetry_driver):
    v = telemetry_driver['Speed'] / 3.6  # Speed in m/s
    time_float = telemetry_driver['Time'] / np.timedelta64(1, 's')  # Time in seconds
    ax_raw = np.gradient(v) / np.gradient(time_float)
    ax_smooth = np.convolve(ax_raw, np.ones((3,)) / 3, mode='same')
    
    ax.plot(telemetry_driver['Distance'], ax_raw, linewidth=1, label='Raw', color='orange')
    ax.plot(telemetry_driver['Distance'], ax_smooth, linewidth=2, label='Filtered', color='lime')
    ax.set(xlabel="Distance (m)", ylabel="Long Acceleration (m/s²)")
    ax.legend()
    
def plot_throttle_brake(ax, telemetry_driver):
    telemetry_driver['Brake'] = telemetry_driver['Brake'].astype(int)
    ax.plot(telemetry_driver['Distance'], telemetry_driver['Throttle'], label='Throttle', color='green')
    ax.plot(telemetry_driver['Distance'], telemetry_driver['Brake'] * 100, label='Brake', color='red')
    ax.set(xlabel="Distance (m)", ylabel="Throttle / Brake (%)")
    ax.legend()
    
def plot_gear(ax, telemetry_driver):
    ax.plot(telemetry_driver['Distance'], telemetry_driver['nGear'], label='Gear', color='magenta')
    ax.set(xlabel="Distance (m)", ylabel="Gear")
    ax.legend()
    
def plot_drs(ax, telemetry_driver):
    telemetry_driver['DRS'] = telemetry_driver['DRS'].fillna(0).apply(lambda x: 1 if x >= 10 else 0)
    ax.plot(telemetry_driver['Distance'], telemetry_driver['DRS'], label='DRS', color='pink')
    ax.set(xlabel="Distance (m)", ylabel="DRS")
    
    # Lock the ticks in place
    ax.set_ylim(-0.2, 1.2)  # This gives breathing room around 0 and 1
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['OFF', 'ON'])
    ax.legend()
    



plt.style.use('dark_background')

fig, axes = plt.subplots(6, 1, figsize=(14, 24)) 

# Add spacing between subplots
plt.subplots_adjust(hspace=0.5)  # More vertical space between plots

# Call your plot functions
plot_speed(axes[1], telemetry_driver)
plot_longitudinal_acceleration(axes[2], telemetry_driver)
plot_throttle_brake(axes[3], telemetry_driver)
plot_gear(axes[4], telemetry_driver)
plot_drs(axes[5], telemetry_driver)

Track_plot.plot_track_map(axes[0], session=session_race, driver=fastest_driver)


plt.show()
