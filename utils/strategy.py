from utils.strategy_features import load_race_data

def simulate_strategy(year, race_name):
    data = load_race_data(year, race_name)

    laps = data["laps"]
    degradation = data["degradation"]
    pit_loss = data["avg_pit_loss"]

    total_laps = laps["LapNumber"].max()

    avg_lap = laps["LapTimeSeconds"].mean()

    one_stop_time = total_laps * avg_lap + pit_loss
    two_stop_time = total_laps * avg_lap + 2 * pit_loss
    three_stop_time = total_laps * avg_lap + 3 * pit_loss

    strategies = {
        "1-stop": one_stop_time,
        "2-stop": two_stop_time,
        "3-stop": three_stop_time
    }

    best_strategy = min(strategies, key=strategies.get)
    best_time = strategies[best_strategy]
    predicted_finish = 3

    return {
        "best_strategy": best_strategy,
        "estimated_race_time": best_time,
        "expected_finish": predicted_finish
    }
