# Depression and Mood Disorder Diagnosis Backend

## Overview
This is a Flask-based backend for an expert system designed to diagnose depression and mood disorders (e.g., possible bipolar disorder, anxiety) in final-year students using the **Certainty Factor (CF)** and **Forward Chaining** methods. The system is based on research from Supiandi et al. (2018) and Khawarizmi et al. (2020), incorporating 20 symptoms and rules for mild depression, moderate depression, severe depression, mood disorders, and anxiety disorders.

The backend provides a REST API that:
- Loads symptoms, certainty factor options, and rules from JSON files.
- Accepts user inputs (symptom certainty levels) via a POST request.
- Returns diagnosis results with confidence percentages.

## Features
- **API Endpoints**: Provides endpoints for fetching symptoms, CF options, and performing diagnoses.
- **JSON Configuration**: Symptoms, rules, and CF options are stored in JSON files for easy updates.
- **Certainty Factor**: Calculates diagnosis confidence using CF formulas from the referenced journals.
- **Forward Chaining**: Infers diagnoses based on user inputs and predefined rules.

## Requirements
- Python 3.8+
- Flask (`pip install flask`)

## Setup Instructions
1. **Clone the Repository** (if applicable) or create the following files in a project directory:
   - `depression_diagnosis.py`: The main Flask application.
   - `symptoms.json`: Contains symptom definitions and expert CF values.
   - `cf_options.json`: Contains certainty factor options for user inputs.
   - `rules.json`: Contains rules for diagnosing conditions.

2. **Install Dependencies**:
   ```bash
   pip install flask
   ```

3. **Prepare JSON Files**:
   - Ensure `symptoms.json`, `cf_options.json`, and `rules.json` are in the same directory as `depression_diagnosis.py`.
   - Example `symptoms.json`:
     ```json
     {
         "D1": {"name": "Kesedihan", "expert_cf": 1.0},
         "D2": {"name": "Pesimis", "expert_cf": 0.2},
         ...
     }
     ```
   - Example `cf_options.json`:
     ```json
     {
         "1": ["Pasti Tidak", -1.0],
         "2": ["Hampir Pasti Tidak", -0.8],
         ...
     }
     ```
   - Example `rules.json`:
     ```json
     {
         "M1": {
             "name": "Depresi Ringan",
             "symptoms": ["D2", "D13"],
             "rule_cf": 1.0
         },
         ...
     }
     ```

4. **Run the Backend**:
   ```bash
   python depression_diagnosis.py
   ```
   - The server will start at `http://localhost:5000` (default).

## API Endpoints
### 1. GET /symptoms
- **Description**: Retrieves the list of symptoms with their names and expert CF values.
- **Response**:
  ```json
  {
      "D1": {"name": "Kesedihan", "expert_cf": 1.0},
      "D2": {"name": "Pesimis", "expert_cf": 0.2},
      ...
  }
  ```
- **Status Codes**:
  - 200: Success
  - 500: Failed to load symptoms file

### 2. GET /cf_options
- **Description**: Retrieves the certainty factor options for user inputs.
- **Response**:
  ```json
  {
      "1": ["Pasti Tidak", -1.0],
      "2": ["Hampir Pasti Tidak", -0.8],
      ...
  }
  ```
- **Status Codes**:
  - 200: Success
  - 500: Failed to load CF options file

### 3. POST /diagnose
- **Description**: Processes user inputs to diagnose depression or mood disorders.
- **Request Body** (JSON):
  ```json
  {
      "D1": 0.2,
      "D2": 0.4,
      "D13": 0.8,
      ...
  }
  ```
  - Keys: Symptom IDs (e.g., "D1", "D2").
  - Values: CF values (must be one of: -1.0, -0.8, -0.6, -0.4, 0.2, 0.4, 0.6, 0.8, 1.0).
- **Response**:
  ```json
  {
      "results": {
          "M1": {"name": "Depresi Ringan", "cf": 40.0},
          "M2": {"name": "Depresi Sedang", "cf": 20.0},
          ...
      },
      "diagnosis": "Depresi Ringan",
      "confidence": 40.0
  }
  ```
- **Status Codes**:
  - 200: Success
  - 400: Invalid input (e.g., invalid symptom ID, invalid CF value)
  - 500: Failed to load configuration files

## Example Usage
Using `curl` to test the `/diagnose` endpoint:
```bash
curl -X POST http://localhost:5000/diagnose -H "Content-Type: application/json" -d '{"D1": 0.2, "D2": 0.4, "D13": 0.8}'
```

Example response:
```json
{
    "results": {
        "M1": {"name": "Depresi Ringan", "cf": 40.0}
    },
    "diagnosis": "Depresi Ringan",
    "confidence": 40.0
}
```

## Project Structure
```
depression-diagnosis-backend/
├── depression_diagnosis.py
├── symptoms.json
├── cf_options.json
├── rules.json
├── README.md
```

## Notes
- **Configuration**: Update JSON files to modify symptoms, CF options, or rules without changing the code.
- **Frontend Integration**: Pair with a frontend (e.g., Laravel, as described in related documentation) to provide a user interface.
- **Security**: In production, use HTTPS and add authentication to secure API endpoints.
- **Error Handling**: The API includes validation for symptom IDs and CF values, returning appropriate error messages.

## References
- Supiandi et al. (2018). *Sistem Pakar Diagnosa Tingkat Depresi Mahasiswa Tingkat Akhir Menggunakan Metode Certainty Factor*.
- Khawarizmi et al. (2020). *Sistem Pakar Diagnosa Gangguan Mood dengan Pendekatan Forward Chaining dan Certainty Factor*.

## License
This project is for educational purposes and based on academic research. No specific license is applied.

For issues or contributions, please contact the project maintainer.