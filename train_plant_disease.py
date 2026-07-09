"""
==============================================================
 Krishi AI — Plant Disease Detection (PyTorch + ResNet50)
 Dataset: PlantDoc kaggle.zip (local — train/ and test/ splits)
==============================================================
Run:
    python train_plant_disease.py          # full training
    python train_plant_disease.py leaf.jpg # inference on image
==============================================================
"""

import os, sys, json, time, zipfile, csv
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from torch.optim.lr_scheduler import ReduceLROnPlateau

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score
)

# ──────────────────────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────────────────────
ZIP_PATH    = Path(os.environ["USERPROFILE"]) / "Downloads" / "PlantDoc kaggle.zip"
DATASET_DIR = Path("plant_disease_dataset")
OUTPUT_DIR  = Path("plant_disease_outputs")

MODEL_PATH       = OUTPUT_DIR / "plant_disease_model.pth"
ONNX_PATH        = OUTPUT_DIR / "plant_disease_model.onnx"
LABEL_MAP_PATH   = OUTPUT_DIR / "label_map.json"
CLASS_NAMES_PATH = OUTPUT_DIR / "class_names.json"
REPORT_CSV_PATH  = OUTPUT_DIR / "classification_report.csv"

BATCH_SIZE          = 32
EPOCHS              = 30
LR                  = 1e-4
WEIGHT_DECAY        = 1e-5
EARLY_STOP_PATIENCE = 5
LR_PATIENCE         = 3
LR_FACTOR           = 0.5
DROPOUT             = 0.5
IMG_SIZE            = 224
VAL_SPLIT           = 0.15   # 15% of train -> validation

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n[INFO] Device: {DEVICE}")
if DEVICE.type == "cuda":
    print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────
#  STEP 1 — EXTRACT DATASET FROM LOCAL ZIP
# ──────────────────────────────────────────────────────────────
def extract_dataset():
    train_dir = DATASET_DIR / "train"
    test_dir  = DATASET_DIR / "test"

    if train_dir.exists() and any(train_dir.iterdir()):
        print(f"[INFO] Dataset already extracted at {DATASET_DIR} — skipping.")
        return train_dir, test_dir

    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"Dataset zip not found at:\n  {ZIP_PATH}\n"
            "Please place 'PlantDoc kaggle.zip' in your Downloads folder."
        )

    print(f"[INFO] Extracting dataset from {ZIP_PATH} ...")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        members = zf.namelist()
        total   = len(members)
        for i, member in enumerate(members, 1):
            zf.extract(member, DATASET_DIR)
            if i % 500 == 0 or i == total:
                print(f"  Extracted {i}/{total} files ...", end="\r")
    print(f"\n[INFO] Extraction complete -> {DATASET_DIR}")
    return train_dir, test_dir


# ──────────────────────────────────────────────────────────────
#  STEP 2 — TRANSFORMS
# ──────────────────────────────────────────────────────────────
def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(30),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    return train_tf, val_tf


# ──────────────────────────────────────────────────────────────
#  STEP 3 — DATA LOADERS
# ──────────────────────────────────────────────────────────────
def build_loaders(train_dir, test_dir, train_tf, val_tf):
    # Full train dataset (with train transforms temporarily)
    full_train = datasets.ImageFolder(str(train_dir), transform=train_tf)
    class_names = full_train.classes
    num_classes = len(class_names)

    # Split train -> train + val (85% / 15%)
    n_val   = int(VAL_SPLIT * len(full_train))
    n_train = len(full_train) - n_val
    train_subset, val_subset = random_split(
        full_train, [n_train, n_val],
        generator=torch.Generator().manual_seed(42)
    )

    # Apply val transforms to validation subset via a wrapper
    class TransformSubset(torch.utils.data.Dataset):
        def __init__(self, subset, transform):
            self.subset    = subset
            self.transform = transform
        def __len__(self):
            return len(self.subset)
        def __getitem__(self, idx):
            img, label = self.subset.dataset.imgs[self.subset.indices[idx]]
            from PIL import Image
            img = Image.open(img).convert("RGB")
            return self.transform(img), label

    val_dataset  = TransformSubset(val_subset, val_tf)
    test_dataset = datasets.ImageFolder(str(test_dir), transform=val_tf)

    workers = 0 if DEVICE.type == "cpu" else 2

    train_loader = DataLoader(train_subset,  batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=workers, pin_memory=(DEVICE.type=="cuda"))
    val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=workers, pin_memory=(DEVICE.type=="cuda"))
    test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=workers, pin_memory=(DEVICE.type=="cuda"))

    print(f"\n[INFO] Classes ({num_classes}): {class_names[:5]} ...")
    print(f"[INFO] Train: {n_train} | Val: {n_val} | Test: {len(test_dataset)}")
    return train_loader, val_loader, test_loader, class_names


# ──────────────────────────────────────────────────────────────
#  STEP 4 — MODEL (ResNet50 + Dropout + Custom FC)
# ──────────────────────────────────────────────────────────────
def build_model(num_classes: int) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

    # Freeze all layers
    for param in model.parameters():
        param.requires_grad = False

    # Unfreeze layer4 only (plus fc below)
    for param in model.layer4.parameters():
        param.requires_grad = True

    # Replace FC: Dropout(0.5) -> Linear(num_classes)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(DROPOUT),
        nn.Linear(in_features, num_classes)
    )
    model = model.to(DEVICE)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"[INFO] Trainable: {trainable:,} / {total:,} params")
    return model


# ──────────────────────────────────────────────────────────────
#  STEP 5 — TRAINING LOOP
# ──────────────────────────────────────────────────────────────
def run_epoch(model, loader, criterion, optimizer=None):
    """Single epoch — training if optimizer given, else eval."""
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    total_loss, correct, total = 0.0, 0, 0
    ctx = torch.enable_grad() if is_train else torch.no_grad()

    with ctx:
        for inputs, labels in loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            if is_train:
                optimizer.zero_grad()
            outputs = model(inputs)
            loss    = criterion(outputs, labels)
            if is_train:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * inputs.size(0)
            _, preds = outputs.max(1)
            correct  += preds.eq(labels).sum().item()
            total    += inputs.size(0)

    return total_loss / total, correct / total


def train(model, train_loader, val_loader, class_names):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR, weight_decay=WEIGHT_DECAY
    )
    scheduler = ReduceLROnPlateau(
        optimizer, mode="min", patience=LR_PATIENCE, factor=LR_FACTOR
    )

    history   = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val  = float("inf")
    no_improve = 0

    print("\n" + "="*65)
    print("  TRAINING — ResNet50 Transfer Learning on PlantDoc")
    print("="*65)
    print(f"  Epochs={EPOCHS}  BatchSize={BATCH_SIZE}  LR={LR}  EarlyStop={EARLY_STOP_PATIENCE}")
    print("="*65)

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()
        tr_loss, tr_acc = run_epoch(model, train_loader, criterion, optimizer)
        vl_loss, vl_acc = run_epoch(model, val_loader,   criterion)
        elapsed = time.time() - t0

        scheduler.step(vl_loss)

        history["train_loss"].append(tr_loss)
        history["val_loss"].append(vl_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(vl_acc)

        flag = ""
        if vl_loss < best_val:
            best_val   = vl_loss
            no_improve = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": vl_loss,
                "val_acc":  vl_acc,
                "class_names": class_names,
            }, str(MODEL_PATH))
            flag = " [OK] BEST"
        else:
            no_improve += 1
            flag = f" (no improve {no_improve}/{EARLY_STOP_PATIENCE})"

        print(
            f"Ep[{epoch:02d}/{EPOCHS}] "
            f"TrLoss={tr_loss:.4f} TrAcc={tr_acc*100:.1f}% | "
            f"VlLoss={vl_loss:.4f} VlAcc={vl_acc*100:.1f}% | "
            f"{elapsed:.0f}s{flag}"
        )

        if no_improve >= EARLY_STOP_PATIENCE:
            print(f"\n[STOP]  Early stopping at epoch {epoch}.")
            break

    print(f"\n[INFO] Best val_loss={best_val:.4f} — model saved -> {MODEL_PATH}")
    return history


# ──────────────────────────────────────────────────────────────
#  STEP 6 — PLOT TRAINING CURVES
# ──────────────────────────────────────────────────────────────
def plot_curves(history):
    ep = range(1, len(history["train_loss"]) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Krishi AI — ResNet50 Training Curves", fontsize=13, fontweight="bold")

    ax1.plot(ep, history["train_loss"], label="Train", color="#2563eb")
    ax1.plot(ep, history["val_loss"],   label="Val",   color="#dc2626")
    ax1.set_title("Loss"); ax1.set_xlabel("Epoch"); ax1.set_ylabel("Cross-Entropy Loss")
    ax1.legend(); ax1.grid(alpha=0.3)

    ax2.plot(ep, [x*100 for x in history["train_acc"]], label="Train", color="#16a34a")
    ax2.plot(ep, [x*100 for x in history["val_acc"]],   label="Val",   color="#d97706")
    ax2.set_title("Accuracy"); ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy (%)")
    ax2.legend(); ax2.grid(alpha=0.3)

    plt.tight_layout()
    out = OUTPUT_DIR / "training_curves.png"
    plt.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Training curves -> {out}")


# ──────────────────────────────────────────────────────────────
#  STEP 7 — EVALUATION
# ──────────────────────────────────────────────────────────────
def evaluate(model, test_loader, class_names):
    model.eval()
    all_preds, all_labels = [], []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(DEVICE)
            _, preds = model(inputs).max(1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)

    acc = accuracy_score(all_labels, all_preds)
    print(f"\n{'='*65}")
    print(f"  TEST ACCURACY: {acc*100:.2f}%")
    print(f"{'='*65}")
    print(classification_report(all_labels, all_preds, target_names=class_names))

    # Save CSV report
    report = classification_report(
        all_labels, all_preds, target_names=class_names, output_dict=True
    )
    with open(REPORT_CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["class","precision","recall","f1-score","support"])
        w.writeheader()
        for cls, m in report.items():
            if isinstance(m, dict):
                w.writerow({"class": cls,
                             "precision": round(m.get("precision",0), 4),
                             "recall":    round(m.get("recall",   0), 4),
                             "f1-score":  round(m.get("f1-score", 0), 4),
                             "support":   int(m.get("support",   0))})
    print(f"[INFO] Report CSV -> {REPORT_CSV_PATH}")

    # Confusion matrix
    n  = len(class_names)
    cm = confusion_matrix(all_labels, all_preds)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    fig_sz  = max(10, n // 2)
    ann_sz  = max(5, 10 - n // 8)
    fig, ax = plt.subplots(figsize=(fig_sz, fig_sz - 1))
    sns.heatmap(cm_norm, annot=(n <= 30), fmt=".2f" if n <= 30 else "",
                xticklabels=class_names, yticklabels=class_names,
                cmap="YlOrRd", ax=ax, linewidths=0.3,
                annot_kws={"size": ann_sz})
    ax.set_title("Confusion Matrix (Normalized)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    plt.xticks(rotation=45, ha="right", fontsize=ann_sz)
    plt.yticks(rotation=0,  fontsize=ann_sz)
    plt.tight_layout()
    cm_path = OUTPUT_DIR / "confusion_matrix.png"
    plt.savefig(str(cm_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Confusion matrix -> {cm_path}")
    return acc


# ──────────────────────────────────────────────────────────────
#  STEP 8 — EXPORT TO ONNX
# ──────────────────────────────────────────────────────────────
def export_onnx(model):
    model.eval()
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
    torch.onnx.export(
        model, dummy, str(ONNX_PATH),
        export_params=True, opset_version=11,
        do_constant_folding=True,
        input_names=["input"], output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    )
    print(f"[INFO] ONNX model -> {ONNX_PATH}")


# ──────────────────────────────────────────────────────────────
#  STEP 9 — SAVE METADATA
# ──────────────────────────────────────────────────────────────
def save_metadata(class_names):
    with open(CLASS_NAMES_PATH, "w") as f:
        json.dump(class_names, f, indent=2)
    with open(LABEL_MAP_PATH, "w") as f:
        json.dump({str(i): n for i, n in enumerate(class_names)}, f, indent=2)
    print(f"[INFO] class_names.json + label_map.json -> {OUTPUT_DIR}")


# ──────────────────────────────────────────────────────────────
#  STEP 10 — PREDICTION FUNCTION
# ──────────────────────────────────────────────────────────────
def predict_disease(image_path: str, model=None, class_names=None):
    """
    Predict plant disease from a leaf image.
    Returns: {class_index, class_name, confidence, top3_predictions}
    """
    from PIL import Image

    if class_names is None:
        with open(CLASS_NAMES_PATH) as f:
            class_names = json.load(f)
    if model is None:
        ckpt  = torch.load(str(MODEL_PATH), map_location=DEVICE)
        model = build_model(len(class_names))
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()

    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    img    = Image.open(image_path).convert("RGB")
    tensor = val_tf(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]

    k = min(3, len(class_names))
    top_vals, top_idxs = torch.topk(probs, k)
    top3 = [
        {"class_name": class_names[idx.item()],
         "confidence": round(val.item() * 100, 2)}
        for idx, val in zip(top_idxs, top_vals)
    ]
    return {
        "class_index":      top_idxs[0].item(),
        "class_name":       class_names[top_idxs[0].item()],
        "confidence":       round(top_vals[0].item() * 100, 2),
        "top3_predictions": top3,
    }


# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*65)
    print("  Krishi AI — PyTorch Plant Disease CNN Pipeline")
    print("="*65)

    # 1. Extract dataset
    train_dir, test_dir = extract_dataset()

    # 2. Transforms + loaders
    train_tf, val_tf = get_transforms()
    train_loader, val_loader, test_loader, class_names = build_loaders(
        train_dir, test_dir, train_tf, val_tf
    )

    # 3. Save metadata early
    save_metadata(class_names)

    # 4. Build model
    model = build_model(len(class_names))

    # 5. Train
    history = train(model, train_loader, val_loader, class_names)

    # 6. Plot curves
    plot_curves(history)

    # 7. Load best checkpoint -> evaluate on test set
    print("\n[INFO] Loading best checkpoint for final evaluation ...")
    ckpt = torch.load(str(MODEL_PATH), map_location=DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])

    evaluate(model, test_loader, class_names)

    # 8. Export ONNX
    export_onnx(model)

    # 9. Summary
    print("\n" + "="*65)
    print("  OUTPUT FILES")
    print("="*65)
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.name:<45} {f.stat().st_size/1024:>8.1f} KB")
    print(f"\n[OK] Done! Best model -> {MODEL_PATH}")


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) == 2 and Path(sys.argv[1]).exists():
        result = predict_disease(sys.argv[1])
        print(f"\n Disease   : {result['class_name']}")
        print(f" Confidence: {result['confidence']}%")
        print( " Top-3     :")
        for p in result["top3_predictions"]:
            print(f"   {p['class_name']:<40} {p['confidence']:5.1f}%")
    else:
        main()
