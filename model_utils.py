import onnxruntime as ort
import numpy as np
from PIL import Image

session = None

def get_session():
    global session
    if session is None:
        session = ort.InferenceSession("plant_disease_model.onnx")
    return session

def preprocess(image: Image.Image):
    image = image.resize((224, 224))
    arr = np.array(image).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406])  # match your training normalization
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    arr = arr.transpose(2, 0, 1)
    return np.expand_dims(arr, 0).astype(np.float32)

def predict(image: Image.Image):
    sess = get_session()
    input_name = sess.get_inputs()[0].name
    return sess.run(None, {input_name: preprocess(image)})[0]