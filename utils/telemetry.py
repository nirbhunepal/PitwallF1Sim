import fastf1
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from app import get_telemetry

fastf1.Cache.enable_cache('data')

def generate_telemetry_plot(year, race_name, session_type, driver):
    session = fastf1.get_session(year, race_name, session_type)
    session.load()
    weather = session.weather_data

    team_colors = {
        'Red Bull': '#0600ef',
        'Ferrari': '#dc0000',
        'Mercedes': '#00d2be',
        'McLaren': '#ff8700',
        'Aston Martin': '#006f62',
        'Williams': '#00a0de',
        'Alpine': '#0090ff',
        'Kick Sauber': '#52e252',
        'Haas': '#b6babd',
        'RB': '#2b4562'
    }

    driver_info = session.get_driver(driver)
    driver_team = driver_info.get('TeamName', None)
    line_color = team_colors.get(driver_team, 'white')

    laps = session.laps.pick_driver(driver).copy()
    laps = laps[~laps['PitInTime'].notna()]
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    laps = laps[laps['LapTimeSeconds'].notna()]
    median_seconds = laps['LapTimeSeconds'].median()
    laps = laps[laps['LapTimeSeconds'] < median_seconds + 10]

    colors = laps['Compound'].map({'SOFT': 'red', 'MEDIUM': 'yellow', 'HARD': 'white'}).fillna('grey')
    median_seconds = laps['LapTimeSeconds'].median()
    laps['delta'] = abs(laps['LapTimeSeconds'] - median_seconds)
    closest = laps['delta'].idxmin()
    race_pace_lap = laps.loc[closest]
    telemetry = race_pace_lap.get_car_data().add_distance()

    plt.style.use('dark_background')
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))

    ax[0, 0].plot(laps['LapNumber'], laps['LapTimeSeconds'], color=line_color)
    ax[0, 0].set_title('Tire Degradation')
    ax[0, 0].set_ylabel('Lap Time (s)')
    ax[0, 0].set_xlabel('Lap Number')

    weather = weather.dropna(subset=['TrackTemp', 'AirTemp'])
    ax[0, 1].plot(weather['Time'], weather['TrackTemp'], color='orange', label='Track Temp')
    ax[0, 1].plot(weather['Time'], weather['AirTemp'], color='skyblue', label='Air Temp')
    ax[0, 1].set_title('Weather Trend Over Race')
    ax[0, 1].set_xlabel('Time')
    ax[0, 1].set_ylabel('Temperature (°C)')
    ax[0, 1].legend()

    laps_for_scatter = laps.dropna(subset=['LapNumber', 'LapTimeSeconds'])
    ax[1, 0].scatter(
        laps_for_scatter['LapNumber'],
        laps_for_scatter['LapTimeSeconds'],
        c=colors.loc[laps_for_scatter.index],
        edgecolor='black',
        s=30
    )
    ax[1, 0].set_title('Lap Times by Tire Compound')
    ax[1, 0].set_xlabel('Lap Number')
    ax[1, 0].set_ylabel('Lap Time (s)')

    telemetry = telemetry.dropna(subset=['Distance', 'nGear'])
    ax[1, 1].plot(telemetry['Distance'], telemetry['nGear'], color=line_color)
    ax[1, 1].set_title('Gear Selected vs Distance')
    ax[1, 1].set_ylabel('Gear Selected')
    ax[1, 1].set_xlabel('Distance')

    plt.suptitle(f'{driver} – {race_name} {year} Data', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('static/graphs/telemetry.png', dpi=300)
    plt.close()

    return '/static/graphs/telemetry.png'












