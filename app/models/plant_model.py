import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os
import json

class PlantDiseaseModel:
    def __init__(self, model_path="plant_disease_model.pth", label_map_path="label_map.json"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load Labels
        with open(label_map_path, 'r') as f:
            self.label_map = json.load(f)
        self.class_names = [self.label_map[str(i)] for i in range(len(self.label_map))]
        self.num_classes = len(self.class_names)
        
        # Build & Load Model
        self.model = self._build_model()
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def _build_model(self):
        model = models.resnet50(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, self.num_classes)
        )
        return model

    def predict_disease(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            
            # Get Top 3
            top_probs, top_idxs = torch.topk(probs, 3)
            
            predictions = []
            for i in range(3):
                predictions.append({
                    "class": self.class_names[top_idxs[i].item()],
                    "confidence": float(top_probs[i].item())
                })
                
        return predictions[0]["class"], predictions[0]["confidence"], predictions

# Global instance
plant_model = PlantDiseaseModel()
