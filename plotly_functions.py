import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt
import Track_plot
import plotly.graph_objects as go
import plotly.io as pio


import plotly.graph_objects as go
import numpy as np
import streamlit as st

def plot_speed_plotly(telemetry_driver): # this a a plotly functions that retrieves the drivers speed from Fast f1 and plots it 
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['Speed'],
        mode='lines',
        name='Speed',
        line=dict(color='cyan')
    ))
    fig.update_layout( # naming my xaxis and my yaxis 
        template="plotly_dark",
        title="Speed vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_longitudinal_acceleration_plotly(telemetry_driver):
    v = telemetry_driver['Speed'] / 3.6  # convertinng the speed into m/s 
    time_float = telemetry_driver['Time'] / np.timedelta64(1, 's')  #  getting our time and ensurinf its in seconds
    ax_raw = np.gradient(v) / np.gradient(time_float) # since accceleratition is Dv/Dx, change in volocity over time. we take that derivative
    ax_smooth = np.convolve(ax_raw, np.ones((3,)) / 3, mode='same') # this smooths that acceleration using a 3-point moving average to reduce noise.

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=ax_raw,
        mode='lines',
        name='Raw',
        line=dict(color='orange')
    ))
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=ax_smooth,
        mode='lines',
        name='Filtered',
        line=dict(color='lime')
    ))
    fig.update_layout( # Graph properties
        template="plotly_dark",
        title="Longitudinal Acceleration vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Long Acceleration (m/s²)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_throttle_brake_plotly(telemetry_driver): # throttle vs Braje plot
    telemetry_driver['Brake'] = telemetry_driver['Brake'].astype(int) * 100 # since in Fastf1 brake is binarry on/off rather than in percentages like the throttle
    # i simply multiply it by 100 to have a work around 

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['Throttle'],
        mode='lines',
        name='Throttle',
        line=dict(color='green')
    ))
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['Brake'],
        mode='lines',
        name='Brake',
        line=dict(color='red')
    ))
    fig.update_layout( # Graph Properties
        template="plotly_dark",
        title="Throttle and Brake vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Throttle / Brake (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True) # this make the plot automatically fill the page width.


def plot_gear_plotly(telemetry_driver): # This displays what  gear they were  along the lap.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'], # x is the distance 
        y=telemetry_driver['nGear'], # the y axis is the gear 
        mode='lines',
        name='Gear',
        line=dict(color='magenta')
    ))
    fig.update_layout(
        template="plotly_dark",
        title="Gear vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Gear",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True) # Graph Properties


def plot_drs_plotly(telemetry_driver):
    telemetry_driver['DRS'] = telemetry_driver['DRS'].fillna(0).apply(lambda x: 1 if x >= 10 else 0) # This line replaces with zero, because FastF1 records Drs from 0 - 12.
    # then converts the column so any value ≥ 10 is marked as 1 (DRS active) and everything else as 0 (DRS off).
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['DRS'],
        mode='lines',
        name='DRS',
        line=dict(color='pink')
    ))
    fig.update_layout( # Graph Properties
        template="plotly_dark",
        title="DRS vs Distance",
        xaxis_title="Distance (m)",
        yaxis=dict(
            title="DRS",
            tickmode='array',
            tickvals=[0, 1], # Drs is similar to the brake, its either on or off, and since its on the y axis 
            ticktext=['OFF', 'ON'], # its ticks are between 1(ON) and 0(OFF)
            range=[-0.2, 1.2]
        ),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
def plot_laptimes(session, driver_code):
    import plotly.graph_objects as go

    fig = go.Figure()

    # Get tire compound colors
    compound_colors = fastf1.plotting.get_compound_mapping(session=session)

    # Get laps for selected driver
    driver_laps = session.laps.pick_driver(driver_code).pick_quicklaps().reset_index()

    # Convert LapTime to seconds
    driver_laps["LapTimeSeconds"] = driver_laps["LapTime"].dt.total_seconds()

    # Plot each compound
    for compound, group in driver_laps.groupby("Compound"):
        fig.add_trace(go.Scatter(
            x=group["LapNumber"],
            y=group["LapTimeSeconds"],     # ✅ use seconds
            mode="markers+lines",
            marker=dict(size=8),
            line=dict(width=1),
            name=f"{driver_code} - {compound}",
            marker_color=compound_colors.get(compound, "white")
        ))

    # Format axis ticks as mm:ss.s
    ticks = sorted(driver_laps["LapTimeSeconds"].round(1).unique())
    tick_labels = [f"{int(t//60)}:{t%60:05.2f}" for t in ticks]

       # Clean Y-axis: automatic ticks, formatted mm:ss.s
    fig.update_yaxes(
        autorange=True,
        tickformat="%M:%S.%L"   # minutes:seconds.milliseconds
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time",
        height=500,
        legend_title="Driver - Compound"
    )

    return fig


