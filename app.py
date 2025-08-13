import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import fastf1
from Track_plot import plot_track_map_plotly
from plotly_functions import (
    plot_speed_plotly,
    plot_longitudinal_acceleration_plotly,
    plot_throttle_brake_plotly,
    plot_gear_plotly,
    plot_drs_plotly
)

# Enable cache for FastF1
fastf1.Cache.enable_cache('cache')

# Page settings
st.set_page_config(layout="wide", page_title="F1 Telemetry Viewer")
st.title("🏎️ F1 Telemetry Visualizer")

# Select Year
year = st.selectbox("Select Year", list(range(2019, 2025)))

# Get GP list for that year
gp_list = fastf1.get_event_schedule(year)['EventName'].unique().tolist()
gp = st.selectbox("Select Grand Prix", gp_list)

st.write(f"Selected: {year} - {gp}")
session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"])


def get_drivers_for_event(year, gp, session_type):
    """
    Return list of (driver_code, team_name, team_color) for the selected event.
    Works with all FastF1 versions and falls back to a safe default color.
    """
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    results = session.results  # pandas DataFrame

    # Detect possible column names
    team_col = next((c for c in ('Team', 'TeamName', 'Constructor') if c in results.columns), None)
    code_col = next((c for c in ('Abbreviation', 'Abbr', 'Driver') if c in results.columns), None)

    FALLBACK_TEAM_COLORS = {
        'Mercedes': '#00D2BE',
        'Ferrari': '#DC0000',
        'Red Bull': '#1E41FF',
        'Alpine': '#0090FF',
        'McLaren': '#FF8700',
        'Alfa Romeo': '#900000',
        'Aston Martin': '#006F62',
        'Haas': '#FFFFFF',
        'AlphaTauri': '#2B4562',
        'Alpha Tauri': '#2B4562',
        'Williams': '#005AFF'
    }

    try:
        from fastf1.plotting import team_color as get_team_color
    except ImportError:
        get_team_color = None

    drivers = []
    for _, row in results.iterrows():
        # Driver code
        code = row.get(code_col) if code_col else None
        if (pd.isna(code) or code is None) and 'Driver' in results.columns:
            drv = row.get('Driver')
            code = (str(drv)[:3].upper()) if pd.notna(drv) else None

        # Team name
        team_name = row.get(team_col) if team_col else None
        if pd.isna(team_name):
            team_name = None

        # Team color
        if team_name:
            if get_team_color:
                try:
                    team_color_hex = get_team_color(team_name)
                except Exception:
                    team_color_hex = FALLBACK_TEAM_COLORS.get(team_name, "#999999")
            else:
                team_color_hex = FALLBACK_TEAM_COLORS.get(team_name, "#999999")
        else:
            team_color_hex = "#999999"

        drivers.append((code, team_name, team_color_hex))

    return drivers


# Get drivers list
drivers = get_drivers_for_event(year, gp, session_type)

# --- Clean F1Tempo-style Driver Dropdown ---
st.subheader("Select a Driver")

# Build HTML-colored labels
driver_labels_html = [
    f"<span style='color:{color}; font-weight:bold;'>{code}</span>"
    for code, _, color in drivers
]
driver_map = {html: code for html, (code, _, _) in zip(driver_labels_html, drivers)}

# Streamlit selectbox with HTML labels
selected_driver_html = st.selectbox(
    "Drivers...",
    driver_labels_html,
    format_func=lambda x: x,
    label_visibility="collapsed"
)

# Store selected driver code
st.session_state.selected_driver = driver_map[selected_driver_html]

# --- Load Fastest Lap Button ---
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

                # Get fastest lap
                lap = session.laps.pick_driver(st.session_state.selected_driver).pick_fastest()
                progress.progress(70)

                # Get telemetry
                telemetry_driver = lap.get_car_data().add_distance()
                progress.progress(85)

                # Plot visuals
                plot_track_map_plotly(year, gp, session_type, st.session_state.selected_driver, highlight_corners=True)
                plot_speed_plotly(telemetry_driver)
                plot_longitudinal_acceleration_plotly(telemetry_driver)
                plot_throttle_brake_plotly(telemetry_driver)
                plot_gear_plotly(telemetry_driver)
                plot_drs_plotly(telemetry_driver)

                progress.progress(100)
                progress.empty()

        except Exception as e:
            st.error(f"Something went wrong: {e}")
