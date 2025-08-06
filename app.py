import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fastf1 import get_session
import fastf1

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
        telemetry = lap.get_car_data().add_distance()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name='Speed',
            line=dict(color='#FF4C4C'),
            hovertemplate='Distance: %{x:.0f} m<br>Speed: %{y:.0f} km/h<extra></extra>'
        ))

        fig.update_layout(
            template="plotly_dark",
            title="Speed vs Distance",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
