import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image # type: ignore
import numpy as np

def load_species_classifier_model():
    try:
        model = tf.keras.models.load_model('C:/Users/Sreeja Mondal/Desktop/Hackathon.h5')
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def preprocess_image_from_stream(pil_image):
    # Ensure the image is in RGB mode
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Resize and preprocess the image
    img = pil_image.resize((224, 224))  # Adjust size if needed
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize to the range [0, 1] if that was used during training
    return img_array

def predict_species_from_array(model, img_array):
    # Make a prediction using the loaded model
    prediction = model.predict(img_array)
    
    # Assuming the model output is a softmax vector, get the index of the highest probability
    predicted_class_idx = np.argmax(prediction, axis=1)[0]
    
    # Convert the prediction index to a species name
    species = prediction_to_species(predicted_class_idx)
    return species

def prediction_to_species(predicted_class_idx):
    species_mapping = {
        0: "Antelope", 1: "Badger", 2: "Bald_eagle", 3: "Bat", 4: "Bear", 5: "Bee",
        6: "Beetle", 7: "Bighorn_sheep", 8: "Bison", 9: "Black_bear", 10: "Boar",
        11: "Burrowing_owl", 12: "Butterfly", 13: "Canada_goose_bird", 14: "Caribou",
        15: "Cat", 16: "Caterpillar", 17: "Chimpanzee", 18: "Cockroach", 19: "Cougar",
        20: "Cow", 21: "Coyote", 22: "Crab", 23: "Crow", 24: "Deer", 25: "Dog",
        26: "Dolphin", 27: "Donkey", 28: "Dragonfly", 29: "Duck", 30: "Eagle",
        31: "Elephant", 32: "Elk", 33: "Flamingo", 34: "Fly", 35: "Fox", 36: "Goat",
        37: "Golden_eagle", 38: "Goldfish", 39: "Goose", 40: "Gorilla", 41: "Grasshopper",
        42: "Great_horned_owl", 43: "Grizzly_bear", 44: "Hamster", 45: "Hare",
        46: "Hedgehog", 47: "Hippopotamus", 48: "Hornbill", 49: "Horse", 50: "Hummingbird",
        51: "Hyena", 52: "Jellyfish", 53: "Kangaroo", 54: "Koala", 55: "Ladybugs",
        56: "Leopard", 57: "Lion", 58: "Lizard", 59: "Lobster", 60: "Lynx",
        61: "Moose", 62: "Mosquito", 63: "Moth", 64: "Mountain_goat", 65: "Mouse",
        66: "Mule deer", 67: "Octopus", 68: "Okapi", 69: "Orangutan", 70: "Otter",
        71: "Owl", 72: "Ox", 73: "Oyster", 74: "Panda", 75: "Parrot",
        76: "Pelecaniformes", 77: "Penguin", 78: "Pig", 79: "Pigeon", 80: "Pine marten",
        81: "Porcupine", 82: "Possum", 83: "Raccoon", 84: "Rat", 85: "Reindeer",
        86: "rhinoceros", 87: "River Otter", 88: "Sandpiper", 89: "Seahorse", 90: "Seal",
        91: "Shark", 92: "Sheep", 93: "Snake", 94: "Snow Goose", 95: "Sparrow",
        96: "Squid", 97: "Squirrel", 98: "Starfish", 99: "Swan", 100: "Tiger",
        101: "Turkey", 102: "Turtle", 103: "Whale", 104: "White tail deer", 105: "Wolf",
        106: "Wombat", 107: "Woodpecker", 108: "Zebra"
    }

    return species_mapping.get(predicted_class_idx, "Unknown")
