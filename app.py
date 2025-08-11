import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fastf1 import get_session, plotting
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
gp_list = fastf1.get_event_schedule(year)['EventName'].unique().tolist()
# Select GP from dropdown
gp = st.selectbox("Select Grand Prix", gp_list)

st.write(f"Selected: {year} - {gp}")
session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"])

def get_drivers_for_event(year, gp, session_type):
    """Return list of (driver_code, team_name, team_color) for the selected event.
       This is robust to different FastF1 column names.
    """
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    results = session.results  # pandas DataFrame

    # detect likely column names (fall back to None if not present)
    team_col = next((c for c in ('Team', 'TeamName', 'Constructor') if c in results.columns), None)
    code_col = next((c for c in ('Abbreviation', 'Abbr', 'Driver') if c in results.columns), None)

    drivers = []
    for _, row in results.iterrows():
        # get driver code / abbreviation (fallback to first 3 chars of 'Driver' if needed)
        code = row.get(code_col) if code_col else None
        if (pd.isna(code) or code is None) and 'Driver' in results.columns:
            drv = row.get('Driver')
            code = (str(drv)[:3].upper()) if pd.notna(drv) else None

        # get team name safely
        team_name = row.get(team_col) if team_col else None
        if pd.isna(team_name):
            team_name = None

        # get team color from fastf1 plotting dict; default to gray
        team_color = plotting.TEAM_COLORS.get(team_name, "#999999") if team_name else "#999999"

        drivers.append((code, team_name, team_color))

    return drivers

drivers = get_drivers_for_event(year, gp, session_type)

# Let user select driver
st.subheader("Select a Driver")
cols = st.columns(4)
for i, (code, team, color) in enumerate(drivers):
    with cols[i % 4]:
        if st.button(code, key=f"driver_{code}"):
            st.session_state.selected_driver = code
    # CSS to color buttons
    st.markdown(
        f"""
        <style>
        div[data-testid="stButton"] button[kind="secondary"] {{
            background-color: {color};
            color: white;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Load Fastest Lap button
if st.button("Load Fastest Lap"):
    if "selected_driver" not in st.session_state:
        st.warning("Please select a driver first.")
    else:
        try:
            with st.spinner("Fetching data..."):
                progress = st.progress(0)

                # Load session
                session = fastf1.get_session(year, gp, session_type)
                progress.progress(20)
                session.load()
                progress.progress(50)

                # Get fastest lap for selected driver
                lap = session.laps.pick_driver(st.session_state.selected_driver).pick_fastest()
                progress.progress(70)

                # Get telemetry
                telemetry_driver = lap.get_car_data().add_distance()
                progress.progress(85)

                # Plot all visuals
                plot_track_map_plotly(year, gp, session_type, st.session_state.selected_driver, highlight_corners=True)
                plot_speed_plotly(telemetry_driver)
                plot_longitudinal_acceleration_plotly(telemetry_driver)
                plot_throttle_brake_plotly(telemetry_driver)
                plot_gear_plotly(telemetry_driver)
                plot_drs_plotly(telemetry_driver)

                progress.progress(100)
                progress.empty()

            st.success(f"✅ Telemetry loaded for {st.session_state.selected_driver}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
