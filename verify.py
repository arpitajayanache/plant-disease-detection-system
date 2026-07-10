import torch
import torch.nn as nn
from torchvision import models
import onnxruntime as ort
import numpy as np
import json
from PIL import Image

IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Load labels
with open("label_map.json", "r") as f:
    label_map = json.load(f)
num_classes = len(label_map)
class_names = [label_map[str(i)] for i in range(num_classes)]

# --- Load PyTorch model ---
def build_model(num_classes):
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(in_features, num_classes)
    )
    return model

torch_model = build_model(num_classes)
checkpoint = torch.load("plant_disease_model.pth", map_location="cpu")
torch_model.load_state_dict(checkpoint['model_state_dict'])
torch_model.eval()

# --- Load ONNX model ---
session = ort.InferenceSession("plant_disease_model.onnx")

# --- Test with a real image ---
# Change this path to any real leaf image you have (e.g. in uploads/ folder)
TEST_IMAGE_PATH = "uploads/1778421883.047599_plant1.png"  # <-- UPDATE THIS

img = Image.open(TEST_IMAGE_PATH).convert("RGB")

# Preprocess for PyTorch
from torchvision import transforms
torch_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])
torch_input = torch_transform(img).unsqueeze(0)

# Preprocess for ONNX (manual, matching same steps)
img_resized = img.resize((IMG_SIZE, IMG_SIZE))
arr = np.array(img_resized).astype(np.float32) / 255.0
mean = np.array(IMAGENET_MEAN)
std = np.array(IMAGENET_STD)
arr = (arr - mean) / std
arr = arr.transpose(2, 0, 1)
onnx_input = np.expand_dims(arr, 0).astype(np.float32)

# Run both
with torch.no_grad():
    torch_output = torch_model(torch_input).numpy()[0]

onnx_output = session.run(None, {"input": onnx_input})[0][0]

# Compare
print("PyTorch top class:", class_names[np.argmax(torch_output)])
print("ONNX top class:   ", class_names[np.argmax(onnx_output)])
print("Max difference:", np.abs(torch_output - onnx_output).max())
# Compare confidence scores after softmax
torch_probs = torch.softmax(torch.tensor(torch_output), dim=0).numpy()
onnx_exp = np.exp(onnx_output - np.max(onnx_output))
onnx_probs = onnx_exp / onnx_exp.sum()

print("PyTorch confidence:", torch_probs.max())
print("ONNX confidence:   ", onnx_probs.max())