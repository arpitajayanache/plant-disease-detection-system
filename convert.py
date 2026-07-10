import torch
import torch.nn as nn
from torchvision import models
import json

IMG_SIZE = 224
MODEL_PATH = "plant_disease_model.pth"
LABEL_MAP_PATH = "label_map.json"
ONNX_OUTPUT_PATH = "plant_disease_model.onnx"

# Load labels to get num_classes (same as llm_service.py does)
with open(LABEL_MAP_PATH, 'r') as f:
    label_map = json.load(f)
num_classes = len(label_map)

# Rebuild the EXACT same architecture as _build_model() in llm_service.py
def build_model(num_classes):
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(in_features, num_classes)
    )
    return model

model = build_model(num_classes)

# Load checkpoint (it's a dict with 'model_state_dict' key)
checkpoint = torch.load(MODEL_PATH, map_location="cpu")
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Dummy input matching IMG_SIZE
dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

# Export
torch.onnx.export(
    model,
    dummy_input,
    ONNX_OUTPUT_PATH,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=17
)
print(f"✅ Exported to {ONNX_OUTPUT_PATH}")