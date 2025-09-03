# importing librabries and also functions made in other files.
import streamlit as st                        
import streamlit.components.v1 as components
import pandas as pd
import fastf1
import json
import os
from Track_plot import plot_track_map_plotly
from plotly_functions import (
    plot_laptimes,
    plot_speed_plotly,
    plot_longitudinal_acceleration_plotly,
    plot_throttle_brake_plotly,
    plot_gear_plotly,
    plot_drs_plotly
)

# Enable cache
fastf1.Cache.enable_cache('cache')

# --- Persistent driver DB file ---
DRIVER_DB_FILE = "driver_db.json" # Driver database file. 

# Load DB from disk if exists
if os.path.exists(DRIVER_DB_FILE): # i noticed after testing the web app, it was slow in tetching driver data, so a fix was to create a simple database for each call you make
    # ^ the above code checks if the file exists, if it does it loads it loads the contents of the JSON file into the Python variable DRIVER_DB (pyhton Dictionary)
    with open(DRIVER_DB_FILE, "r") as f:
        DRIVER_DB = json.load(f)
else:
    DRIVER_DB = {} # if not create one.

def save_driver_db(): # this is a function that creates a new entry into the Driver_DB JSON file, after a session is loaded by a user. 
    with open(DRIVER_DB_FILE, "w") as f:
        json.dump(DRIVER_DB, f)

# --- Static + cached driver list function ---
def get_drivers_for_event(year, gp, session_type): # here is where the actually telemtry app starts 
    """
    Returns drivers from DB if available.
    If missing, fetch once and cache for all session types of the GP/year.
    """
    key = f"{year}::{gp}::{session_type}" # Driver_Db is a dictionary so in order to keep things organised a key, unique identifier  for that specific event/session.
    if key in DRIVER_DB: # since each call is stored in the database, if we make a call that has been made before we simply just have to retrive they key 
        return DRIVER_DB[key]
    # Auto-fetch if not found
    drivers = fetch_and_cache_drivers(year, gp, session_type)
    return drivers

def fetch_and_cache_drivers(year, gp, session_type):
    """Fetch real drivers from FastF1, save to DB."""
    session = fastf1.get_session(year, gp, session_type) # we initialize the seeion by calling faftf1 and loading it 
    session.load()

    try:
        from fastf1.plotting import team_color as get_team_color # in the driver dropdown menu we want each drivers name abriviated and 
        # assosciated with the team colour they drive for.
    except ImportError:
        get_team_color = None

    FALLBACK_TEAM_COLORS = { #  each individual team and their colours 
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

    drivers = [] # creating an empty list of drivers
    for drv in session.drivers:
        drv_data = session.get_driver(drv) # store driver data fetched from FasfF1
        code = drv_data.get("Abbreviation", "").upper() # abbriviate their name and change to upper case for consistency 
        team = drv_data.get("TeamName", "") # teamname
        if get_team_color: # if get team color from above == None
            try:
                color = get_team_color(team) # if get_team_color(team) works, you get the real team color.
            except Exception:
                color = FALLBACK_TEAM_COLORS.get(team, "#999999") # if it does not use the fallback team colours, I see it as a fail safe, since FastF1 is ever changing 
        else:
            color = FALLBACK_TEAM_COLORS.get(team, "#999999") #if all esle fails use a safe fallback gray
        drivers.append((code, team, color)) # lastly each driver in our list has their abribiated name, team and colour.

    for sess_type in ["Q", "R", "FP1", "FP2", "FP3"]: # we iterate through a list of session assigning each a key and attaching them to our previous driver list
        key = f"{year}::{gp}::{sess_type}" # now we know what year, team ,team colour and event that driver partook in.
        DRIVER_DB[key] = drivers

    save_driver_db()
    return drivers

# --- Page settings ---
st.set_page_config(layout="wide", page_title="F1 Telemetry Viewer")
st.title("🏎️ F1 Telemetry Visualizer")

# Select Year
year = st.selectbox("Select Year", list(range(2019, 2025)))

# Get GP list for that year
gp_list = fastf1.get_event_schedule(year)['EventName'].unique().tolist()
gp = st.selectbox("Select Grand Prix", gp_list)

#  dont realy need this: st.write(f"Selected: {year} - {gp}")
session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"])

# Get drivers (instant if cached)
drivers = get_drivers_for_event(year, gp, session_type)


# Default selection
if "driver_selection" not in st.session_state:
    st.session_state.driver_selection = drivers[0][0] if drivers else ""

# --- Colored HTML dropdown for drivers and team colours---

st.subheader("Select a Driver")

# Build the <option> tags for each driver
options_html = "".join(
    [
        f"<option value='{code}' style='color:{color}; font-weight:bold;' "
        f"{'selected' if code == st.session_state.driver_selection else ''}>{code}</option>"
        for code, _, color in drivers
    ]
)

# Wrap options into a <select> dropdown with custom styling
dropdown_html = f"""
<select id="driver_select" style="
    padding:8px; 
    font-size:16px; 
    border-radius:5px; 
    width:120px;
    background-color:#111;  /* dark background */
    color:white;            /* default text color */
">
    {options_html}
</select>

<script>
    // Attach a change listener to the dropdown
    const selectEl = document.getElementById("driver_select");
    selectEl.addEventListener("change", function() {{
        const selected = selectEl.value;  
        // Send the selected driver code back to Streamlit frontend
        window.parent.postMessage({{"type": "driver_selection", "value": selected}}, "*");
    }});
</script>
"""

# Render the custom dropdown in Streamlit
components.html(dropdown_html, height=50)

# --- Load Fastest Lap ---
if st.button("Load Fastest Lap"): # once you click a button to load their fastest lap
    selected_driver = st.session_state.driver_selection
    if not selected_driver or selected_driver == "???": # if you didnt select a driver it prompts a message.
        st.info("Loading real driver list...")
        with st.spinner("Fetching driver data..."): 
            try:
                drivers = fetch_and_cache_drivers(year, gp, session_type)
                st.session_state.driver_selection = drivers[0][0]
                st.rerun()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        try:
            with st.spinner("Fetching data..."):
                progress = st.progress(0) # this is our progress bar 
                session = fastf1.get_session(year, gp, session_type) # get our selected session
                session.load()
                progress.progress(30)

                lap = session.laps.pick_driver(selected_driver).pick_fastest() # load that drivers fastest lap
                progress.progress(60)

                telemetry_driver = lap.get_car_data().add_distance() # telemetry_driver includes Time, Speed, throttle, Brake, Engine Rpm and distance
                progress.progress(80)

                plot_track_map_plotly(year, gp, session_type, selected_driver, highlight_corners=True) # Now we call our plot_track map function
                fig = plot_laptimes(session, selected_driver)
                st.plotly_chart(fig, use_container_width=True)
                plot_speed_plotly(telemetry_driver) # speed  plot
                plot_longitudinal_acceleration_plotly(telemetry_driver) # acceleration plot
                plot_throttle_brake_plotly(telemetry_driver) # Throttle Vs Brake plot 
                plot_gear_plotly(telemetry_driver) # gear Plot
                plot_drs_plotly(telemetry_driver) # Drs plot 

                progress.progress(100)
                progress.empty()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
