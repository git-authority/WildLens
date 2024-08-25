from flask import Flask, render_template, request, redirect, url_for
from io import BytesIO
from PIL import Image
import pandas as pd
from model import load_species_classifier_model, predict_species_from_array, preprocess_image_from_stream
import base64

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load species information from Excel (.xlsx) file
try:
    species_info = pd.read_excel('Animal_Data.xlsx', engine='openpyxl')
    if 'Species' not in species_info.columns:
        raise ValueError("The 'Species' column is missing in the Excel file.")
except FileNotFoundError as e:
    print(f"Error loading Excel file: {e}")
    species_info = pd.DataFrame()  
except ValueError as ve:
    print(f"ValueError: {ve}")
    species_info = pd.DataFrame()

model = load_species_classifier_model()

# Converting video to frames (optional functionality)

def video_to_frames(video_path, output_folder='frames', frame_size=(224, 224)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0

    while True:
        success, frame = video.read()
        if not success:
            break
        
        frame_count += 1
        frame = cv2.resize(frame, frame_size)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
    
    video.release()

    print(f"Total frames extracted: {frame_count}")
    return np.array(frames)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            print("No file part in request.")
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            print("Empty filename.")
            return redirect(url_for('index'))
        
        if file and allowed_file(file.filename):
            try:
                img_stream = BytesIO(file.read())
                image = Image.open(img_stream)

                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                processed_image = preprocess_image_from_stream(image)
                species = predict_species_from_array(model, processed_image)
                
                print(f"Prediction made: {species}")
                
                # Convert image to base64 string
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # Retrieve species information from the Excel file
                species_data = {}
                if not species_info.empty and 'Species' in species_info.columns:
                    # Ensure species column and predicted species are both lowercase and stripped of spaces
                    species_info['Species'] = species_info['Species'].str.strip().str.lower()
                    species = species.strip().lower()
                    
                    species_data = species_info[species_info['Species'] == species].to_dict('records')
                    
                    if species_data:
                        species_data = species_data[0]
                        print(f"Species data found: {species_data}")
                    else:
                        print(f"No matching species data found for: {species}")
                        species_data = {}
                else:
                    print("No species data found or Excel file is empty.")
                
                return render_template('result.html', img_str=img_str, species=species, species_data=species_data)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return (f"An unexpected error occurred: {e}")
    
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)



