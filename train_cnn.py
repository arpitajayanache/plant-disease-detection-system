# train_cnn.py
import os
import yaml
import shutil
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image_dataset_from_directory

# 1. Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_ROOT = os.path.join(BASE_DIR, 'dataset')
YAML_PATH = os.path.join(DATASET_ROOT, 'data.yaml')
CLASSIFICATION_DIR = os.path.join(DATASET_ROOT, 'classification')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "plantdec_cnn_tensorflow.h5")

# 2. Auto-Reorganize YOLO to Classification Format
def reorganize_data():
    if not os.path.exists(YAML_PATH):
        print(f"Error: {YAML_PATH} not found. Ensure dataset is unzipped correctly.")
        return False
    
    # We always re-run to ensure at least 'train' is organized
    print("Organizing YOLO dataset into classification folders...")
    with open(YAML_PATH, 'r') as f:
        data = yaml.safe_load(f)
        class_names = data['names']

    for split in ['train', 'valid', 'test']:
        img_dir = os.path.join(DATASET_ROOT, split, 'images')
        lbl_dir = os.path.join(DATASET_ROOT, split, 'labels')
        out_dir = os.path.join(CLASSIFICATION_DIR, split)
        
        if not os.path.exists(img_dir) or not os.path.exists(lbl_dir):
            print(f"  Skipping {split} set (images or labels missing)...")
            continue
        
        print(f"  Processing {split} set...")
        for img_name in os.listdir(img_dir):
            if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')): continue
            
            lbl_name = os.path.splitext(img_name)[0] + '.txt'
            lbl_path = os.path.join(lbl_dir, lbl_name)
            
            if os.path.exists(lbl_path):
                with open(lbl_path, 'r') as f:
                    line = f.readline().strip()
                    if not line: continue
                    try:
                        class_id = int(line.split()[0])
                        class_name = class_names[class_id].replace(' ', '_').replace('(', '').replace(')', '')
                        
                        target_dir = os.path.join(out_dir, class_name)
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.copy(os.path.join(img_dir, img_name), os.path.join(target_dir, img_name))
                    except: continue
    return True

if not reorganize_data():
    exit()

# 3. Load Data for Training
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
TRAIN_DIR = os.path.join(CLASSIFICATION_DIR, 'train')
VAL_DIR = os.path.join(CLASSIFICATION_DIR, 'valid')

print("\nLoading datasets...")

# If validation folder doesn't exist, we split the training set
if not os.path.exists(VAL_DIR) or len(os.listdir(VAL_DIR)) == 0:
    print("Validation folder empty. Splitting training data (80/20)...")
    train_ds = image_dataset_from_directory(
        TRAIN_DIR, validation_split=0.2, subset="training", seed=123,
        image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
    )
    val_ds = image_dataset_from_directory(
        TRAIN_DIR, validation_split=0.2, subset="validation", seed=123,
        image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
    )
else:
    train_ds = image_dataset_from_directory(
        TRAIN_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
    )
    val_ds = image_dataset_from_directory(
        VAL_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
    )

class_names = train_ds.class_names
print(f"Detected {len(class_names)} classes.")

# 4. Build Model (MobileNetV2)
print("\nBuilding model...")
base_model = tf.keras.applications.MobileNetV2(input_shape=(224,224,3), include_top=False, weights='imagenet')
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 5. Train
print("\nStarting training (10 epochs)...")
model.fit(train_ds, validation_data=val_ds, epochs=10)

# 6. Save
model.save(MODEL_SAVE_PATH)
print(f"\nSUCCESS! Model saved as {MODEL_SAVE_PATH}")
print("Now run: python app.py")
