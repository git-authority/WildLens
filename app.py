from flask import Flask, render_template, request, send_from_directory
from keras.models import load_model
import cv2
import numpy as np
import os

app = Flask(__name__)

# Load the model 
model = load_model('species_classifier_final (1).h5')
print("+"*50, "H5 Model is loaded")

# Define the labels
labels = ['antelope', 'badger', 'bald_eagle', 'bat', 'bear', 'bee', 'beetle', 'bighorn_sheep', 'bison', 'black_bear', 'boar', 'burrowing_owl', 'butterfly', 'canada_goose_bird', 'caribou', 'cat', 'caterpillar', 'chimpanzee', 'cockroach', 'cougar', 'cow', 'coyote', 'crab', 'crow', 'deer', 'dog', 'dolphin', 'donkey', 'dragonfly', 'duck', 'eagle', 'elephant', 'elk', 'flamingo', 'fly', 'fox', 'goat', 'golden_eagle', 'goldfish', 'goose', 'gorilla', 'grasshopper', 'great_horned_owl', 'grizzly_bear', 'hamster', 'hare', 'hedgehog', 'hippopotamus', 'hornbill', 'horse', 'hummingbird', 'hyena', 'jellyfish', 'kangaroo', 'koala', 'ladybugs', 'leopard', 'lion', 'lizard', 'lobster', 'lynx', 'moose', 'mosquito', 'moth', 'mountain_goat', 'mouse', 'mule_deer', 'octopus', 'okapi', 'orangutan', 'otter', 'owl', 'ox', 'oyster', 'panda', 'parrot', 'pelecaniformes', 'penguin', 'pig', 'pigeon', 'pine_marten', 'porcupine', 'possum', 'raccoon', 'rat', 'reindeer', 'rhinoceros', 'river_otter', 'sandpiper', 'seahorse', 'seal', 'shark', 'sheep', 'snake', 'snow_goose', 'sparrow', 'squid', 'squirrel', 'starfish', 'swan', 'tiger', 'turkey', 'turtle', 'whale', 'white_tail_deer', 'wolf', 'wombat', 'woodpecker', 'zebra']

# Set up static folder for uploaded files
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def video_to_frames(video_path, frame_size=(224, 224)):
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
    return render_template("index.html", data="hey")

@app.route("/prediction", methods=["POST"])
def prediction():
    # Check if an image was uploaded
    if 'img' in request.files and request.files['img'].filename != '':
        img = request.files['img']
        img_filename = os.path.join(app.config['UPLOAD_FOLDER'], "uploaded_image.jpg")
        img.save(img_filename)
        
        # Load and preprocess image
        image = cv2.imread(img_filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))
        image = np.reshape(image, (1, 224, 224, 3))
        image = image.astype(np.float32) / 255.0
        
        # Predict on the image
        pred = model.predict(image)
        pred_index = np.argmax(pred, axis=1)[0]
        pred_label = labels[pred_index]
        
        return render_template("prediction.html", data=pred_label, img_filename=img_filename, video_filename=None)
    
    # Check if a video was uploaded
    elif 'video' in request.files and request.files['video'].filename != '':
        video = request.files['video']
        video_filename = os.path.join(app.config['UPLOAD_FOLDER'], "uploaded_video.mp4")
        video.save(video_filename)
        
        # Verify if the video file was saved successfully
        if not os.path.exists(video_filename):
            return "Video could not be saved. Please try again."
        
        # Check the file size to ensure it is not empty
        file_size = os.path.getsize(video_filename)
        print(f"Saved video file size: {file_size} bytes")
        if file_size == 0:
            return "Saved video file is empty. Please try again."

        # Attempt to extract frames from the video
        frames = video_to_frames(video_filename)
        if frames.size == 0:
            return "Failed to extract frames from video. Please try again."
        
        # Normalize frames
        frames = frames.astype(np.float32) / 255.0
        
        # Predict on each frame and average the predictions
        preds = model.predict(frames)
        pred = np.mean(preds, axis=0)
    
        pred_index = np.argmax(pred)
        pred_label = labels[pred_index]
    
        return render_template("prediction.html", data=pred_label, img_filename=None, video_filename=video_filename)
    
    return "No file uploaded. Please upload an image or a video."

if __name__ == "__main__":
    app.run(debug=True)