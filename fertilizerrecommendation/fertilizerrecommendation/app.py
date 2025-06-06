from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os
import tempfile
import shutil

app = Flask(__name__)

# Define CSV file path
csv_file = r"C:\Users\Chinn\OneDrive\Desktop\fertilizerrecommendation\fertilizerrecommendation\data\f2.csv"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        soil_type = request.form['soil_type'].strip().lower()
        crop_type = request.form['crop_type'].strip().lower()
        nitrogen = float(request.form['nitrogen'])
        phosphorous = float(request.form['phosphorous'])
        potassium = float(request.form['potassium'])

        # Load or create the CSV file
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
        else:
            df = pd.DataFrame(columns=['Soil_Type', 'Crop_Type', 'Nitrogen', 'Phosphorous', 'Potassium', 'Fertilizer'])

        # Normalize columns
        df['Soil_Type'] = df['Soil_Type'].astype(str).str.strip().str.lower()
        df['Crop_Type'] = df['Crop_Type'].astype(str).str.strip().str.lower()
        df['Nitrogen'] = pd.to_numeric(df['Nitrogen'], errors='coerce')
        df['Phosphorous'] = pd.to_numeric(df['Phosphorous'], errors='coerce')
        df['Potassium'] = pd.to_numeric(df['Potassium'], errors='coerce')

        # Check if input exists
        match = df[
            (df['Soil_Type'] == soil_type) &
            (df['Crop_Type'] == crop_type) &
            (df['Nitrogen'] == nitrogen) &
            (df['Phosphorous'] == phosphorous) &
            (df['Potassium'] == potassium)
        ]

        if not match.empty:
            fertilizer = match.iloc[0]['Fertilizer']
        else:
            fertilizer = "No exact match found. Please consult with an agronomist."

            # Create new row
            new_row = pd.DataFrame([{
                'Soil_Type': soil_type,
                'Crop_Type': crop_type,
                'Nitrogen': nitrogen,
                'Phosphorous': phosphorous,
                'Potassium': potassium,
                'Fertilizer': fertilizer
            }])

            # Append safely using temp file
            df = pd.concat([df, new_row], ignore_index=True)
            with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8') as tmpfile:
                temp_path = tmpfile.name
                df.to_csv(temp_path, index=False)
                tmpfile.flush()

            # Replace original file (only if no error)
            shutil.move(temp_path, csv_file)

        return jsonify({"prediction": fertilizer})

    except PermissionError:
        return jsonify({"error": "Permission denied. Please close the CSV file if it's open and try again."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
