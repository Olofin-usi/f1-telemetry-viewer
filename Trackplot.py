import fastf1 
from fastf1 import plotting
import numpy as np
from matplotlib import pyplot as plt

plotting.setup_mpl()
plt.style.use('dark_background')  # 👈 dark theme for consistency

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def plot_track_map(ax=None, session=None, year=2023, event='Silverstone', session_type='Q',
                   driver=None, highlight_corners=True, title=None,
                   color='white'):

    if session is None:
        session = fastf1.get_session(year, event, session_type)
        session.load()

    if driver is not None:
        lap = session.laps.pick_drivers(driver).pick_fastest()
    else:
        lap = session.laps.pick_fastest()

    pos = lap.get_pos_data()
    circuit_info = session.get_circuit_info()

    track = pos[['X', 'Y']].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)
    
    # After rotated_track is computed
    x_vals = rotated_track[:, 0]
    y_vals = rotated_track[:, 1]
    
    # Set zoomed-in view with padding
    padding = 100  # adjust as needed
    ax.set_xlim(x_vals.min() - padding, x_vals.max() + padding)
    ax.set_ylim(y_vals.min() - padding, y_vals.max() + padding)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))

    ax.plot(rotated_track[:, 0], rotated_track[:, 1], color=color, linewidth=3, zorder=1)

    if highlight_corners:
        offset_vector = [700, 0]
        for _, corner in circuit_info.corners.iterrows():
            txt = f"{corner['Number']}{corner['Letter']}"
            offset_angle = corner['Angle'] / 180 * np.pi
            offset_x, offset_y = rotate(offset_vector, angle=offset_angle)
            text_x = corner['X'] + offset_x
            text_y = corner['Y'] + offset_y
            text_x, text_y = rotate([text_x, text_y], angle=track_angle)
            track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

            ax.scatter(text_x, text_y, color='gray', s=60, zorder=2)
            ax.plot([track_x, text_x], [track_y, text_y], color='gray', linestyle='--', linewidth=1, zorder=1)
            ax.text(text_x, text_y, txt,
                    va='center_baseline', ha='center', size=8, color='white', fontweight='bold', zorder=3)

    # Remove all borders and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.axis('equal')
    ax.set_facecolor('#111111')  # nice dark background

    if title:
        ax.set_title(title, fontsize=12, color='white', pad=10)
    else:
        ax.set_title(session.event['Location'], fontsize=12, color='white', pad=10)
            
