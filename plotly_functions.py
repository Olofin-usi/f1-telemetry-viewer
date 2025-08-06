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

def plot_speed_plotly(telemetry_driver):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['Speed'],
        mode='lines',
        name='Speed',
        line=dict(color='cyan')
    ))
    fig.update_layout(
        template="plotly_dark",
        title="Speed vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_longitudinal_acceleration_plotly(telemetry_driver):
    v = telemetry_driver['Speed'] / 3.6  # m/s
    time_float = telemetry_driver['Time'] / np.timedelta64(1, 's')  # seconds
    ax_raw = np.gradient(v) / np.gradient(time_float)
    ax_smooth = np.convolve(ax_raw, np.ones((3,)) / 3, mode='same')

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
    fig.update_layout(
        template="plotly_dark",
        title="Longitudinal Acceleration vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Long Acceleration (m/s²)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_throttle_brake_plotly(telemetry_driver):
    telemetry_driver['Brake'] = telemetry_driver['Brake'].astype(int) * 100

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
    fig.update_layout(
        template="plotly_dark",
        title="Throttle and Brake vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Throttle / Brake (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_gear_plotly(telemetry_driver):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['nGear'],
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
    st.plotly_chart(fig, use_container_width=True)


def plot_drs_plotly(telemetry_driver):
    telemetry_driver['DRS'] = telemetry_driver['DRS'].fillna(0).apply(lambda x: 1 if x >= 10 else 0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=telemetry_driver['Distance'],
        y=telemetry_driver['DRS'],
        mode='lines',
        name='DRS',
        line=dict(color='pink')
    ))
    fig.update_layout(
        template="plotly_dark",
        title="DRS vs Distance",
        xaxis_title="Distance (m)",
        yaxis=dict(
            title="DRS",
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['OFF', 'ON'],
            range=[-0.2, 1.2]
        ),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
