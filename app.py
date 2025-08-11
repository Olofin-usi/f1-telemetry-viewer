import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fastf1 import get_session
import fastf1
from Track_plot import plot_track_map_plotly
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

# Select Year
year = st.selectbox("Select Year", list(range(2019, 2025)))

# Get GP list for that year
schedule = fastf1.get_event_schedule(year)
gp_list = schedule['EventName'].unique().tolist()

# Select GP from dropdown
gp = st.selectbox("Select Grand Prix", gp_list)

st.write(f"Selected: {year} - {gp}")
session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"])
driver = st.text_input("Driver Code (e.g. 'VER')", value="VER")

if st.button("Load Fastest Lap"):
    try:
                # Spinner to indicate loading process
        with st.spinner("Fetching fastest lap data..."):
            progress = st.progress(0)

            # Step 1: Load session
            session = get_session(year, gp, session_type)
            progress.progress(20)
            session.load()
            progress.progress(50)

            # Step 2: Get fastest lap
            lap = session.laps.pick_driver(driver).pick_fastest()
            progress.progress(70)

            # Step 3: Get telemetry
            telemetry_driver = lap.get_car_data().add_distance()
            progress.progress(85)

        plot_track_map_plotly(year, gp, session_type, driver, highlight_corners=True)
        plot_speed_plotly(telemetry_driver)
        plot_longitudinal_acceleration_plotly(telemetry_driver)
        plot_throttle_brake_plotly(telemetry_driver)
        plot_gear_plotly(telemetry_driver)
        plot_drs_plotly(telemetry_driver)
        progress.progress(100)

        st.success("✅ Telemetry loaded successfully!")


    except Exception as e:
        st.error(f"Something went wrong: {e}")
