import fastf1
import pandas as pd

fastf1.Cache.enable_cache('data')


def load_race_data(year, race_name):
    session = fastf1.get_session(year, race_name, "Race")
    session.load()

    laps = session.laps.copy()
    weather = session.weather_data.copy()

    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    laps = laps[
        (laps["LapTime"].notna()) &
        (laps["PitInTime"].isna()) &
        (laps["LapTimeSeconds"] > 40)
    ]

    degradation = (
        laps.groupby(["Driver", "Stint"])
            .apply(lambda x: (x["LapTimeSeconds"].iloc[-1] - x["LapTimeSeconds"].iloc[0]) /
                             max(len(x) - 1, 1))
            .reset_index(name="DegSlope")
    )

    pit_deltas = []
    for drv in laps["Driver"].unique():
        drv_laps = session.laps.pick_driver(drv)
        pitlaps = drv_laps[drv_laps["PitInTime"].notna()]
        if len(pitlaps) > 0:
            pit_deltas.append({
                "Driver": drv,
                "PitLoss": pitlaps["LapTimeSeconds"].mean()
            })

    pit_deltas = pd.DataFrame(pit_deltas)
    avg_pit_loss = pit_deltas["PitLoss"].mean() if len(pit_deltas) else 22.0

    return {
        "laps": laps,
        "weather": weather,
        "degradation": degradation,
        "avg_pit_loss": avg_pit_loss
    }
