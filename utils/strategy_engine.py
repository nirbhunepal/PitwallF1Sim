import fastf1
import numpy as np
import pandas as pd
import random

fastf1.Cache.enable_cache('data')


def load_race_data(year, race_name):
    session = fastf1.get_session(year, race_name, "Race")
    session.load()
    laps = session.laps
    weather = session.weather_data
    return laps, weather


def estimate_base_lap_time(laps):
    clean_laps = laps[laps['PitOutTime'].isna() & laps['PitInTime'].isna()]
    base = clean_laps['LapTime'].dt.total_seconds().median()
    return base


def tyre_degradation(compound):
    values = {
        "SOFT": 0.15,
        "MEDIUM": 0.10,
        "HARD": 0.07
    }
    return values.get(compound, 0.10)


def simulate_stint(base_time, compound, laps_in_stint):
    deg = tyre_degradation(compound)
    times = []
    for lap in range(int(laps_in_stint)):
        lap_time = base_time + (deg * lap)
        times.append(lap_time)
    return np.sum(times)


def simulate_pit_loss():
    return random.uniform(20.0, 25.0)


def add_weather_penalty(base_time, weather):
    avg_temp = weather['TrackTemp'].mean()
    if avg_temp is None or np.isnan(avg_temp):
        return base_time
    if avg_temp > 40:
        return base_time + 0.25
    if avg_temp < 20:
        return base_time + 0.15
    return base_time


def simulate_strategy(base_lap, total_laps, weather, strategy_plan):
    total_time = 0
    for stint in strategy_plan:
        comp = stint["compound"]
        length = stint["laps"]

        adjusted = add_weather_penalty(base_lap, weather)
        stint_time = simulate_stint(adjusted, comp, length)
        total_time += stint_time

        if stint is not strategy_plan[-1]:
            total_time += simulate_pit_loss()

    return total_time


def expected_finish(total_time, field_times):
    filtered = [t for t in field_times if not np.isnan(t)]
    sorted_times = sorted(filtered + [total_time])
    position = sorted_times.index(total_time) + 1
    return position


def pick_best_strategy(year, race_name):
    laps, weather = load_race_data(year, race_name)
    base = estimate_base_lap_time(laps)

    total_laps = int(laps["LapNumber"].max())

    field_drivers = laps["Driver"].unique()
    field_times = []
    for d in field_drivers:
        driver_laps = laps[laps["Driver"] == d]['LapTime'].dt.total_seconds()
        total = driver_laps.sum(skipna=True)
        field_times.append(total)

    strategies = {
        "0-stop": [
            {"compound": "HARD", "laps": total_laps}
        ],
        "1-stop": [
            {"compound": "MEDIUM", "laps": total_laps // 2},
            {"compound": "HARD", "laps": total_laps - total_laps // 2}
        ],
        "2-stop": [
            {"compound": "SOFT", "laps": total_laps // 3},
            {"compound": "MEDIUM", "laps": total_laps // 3},
            {"compound": "HARD", "laps": total_laps - 2 * (total_laps // 3)}
        ]
    }

    results = {}
    for name, plan in strategies.items():
        total_time = simulate_strategy(base, total_laps, weather, plan)
        finish = expected_finish(total_time, field_times)
        results[name] = (total_time, finish)

    best_name = min(results, key=lambda k: results[k][0])

    return {
        "best_strategy": best_name,
        "times": {
            name: results[name][0]
            for name in results
        }
    }

