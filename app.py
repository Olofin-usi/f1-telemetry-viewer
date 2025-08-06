import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fastf1 import get_session
import fastf1
from plotly_functions import (
    plot_speed_plotly,
    plot_longitudinal_acceleration_plotly,
    plot_throttle_brake_plotly,
    plot_gear_plotly,
    plot_drs_plotly
)

fastf1.Cache.enable_cache('cache')  # Local cache to speed things up

st.set_page_config(layout="wide", page_title="F1 Telemetry Viewer")

st.title("🏎️ F1 Telemetry Visualizer")

year = st.selectbox("Select Year", list(range(2021, 2025)))
gp = st.text_input("Enter Grand Prix Name (e.g. 'Monza')", value="Monza")
session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"])
driver = st.text_input("Driver Code (e.g. 'VER')", value="VER")

if st.button("Load Data"):
    try:
        session = get_session(year, gp, session_type)
        session.load()
        lap = session.laps.pick_driver(driver).pick_fastest()
        telemetry_driver = lap.get_car_data().add_distance()

        plot_speed_plotly(telemetry_driver)
        plot_longitudinal_acceleration_plotly(telemetry_driver)
        plot_throttle_brake_plotly(telemetry_driver)
        plot_gear_plotly(telemetry_driver)
        plot_drs_plotly(telemetry_driver)


    except Exception as e:
        st.error(f"Something went wrong: {e}")
