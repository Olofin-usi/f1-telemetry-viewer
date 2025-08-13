import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import fastf1
from Track_plot import plot_track_map_plotly
from plotly_functions import (
    plot_speed_plotly,
    plot_longitudinal_acceleration_plotly,
    plot_throttle_brake_plotly,
    plot_gear_plotly,
    plot_drs_plotly
)

# Enable cache
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
    Fast driver list using only classification data.
    Works without loading full telemetry.
    """
    session = fastf1.get_session(year, gp, session_type)

    # This fetches only classification data (fast)
    classification = session.get_classification()

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
    for _, row in classification.iterrows():
        code = row.get('Abbreviation') or row.get('Driver')
        if pd.notna(code):
            code = str(code).upper()[:3]
        else:
            code = None

        team_name = row.get('TeamName') or row.get('Constructor')
        if pd.isna(team_name):
            team_name = None

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


# Get drivers quickly
drivers = get_drivers_for_event(year, gp, session_type)

# Default selection
if "driver_selection" not in st.session_state:
    st.session_state.driver_selection = drivers[0][0] if drivers else ""

# --- Colored HTML dropdown ---
st.subheader("Select a Driver")

options_html = "".join(
    [f"<option value='{code}' style='color:{color}; font-weight:bold;' {'selected' if code == st.session_state.driver_selection else ''}>{code}</option>"
     for code, _, color in drivers]
)

dropdown_html = f"""
<select id="driver_select" style="
    padding:8px; 
    font-size:16px; 
    border-radius:5px; 
    width:120px;
    background-color:#111;
    color:white;
">
    {options_html}
</select>

<script>
    const selectEl = document.getElementById("driver_select");
    selectEl.addEventListener("change", function() {{
        const selected = selectEl.value;
        window.parent.postMessage({{"type": "driver_selection", "value": selected}}, "*");
    }});
</script>
"""

components.html(dropdown_html, height=50)

# Handle incoming selection
def handle_selection():
    import streamlit.runtime.scriptrunner as scriptrunner
    ctx = scriptrunner.get_script_run_ctx()
    # This is a placeholder — in production, you’d use custom components or query params

# --- Load Fastest Lap ---
if st.button("Load Fastest Lap"):
    selected_driver = st.session_state.driver_selection
    if not selected_driver:
        st.warning("Please select a driver first.")
    else:
        try:
            with st.spinner("Fetching data..."):
                progress = st.progress(0)
                session = fastf1.get_session(year, gp, session_type)
                session.load()  # Full load now
                progress.progress(30)

                lap = session.laps.pick_driver(selected_driver).pick_fastest()
                progress.progress(60)

                telemetry_driver = lap.get_car_data().add_distance()
                progress.progress(80)

                plot_track_map_plotly(year, gp, session_type, selected_driver, highlight_corners=True)
                plot_speed_plotly(telemetry_driver)
                plot_longitudinal_acceleration_plotly(telemetry_driver)
                plot_throttle_brake_plotly(telemetry_driver)
                plot_gear_plotly(telemetry_driver)
                plot_drs_plotly(telemetry_driver)

                progress.progress(100)
                progress.empty()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
