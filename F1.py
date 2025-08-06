#The packages needed are imported
import fastf1 as ff1
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt


# Enable the cache by providing the name of the cache folder
ff1.Cache.enable_cache('cache')

# Setup plotting
plotting.setup_mpl()

# We choose the session and load it
session = ff1.get_session(2022, 'Abu Dhabi', 'Q')
session.load()

# We choose the driver and obtain his best lap
driver = 'VER'
fastest_driver = session.laps.pick_drivers(driver).pick_fastest()
telemetry_driver = fastest_driver.get_telemetry().add_distance()

v = telemetry_driver['Speed'] / 3.6    # Speed in m/s
time_float = telemetry_driver['Time'] / np.timedelta64(1, 's')    # Time as a float variable

# We calculate the longitudinal acceleration and filter it
ax = np.gradient(v)/np.gradient(time_float)
ax_smooth = np.convolve(ax, np.ones((3,))/3, mode = 'same')

fig, axes = plt.subplots(2, 1, figsize=(12, 12))
axes[0].plot(telemetry_driver['Distance'], telemetry_driver['Speed'], linewidth = 2)
axes[0].set(xlabel = "Distance (m)", ylabel = "Speed (km/h)")

axes[1].plot(telemetry_driver['Distance'], ax, linewidth = 1, label = 'Raw')
axes[1].plot(telemetry_driver['Distance'], ax_smooth, linewidth = 2, label = 'Filtered')
axes[1].set(xlabel = "Distance (m)", ylabel = "Longitudinal Acceleration (m/s^2)")
axes[1].legend()

m = 798    #kg
g = 9.81

staticWeightTot = m*g

fractionWeightFront = 0.46

staticWeightFront = fractionWeightFront*staticWeightTot
staticWeightRear  = staticWeightTot - staticWeightFront

# III Model: the effect of drag and downforce are added

rho = 1.225
CdA = 1.7               #Drag Coefficient * Frontal Area
efficiency = 3.7
ClA = efficiency*CdA    #Downforce Coefficient * Frontal Area

dragHeight = 0.5 #Height at which the drag force is applied

# We compute the drag and downforce
dragForce = 0.5*CdA*rho*np.square(v)
downForce = 0.5*ClA*rho*np.square(v)

fractionDownforceFront = 0.4    # Front downforce as a fraction of the total downforce (Aero balance)

downForceFront = fractionDownforceFront*downForce
downForceRear = (1 - fractionDownforceFront)*downForce

# II Model: Inertial Load Transfer added
CoGheight = 0.25   #m
wheelbase = 3.6    #m

deltaLoad = -CoGheight/wheelbase*m*ax_smooth    #Positive Longitudinal Acceleration -> Load shifts to the rear axle (deltaLoad < 0)

loadFront_loadTransferModel = staticWeightFront + deltaLoad
loadRear_loadTransferModel  = staticWeightRear  - deltaLoad
deltaLoadbyDrag = - dragHeight/wheelbase*dragForce    #Always negative: the drag shifts the load from the front to the rear!

loadFront_loadTransferAeroModel = loadFront_loadTransferModel + downForceFront + deltaLoadbyDrag
loadRear_loadTransferAeroModel  = loadRear_loadTransferModel  + downForceRear  - deltaLoadbyDrag



fig, axes = plt.subplots(1)
plt.plot(telemetry_driver['Distance'], dragForce, label = 'Drag (N)')
plt.plot(telemetry_driver['Distance'], downForce, label = 'Total Downforce (N)')
plt.legend()

plot_ratios = [1, 1, 3]

fig, axes = plt.subplots(3, 1, figsize=(16, 16), gridspec_kw={'height_ratios': plot_ratios})
axes[0].plot(telemetry_driver['Distance'], telemetry_driver['Speed'], linewidth = 2)
axes[0].set(xlabel = "Distance (m)", ylabel = "Speed (km/h)")

axes[1].plot(telemetry_driver['Distance'], ax_smooth, linewidth = 2)
axes[1].set(xlabel = "Distance (m)", ylabel = "Longitudinal Acceleration (m/s^2)")

axes[2].plot(telemetry_driver['Distance'], loadFront_loadTransferModel, '--r', linewidth = 2, label = 'Front (Load Transfer Model)')
axes[2].plot(telemetry_driver['Distance'], loadRear_loadTransferModel, '--b',  linewidth = 2, label = 'Rear  (Load Transfer Model)')
axes[2].plot(telemetry_driver['Distance'], loadFront_loadTransferAeroModel, ':r', linewidth = 2, label = 'Front (Load Transfer Model with Aero)')
axes[2].plot(telemetry_driver['Distance'], loadRear_loadTransferAeroModel, ':b',  linewidth = 2, label = 'Rear  (Load Transfer Model with Aero)')
axes[2].set(xlabel = "Distance (m)", ylabel = "Vertical Load (N)")
axes[2].legend()

plt.show()





