from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)


def load_json_file(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


symptoms = load_json_file("symptoms.json") or {}
cf_options = load_json_file("cf_options.json") or {}
rules = load_json_file("rules.json") or {}


def calculate_single_cf(expert_cf, user_cf):
    return expert_cf * user_cf


def combine_cf(cf1, cf2):
    return cf1 + cf2 * (1 - cf1)


def calculate_rule_cf(symptom_cfs, rule):
    if not symptom_cfs:
        return 0.0
    min_cf = min(symptom_cfs)
    return min_cf * rule["rule_cf"]


def forward_chaining(user_inputs):
    results = {}
    for rule_id, rule in rules.items():
        symptom_cfs = []
        for symptom_id in rule["symptoms"]:
            if symptom_id in user_inputs:
                cf = calculate_single_cf(
                    symptoms[symptom_id]["expert_cf"], user_inputs[symptom_id]
                )
                symptom_cfs.append(cf)
        if symptom_cfs:
            rule_cf = calculate_rule_cf(symptom_cfs, rule)
            results[rule_id] = {
                "name": rule["name"],
                "cf": rule_cf * 100,
            }
    return results


@app.route("/diagnose", methods=["POST"])
def diagnose():
    if not symptoms or not rules:
        return jsonify({"error": "Failed to load configuration files"}), 500

    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input, JSON object expected"}), 400

    user_inputs = {}
    valid_cf_values = [cf[1] for cf in cf_options.values()]
    for symptom_id, cf_value in data.items():
        if symptom_id not in symptoms:
            return jsonify({"error": f"Invalid symptom ID: {symptom_id}"}), 400
        try:
            cf_value = float(cf_value)
            if cf_value not in valid_cf_values:
                return jsonify(
                    {
                        "error": f"Invalid CF value for {symptom_id}: {cf_value}. Must be one of {valid_cf_values}"
                    }
                ), 400
            user_inputs[symptom_id] = cf_value
        except (ValueError, TypeError):
            return jsonify(
                {"error": f"CF value for {symptom_id} must be a number"}
            ), 400

    if not user_inputs:
        return jsonify({"error": "No valid symptom inputs provided"}), 400

    results = forward_chaining(user_inputs)

    if not results:
        return jsonify(
            {
                "results": [],
                "diagnosis": "Tidak ada diagnosis yang dapat ditentukan berdasarkan input Anda.",
            }
        ), 200

    max_cf = -1
    diagnosis = None
    for rule_id, result in results.items():
        if result["cf"] > max_cf:
            max_cf = result["cf"]
            diagnosis = result["name"]

    response = {
        "results": results,
        "diagnosis": diagnosis,
        "confidence": max_cf if diagnosis else None,
    }
    return jsonify(response), 200


@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    if not symptoms:
        return jsonify({"error": "Failed to load symptoms file"}), 500
    return jsonify(symptoms), 200


@app.route("/cf_options", methods=["GET"])
def get_cf_options():
    if not cf_options:
        return jsonify({"error": "Failed to load CF options file"}), 500
    return jsonify(cf_options), 200


@app.route("/")
def hello_world():
    return "<p>Ini Backend Emo-Sense!</p>"


if __name__ == "__main__":
    app.run(debug=True)
