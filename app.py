from flask import Flask, render_template, request, jsonify
import utils.telemetry as telemetry_module
import joblib
import pandas as pd

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/get_telemetry', methods=['POST'])
def get_telemetry():
    data = request.get_json()
    driver = data['driver']
    year = int(data['year'])
    race = data['race']
    image_path = telemetry_module.generate_telemetry_plot(year, race, "Race", driver)

    return jsonify({"status": "success", "image_path": image_path})

@app.route('/run_strategy', methods=['POST'])
def run_strategy():
    data = request.get_json()
    year = int(data['year'])
    race = data['race']

    from utils.strategy_engine import pick_best_strategy

    try:
        result = pick_best_strategy(year, race)
        return jsonify({
            "status": "success",
            "best_strategy": result["best_strategy"],
            "times": result["times"]

        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)

