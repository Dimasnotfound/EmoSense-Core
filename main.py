from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emosense.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Define Diagnosis model
class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_inputs = db.Column(db.String(500), nullable=False)  # Store as JSON string
    results = db.Column(db.String(500), nullable=False)  # Store as JSON string
    diagnosis = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "user_inputs": json.loads(self.user_inputs),
            "results": json.loads(self.results),
            "diagnosis": self.diagnosis,
            "confidence": self.confidence,
        }


# Create the database and tables
with app.app_context():
    db.create_all()


# Load JSON files
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


# Forward chaining logic
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
        if rule_id == "N1":
            continue
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

    THRESHOLD = 30.0
    significant_diagnoses = {k: v for k, v in results.items() if v["cf"] >= THRESHOLD}

    if not significant_diagnoses:
        normal_result = {
            "N1": {
                "name": "Normal",
                "cf": 100.0,
            }
        }
        # Save to database
        diagnosis_entry = Diagnosis(
            user_inputs=json.dumps(user_inputs),
            results=json.dumps(normal_result),
            diagnosis="Normal",
            confidence=100.0,
        )
        db.session.add(diagnosis_entry)
        db.session.commit()

        return jsonify(
            {
                "results": normal_result,
                "diagnosis": "Normal",
                "confidence": 100.0,
                "message": "Tidak ada tanda-tanda depresi atau gangguan suasana hati. Tetap jaga kesehatan mental Anda dan konsultasikan dengan profesional jika merasa perlu.",
            }
        ), 200

    max_cf = -1
    diagnosis = None
    for rule_id, result in significant_diagnoses.items():
        if result["cf"] > max_cf:
            max_cf = result["cf"]
            diagnosis = result["name"]

    # Save to database
    diagnosis_entry = Diagnosis(
        user_inputs=json.dumps(user_inputs),
        results=json.dumps(results),
        diagnosis=diagnosis,
        confidence=max_cf if diagnosis else None,
    )
    db.session.add(diagnosis_entry)
    db.session.commit()

    response = {
        "results": results,
        "diagnosis": diagnosis,
        "confidence": max_cf if diagnosis else None,
        "message": "Hasil ini bukan pengganti diagnosis profesional. Jika Anda merasa perlu, konsultasikan dengan psikolog atau dokter.",
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


@app.route("/diagnoses", methods=["GET"])
def get_diagnoses():
    diagnoses = Diagnosis.query.all()
    return jsonify([diagnosis.to_dict() for diagnosis in diagnoses]), 200


@app.route("/")
def hello_world():
    return "<p>Ini Backend EmoSense!</p>"


if __name__ == "__main__":
    app.run(debug=True)
