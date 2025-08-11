import fastf1
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def rotate(xy, *, angle):
    """Rotate an (x, y) coordinate array by a given angle in radians."""
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def plot_track_map_plotly(year=2023, event='Silverstone', session_type='Q',
                          driver=None, highlight_corners=True):
    """
    Plot an F1 track map in Plotly and display it in Streamlit.

    Args:
        year (int): The season year.
        event (str): Grand Prix name (e.g. 'Monza').
        session_type (str): 'Q', 'R', 'FP1', etc.
        driver (str): Optional driver code to highlight fastest lap.
        highlight_corners (bool): Show corner numbers on the map.
    """

    # Load session and lap data
    session = fastf1.get_session(year, event, session_type)
    session.load()

    # Pick fastest lap (either from a specific driver or overall)
    if driver:
        lap = session.laps.pick_driver(driver).pick_fastest()
    else:
        lap = session.laps.pick_fastest()

    pos = lap.get_pos_data()
    circuit_info = session.get_circuit_info()

    # Rotate track to match circuit info orientation
    track = pos[['X', 'Y']].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)

    # Start Plotly figure
    fig = go.Figure()

    # Add track line
    fig.add_trace(go.Scatter(
        x=rotated_track[:, 0],
        y=rotated_track[:, 1],
        mode='lines',
        line=dict(color='white', width=3),
        name='Track'
    ))

    # Optionally add corner markers and labels
    if highlight_corners:
        for _, corner in circuit_info.corners.iterrows():
            txt = f"{corner['Number']}{corner['Letter']}"
            # Rotate the actual corner coordinates
            track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)
            fig.add_trace(go.Scatter(
                x=[track_x],
                y=[track_y],
                mode='markers+text',
                marker=dict(color='red', size=8),
                text=[txt],
                textposition="top center",
                name=f"Corner {txt}",
                showlegend=False
            ))

    # Style the layout
    fig.update_layout(
        template="plotly_dark",
        title=f"{session.event['Location']} Track Map",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=700
    )

    # Keep equal aspect ratio for x/y axes
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
