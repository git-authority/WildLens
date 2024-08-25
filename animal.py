from flask import Flask, render_template, request, redirect, url_for
from io import BytesIO
from PIL import Image
import pandas as pd
from model import load_species_classifier_model, predict_species_from_array, preprocess_image_from_stream

app = Flask(__name__)

# Load species information from Excel (.xlsx) file
try:
    species_info = pd.read_excel('Animal_Data.xlsx', engine='openpyxl')
    if 'Species' not in species_info.columns:
        raise ValueError("The 'Species' column is missing in the Excel file.")
except FileNotFoundError as e:
    print(f"Error loading Excel file: {e}")
    species_info = pd.DataFrame()  # Create an empty DataFrame as a fallback
except ValueError as ve:
    print(f"ValueError: {ve}")
    species_info = pd.DataFrame()

# Load your pre-trained model
model = load_species_classifier_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                # Read the file into a BytesIO object
                img_bytes = BytesIO(file.read())
                
                # Open the image using PIL
                image = Image.open(img_bytes)
                
                # Reset the BytesIO object for processing
                img_bytes.seek(0)
                
                # Process the image in memory
                img_array = preprocess_image_from_stream(img_bytes)
                
                # Make a prediction
                species = predict_species_from_array(img_array, model)
                print(f"Predicted species: {species}")
                
                # Fetch additional information from the Excel file
                species_data = {}
                if not species_info.empty and 'Species' in species_info.columns:
                    species_data = species_info[species_info['Species'].str.lower() == species.lower()].to_dict('records')
                    species_data = species_data[0] if species_data else {}
                    print(f"Species data found: {species_data}")
                else:
                    print("No species data found or Excel file is empty.")
                
                return render_template('result.html', species=species, species_data=species_data)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return f"An unexpected error occurred: {e}"
    
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    app.run(debug=True)
