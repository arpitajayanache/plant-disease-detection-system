
# ============================================================
# PLANT DISEASE CNN — GOOGLE COLAB TRAINING GUIDE
# PyTorch + TensorFlow | PlantDoc Dataset
# Copy each cell block into a new Colab cell
# ============================================================

# ─────────────────────────────────────────────────────────────
# CELL 1 ── Check GPU & Install Packages
# ─────────────────────────────────────────────────────────────
"""
# 🌿 Plant Disease CNN Training — Google Colab
### Step 1: Enable GPU first → Runtime > Change Runtime Type > GPU
"""

import subprocess
subprocess.run(["nvidia-smi"])  # Confirm GPU is available

# Install / upgrade required packages
# !pip install -q torch torchvision tensorflow opencv-python-headless matplotlib seaborn scikit-learn

import torch
import tensorflow as tf

print("PyTorch version :", torch.__version__)
print("TensorFlow version:", tf.__version__)
print("GPU (PyTorch)    :", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
print("GPU (TensorFlow) :", tf.config.list_physical_devices('GPU'))


# ─────────────────────────────────────────────────────────────
# CELL 2 ── Mount Google Drive & Set Dataset Path
# ─────────────────────────────────────────────────────────────
"""
### Step 2: Mount Drive and locate your dataset
Upload the PlantDoc dataset to your Google Drive before running this cell.
Expected structure:
  MyDrive/PlantDoc/train/ClassName/image.jpg
  MyDrive/PlantDoc/val/ClassName/image.jpg
  MyDrive/PlantDoc/test/ClassName/image.jpg
"""

from google.colab import drive
drive.mount('/content/drive')

import os

DATASET_ROOT = '/content/drive/MyDrive/PlantDoc'   # ← change if needed
TRAIN_DIR    = os.path.join(DATASET_ROOT, 'train')
VAL_DIR      = os.path.join(DATASET_ROOT, 'val')
TEST_DIR     = os.path.join(DATASET_ROOT, 'test')

# Print folder structure
for split in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    classes = os.listdir(split)
    print(f"\n{split}  →  {len(classes)} classes")
    for c in classes[:5]:
        n = len(os.listdir(os.path.join(split, c)))
        print(f"   {c}: {n} images")
    if len(classes) > 5:
        print(f"   ... and {len(classes)-5} more classes")


# ─────────────────────────────────────────────────────────────
# CELL 3 ── Shared Config
# ─────────────────────────────────────────────────────────────
"""
### Step 3: Shared hyper-parameters
"""

IMG_SIZE   = 224          # resize all images to 224×224
BATCH_SIZE = 32
EPOCHS     = 20
LR         = 1e-3

# Discover class names from train folder
CLASS_NAMES = sorted(os.listdir(TRAIN_DIR))
NUM_CLASSES = len(CLASS_NAMES)
print(f"Total classes: {NUM_CLASSES}")
print(CLASS_NAMES)


# ─────────────────────────────────────────────────────────────
# CELL 4 ── PyTorch: DataLoaders
# ─────────────────────────────────────────────────────────────
"""
### Step 4 (PyTorch): Data preparation with torchvision
"""

import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ImageNet-style mean/std normalisation
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])

train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transforms)
val_dataset   = datasets.ImageFolder(VAL_DIR,   transform=val_transforms)
test_dataset  = datasets.ImageFolder(TEST_DIR,  transform=val_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,  num_workers=2, pin_memory=True)
val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)

print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_dataset)}")


# ─────────────────────────────────────────────────────────────
# CELL 5 ── PyTorch: CNN Model
# ─────────────────────────────────────────────────────────────
"""
### Step 5 (PyTorch): Define CNN architecture
"""

import torch.nn as nn
import torch.nn.functional as F

class PlantCNN(nn.Module):
    def __init__(self, num_classes):
        super(PlantCNN, self).__init__()

        # Block 1
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2))   # 112×112

        # Block 2
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2))   # 56×56

        # Block 3
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2))  # 28×28

        # Block 4
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(), nn.MaxPool2d(2))  # 14×14

        # Classifier
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),          # 1×1
            nn.Flatten(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        return self.classifier(x)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
pt_model = PlantCNN(NUM_CLASSES).to(DEVICE)
print(pt_model)

# Quick sanity check
dummy = torch.randn(2, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
print("Output shape:", pt_model(dummy).shape)  # should be [2, NUM_CLASSES]


# ─────────────────────────────────────────────────────────────
# CELL 6 ── PyTorch: Training Loop
# ─────────────────────────────────────────────────────────────
"""
### Step 6 (PyTorch): Train the model
"""

import copy
import time
import matplotlib.pyplot as plt

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(pt_model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# ── History trackers ──────────────────────────────────────────
pt_history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
best_val_acc = 0.0
best_weights = copy.deepcopy(pt_model.state_dict())

for epoch in range(1, EPOCHS + 1):
    t0 = time.time()

    # ── Training phase ────────────────────────────────────────
    pt_model.train()
    running_loss = running_correct = 0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = pt_model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss    += loss.item() * imgs.size(0)
        running_correct += (outputs.argmax(1) == labels).sum().item()

    train_loss = running_loss / len(train_dataset)
    train_acc  = running_correct / len(train_dataset)

    # ── Validation phase ──────────────────────────────────────
    pt_model.eval()
    val_loss = val_correct = 0

    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = pt_model(imgs)
            val_loss    += criterion(outputs, labels).item() * imgs.size(0)
            val_correct += (outputs.argmax(1) == labels).sum().item()

    val_loss /= len(val_dataset)
    val_acc   = val_correct / len(val_dataset)

    scheduler.step()

    pt_history['train_loss'].append(train_loss)
    pt_history['val_loss'].append(val_loss)
    pt_history['train_acc'].append(train_acc)
    pt_history['val_acc'].append(val_acc)

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        best_weights = copy.deepcopy(pt_model.state_dict())

    elapsed = time.time() - t0
    print(f"Epoch [{epoch:02d}/{EPOCHS}] | "
          f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
          f"Time: {elapsed:.1f}s")

# Load best weights
pt_model.load_state_dict(best_weights)
print(f"\nBest Val Accuracy: {best_val_acc:.4f}")

# ── Plot results ──────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(pt_history['train_loss'], label='Train Loss')
axes[0].plot(pt_history['val_loss'],   label='Val Loss')
axes[0].set_title('PyTorch — Loss'); axes[0].legend(); axes[0].set_xlabel('Epoch')

axes[1].plot(pt_history['train_acc'], label='Train Acc')
axes[1].plot(pt_history['val_acc'],   label='Val Acc')
axes[1].set_title('PyTorch — Accuracy'); axes[1].legend(); axes[1].set_xlabel('Epoch')

plt.tight_layout(); plt.savefig('pytorch_training_curves.png', dpi=120); plt.show()


# ─────────────────────────────────────────────────────────────
# CELL 7 ── PyTorch: Evaluation & Single-Image Prediction
# ─────────────────────────────────────────────────────────────
"""
### Step 7 (PyTorch): Evaluate on test set & predict a single image
"""

from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import numpy as np

pt_model.eval()
all_preds, all_labels = [], []

with torch.no_grad():
    for imgs, labels in test_loader:
        imgs = imgs.to(DEVICE)
        preds = pt_model(imgs).argmax(1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.numpy())

print("\n── Classification Report ─────────────────────────────────")
print(classification_report(all_labels, all_preds, target_names=CLASS_NAMES))

# Confusion matrix (top 10 classes for readability)
cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(14, 12))
sns.heatmap(cm, xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
            fmt='d', cmap='Blues', annot=(NUM_CLASSES <= 15))
plt.title('PyTorch — Confusion Matrix')
plt.tight_layout(); plt.savefig('pytorch_confusion_matrix.png', dpi=120); plt.show()

# ── Predict a single image ────────────────────────────────────
from PIL import Image

def pt_predict(image_path):
    img = Image.open(image_path).convert('RGB')
    tensor = val_transforms(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        output  = pt_model(tensor)
        probs   = torch.softmax(output, dim=1)
        conf, pred = probs.max(1)
    return CLASS_NAMES[pred.item()], conf.item()

# Example: replace with any test image path
sample_path = os.path.join(TEST_DIR, CLASS_NAMES[0],
                           os.listdir(os.path.join(TEST_DIR, CLASS_NAMES[0]))[0])
disease, confidence = pt_predict(sample_path)
print(f"\nPredicted Disease : {disease}")
print(f"Confidence        : {confidence*100:.2f}%")


# ─────────────────────────────────────────────────────────────
# CELL 8 ── PyTorch: Save Model
# ─────────────────────────────────────────────────────────────
"""
### Step 8 (PyTorch): Save the trained model
"""

SAVE_DIR = '/content/drive/MyDrive/PlantDoc_Models'
os.makedirs(SAVE_DIR, exist_ok=True)

# Save state dict (recommended)
torch.save(pt_model.state_dict(),
           os.path.join(SAVE_DIR, 'plantdoc_cnn_pytorch.pth'))

# Save full model (optional)
torch.save(pt_model,
           os.path.join(SAVE_DIR, 'plantdoc_cnn_pytorch_full.pth'))

print("PyTorch model saved ✓")


# ═════════════════════════════════════════════════════════════
# ── TensorFlow / Keras Section ────────────────────────────────
# ═════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# CELL 9 ── TensorFlow: DataLoaders
# ─────────────────────────────────────────────────────────────
"""
### Step 9 (TensorFlow): Data preparation
"""

import tensorflow as tf
from tensorflow.keras.utils import image_dataset_from_directory

AUTOTUNE = tf.data.AUTOTUNE

# Load datasets
tf_train = image_dataset_from_directory(
    TRAIN_DIR, image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE, shuffle=True, seed=42, label_mode='int')

tf_val = image_dataset_from_directory(
    VAL_DIR, image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE, shuffle=False, label_mode='int')

tf_test = image_dataset_from_directory(
    TEST_DIR, image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE, shuffle=False, label_mode='int')

TF_CLASS_NAMES = tf_train.class_names
print("TF Classes:", TF_CLASS_NAMES)

# ── Augmentation & Normalisation pipeline ─────────────────────
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.15),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomBrightness(0.2),
])

def preprocess(images, labels):
    images = tf.cast(images, tf.float32) / 255.0   # scale to [0,1]
    return images, labels

def augment(images, labels):
    images = data_augmentation(images, training=True)
    return images, labels

tf_train = (tf_train
            .map(augment,    num_parallel_calls=AUTOTUNE)
            .map(preprocess, num_parallel_calls=AUTOTUNE)
            .prefetch(AUTOTUNE))

tf_val   = tf_val.map(preprocess, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
tf_test  = tf_test.map(preprocess, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)

print("TF datasets ready ✓")


# ─────────────────────────────────────────────────────────────
# CELL 10 ── TensorFlow: CNN Model
# ─────────────────────────────────────────────────────────────
"""
### Step 10 (TensorFlow): Build CNN with Keras Sequential API
"""

from tensorflow.keras import layers, models

def build_tf_cnn(num_classes, img_size=224):
    model = models.Sequential([
        # ── Input ─────────────────────────────────────────────
        layers.Input(shape=(img_size, img_size, 3)),

        # ── Block 1 ───────────────────────────────────────────
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),                                 # 112×112

        # ── Block 2 ───────────────────────────────────────────
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),                                 # 56×56

        # ── Block 3 ───────────────────────────────────────────
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),                                 # 28×28

        # ── Block 4 ───────────────────────────────────────────
        layers.Conv2D(256, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),                                 # 14×14

        # ── Classifier ────────────────────────────────────────
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax'),
    ], name='PlantDiseaseCNN')
    return model

tf_model = build_tf_cnn(NUM_CLASSES)
tf_model.summary()


# ─────────────────────────────────────────────────────────────
# CELL 11 ── TensorFlow: Compile & Train
# ─────────────────────────────────────────────────────────────
"""
### Step 11 (TensorFlow): Compile and train
"""

import os

tf_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LR),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=5, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1),
    tf.keras.callbacks.ModelCheckpoint(
        filepath=os.path.join(SAVE_DIR, 'best_tf_model.keras'),
        monitor='val_accuracy', save_best_only=True, verbose=1),
]

tf_history = tf_model.fit(
    tf_train,
    epochs=EPOCHS,
    validation_data=tf_val,
    callbacks=callbacks,
)

# ── Plot results ──────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(tf_history.history['loss'],     label='Train Loss')
axes[0].plot(tf_history.history['val_loss'], label='Val Loss')
axes[0].set_title('TensorFlow — Loss'); axes[0].legend(); axes[0].set_xlabel('Epoch')

axes[1].plot(tf_history.history['accuracy'],     label='Train Acc')
axes[1].plot(tf_history.history['val_accuracy'], label='Val Acc')
axes[1].set_title('TensorFlow — Accuracy'); axes[1].legend(); axes[1].set_xlabel('Epoch')

plt.tight_layout(); plt.savefig('tf_training_curves.png', dpi=120); plt.show()


# ─────────────────────────────────────────────────────────────
# CELL 12 ── TensorFlow: Evaluation & Single-Image Prediction
# ─────────────────────────────────────────────────────────────
"""
### Step 12 (TensorFlow): Evaluate on test set & predict one image
"""

test_loss, test_acc = tf_model.evaluate(tf_test)
print(f"\nTest Loss    : {test_loss:.4f}")
print(f"Test Accuracy: {test_acc*100:.2f}%")

# ── Predict a single image ────────────────────────────────────
import numpy as np
from PIL import Image as PILImage

def tf_predict(image_path):
    img    = PILImage.open(image_path).convert('RGB').resize((IMG_SIZE, IMG_SIZE))
    arr    = np.array(img, dtype=np.float32) / 255.0
    tensor = np.expand_dims(arr, axis=0)                       # [1, H, W, 3]
    probs  = tf_model.predict(tensor, verbose=0)[0]
    idx    = np.argmax(probs)
    return TF_CLASS_NAMES[idx], float(probs[idx])

disease_tf, conf_tf = tf_predict(sample_path)
print(f"\n[TF] Predicted Disease : {disease_tf}")
print(f"[TF] Confidence        : {conf_tf*100:.2f}%")


# ─────────────────────────────────────────────────────────────
# CELL 13 ── TensorFlow: Save Model
# ─────────────────────────────────────────────────────────────
"""
### Step 13 (TensorFlow): Save models in multiple formats
"""

# Native Keras format (recommended)
tf_model.save(os.path.join(SAVE_DIR, 'plantdoc_cnn_tensorflow.keras'))

# Legacy HDF5 format (for older Keras)
tf_model.save(os.path.join(SAVE_DIR, 'plantdoc_cnn_tensorflow.h5'))

# TensorFlow SavedModel format (for TFLite / TFServing)
tf_model.export(os.path.join(SAVE_DIR, 'plantdoc_savedmodel'))

print("TensorFlow models saved ✓")


# ─────────────────────────────────────────────────────────────
# CELL 14 ── Integration Guide (Flask + React + Gemini LLM)
# ─────────────────────────────────────────────────────────────
"""
### Step 14: System Integration Notes
─────────────────────────────────────
A) Flask Backend (app.py)
─────────────────────────────────────
Load the saved model once at startup, expose a /predict endpoint.

Sample snippet (PyTorch):

    from flask import Flask, request, jsonify
    from PIL import Image
    import torch, io

    app   = Flask(__name__)
    model = PlantCNN(NUM_CLASSES)
    model.load_state_dict(torch.load('plantdoc_cnn_pytorch.pth', map_location='cpu'))
    model.eval()

    @app.route('/predict', methods=['POST'])
    def predict():
        file  = request.files['image']
        img   = Image.open(io.BytesIO(file.read())).convert('RGB')
        tensor = val_transforms(img).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), 1)
        conf, idx = probs.max(1)
        return jsonify({'disease': CLASS_NAMES[idx], 'confidence': conf.item()})

─────────────────────────────────────
B) React Frontend
─────────────────────────────────────
Upload image via <input type="file"> → POST FormData to /predict → display result.

    const handleUpload = async (file) => {
      const form = new FormData();
      form.append('image', file);
      const res  = await fetch('http://localhost:5000/predict', { method:'POST', body: form });
      const data = await res.json();
      setDisease(data.disease);
      setConfidence(data.confidence);
    };

─────────────────────────────────────
C) Gemini LLM Cure Module
─────────────────────────────────────
Map predicted disease → prompt → Gemini API → display cure steps.

    import google.generativeai as genai

    genai.configure(api_key='YOUR_GEMINI_API_KEY')
    model_llm = genai.GenerativeModel('gemini-pro')

    def get_cure(disease_name, language='English'):
        prompt = (
            f"The plant has been diagnosed with: {disease_name}.\\n"
            f"Please provide:\\n"
            f"1. A short description of the disease.\\n"
            f"2. Immediate treatment steps (use simple language).\\n"
            f"3. Preventive measures for the future.\\n"
            f"Answer in {language}."
        )
        response = model_llm.generate_content(prompt)
        return response.text

    # Usage
    cure_text = get_cure("Tomato Early Blight", language="Hindi")
    print(cure_text)

─────────────────────────────────────
D) Multilingual Voice Output (Python)
─────────────────────────────────────
    from gtts import gTTS
    import os

    def speak_cure(text, lang_code='hi'):    # 'hi'=Hindi, 'en'=English, 'mr'=Marathi
        tts = gTTS(text=text, lang=lang_code)
        tts.save('cure.mp3')
        os.system('mpg321 cure.mp3')         # or use playsound on Windows

─────────────────────────────────────
Full Pipeline Summary:
  Image Upload → Flask /predict → CNN Model → disease_name
      ↓
  disease_name + language → Gemini LLM → cure_text
      ↓
  cure_text → gTTS → voice output + displayed on React UI
─────────────────────────────────────
"""

print("Integration guide printed. Refer to the comments above.")
