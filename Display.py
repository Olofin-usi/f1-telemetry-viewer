import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt



session_race = fastf1.get_session(2023, 'Silverstone', 'R')
session_race.load()
# We choose the driver and obtain his best lap
driver = 'VER'
fastest_driver = session_race.laps.pick_drivers(driver).pick_fastest()
telemetry_driver = fastest_driver.get_telemetry().add_distance()

v = telemetry_driver['Speed'] / 3.6    # Speed in m/s
time_float = telemetry_driver['Time'] / np.timedelta64(1, 's')    # Time as a float variable
ver_laps = session_race.laps.pick_drivers('VER')
Car_data = ver_laps.get_telemetry().add_distance() # getting the fastest drivers telemetry from the car_data field 




# Find gear changes by comparing consecutive rows
gear = Car_data['nGear']  # 'nGear' in older FastF1 versions
gear_changes = Car_data[gear.shift() != gear]  # Only rows where gear changes


# since the brake being on is a true/false (Boolean) its best to change it to integers
# making it easier to plot. 
telemetry_driver['Brake'] = telemetry_driver['Brake'].astype(int)
telemetry_driver['DRS'] = telemetry_driver['DRS'].astype(int) # the same is applied to DRS
 

# We calculate the longitudinal acceleration and filter it
ax = np.gradient(v)/np.gradient(time_float)
ax_smooth = np.convolve(ax, np.ones((3,))/3, mode = 'same')

plt.style.use('dark_background')

fig, axes = plt.subplots(5, 1, figsize=(12, 12))

# Speed plot
axes[0].plot(telemetry_driver['Distance'], telemetry_driver['Speed'], linewidth=2, color='cyan')
axes[0].set(xlabel="Distance (m)", ylabel="Speed (km/h)")

# Longitudinal acceleration plot
axes[1].plot(telemetry_driver['Distance'], ax, linewidth=1, label='Raw', color='orange')
axes[1].plot(telemetry_driver['Distance'], ax_smooth, linewidth=2, label='Filtered', color='lime')
axes[1].set(xlabel="Distance (m)", ylabel="Longitudinal Acceleration (m/s²)")
axes[1].legend()

# Throttle and Brake plot
axes[2].plot(telemetry_driver['Distance'], telemetry_driver['Throttle'], label='Throttle', color='green')
axes[2].plot(telemetry_driver['Distance'], telemetry_driver['Brake'] * 100, label='Brake', color='red')
axes[2].set(xlabel="Distance (m)", ylabel="Throttle / Brake (%)")
axes[2].legend()

# Gear plot
axes[3].plot(telemetry_driver['Distance'], telemetry_driver['nGear'], label='Gear', color='magenta')
axes[3].set(xlabel="Distance (m)", ylabel="Gear")
axes[3].legend()

#DRS plot
axes[4].plot(telemetry_driver['Distance'], telemetry_driver['DRS'], label='DRS', color='pink')
axes[4].set(xlabel="Distance (m)", ylabel="DRS")
axes[4].set_yticks([0, 1])
axes[4].set_yticklabels(['OFF', 'ON']) # manually set the axis to just say on or Off
axes[4].legend()

# Using plain matplotlib instead of seaborn

plt.show()