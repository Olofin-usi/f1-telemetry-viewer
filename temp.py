import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt

session_race = fastf1.get_session(2021, 'Abu Dhabi', 'Q')
session_race.load()

# Choose drivers and get best laps
driver_1 = session_race.laps.pick_drivers('VER').pick_fastest()
driver_2 = session_race.laps.pick_drivers('HAM').pick_fastest()

driver_1_telemetry = driver_1.get_telemetry().add_distance()
driver_2_telemetry = driver_2.get_telemetry().add_distance()

time_driver_1 = driver_1_telemetry['Time'] / np.timedelta64(1, 's')
time_driver_2 = driver_2_telemetry['Time'] / np.timedelta64(1, 's')

# Decide baseline (fastest driver)
if driver_1_telemetry['Time'].iloc[-1] < driver_2_telemetry['Time'].iloc[-1]:
    baseline = driver_1
    comparison = driver_2
else:
    baseline = driver_2
    comparison = driver_1

baseline_telemetry = baseline.get_telemetry().add_distance()
comparison_telemetry = comparison.get_telemetry().add_distance()

baseline_time = baseline_telemetry['Time'].dt.total_seconds()
comparison_time = comparison_telemetry['Time'].dt.total_seconds()

# Interpolate times over common distance
common_distance = np.linspace(0, min(baseline_telemetry['Distance'].max(), comparison_telemetry['Distance'].max()), num=1000)
baseline_interp = np.interp(common_distance, baseline_telemetry['Distance'], baseline_time)
comparison_interp = np.interp(common_distance, comparison_telemetry['Distance'], comparison_time)

# Calculate delta time
delta_time = comparison_interp - baseline_interp

# Plot everything on the same axes
plt.figure(figsize=(14,8))

plt.plot(common_distance, baseline_interp, label=f"Baseline: {baseline['Driver']}", color='blue', linewidth=2)
plt.plot(common_distance, comparison_interp, label=f"Comparison: {comparison['Driver']}", color='red', linewidth=2)
plt.plot(common_distance, delta_time, label=f"Lap Delta ({comparison['Driver']} - {baseline['Driver']})", color='green', linewidth=2)

plt.axhline(0, color='black', linestyle='--', linewidth=1, label='Zero Delta Line')

plt.xlabel("Distance (m)")
plt.ylabel("Time (s) / Delta Time (s)")
plt.title("Driver Lap Times and Lap Delta vs Distance")
plt.legend()
plt.grid(True)
plt.show()
