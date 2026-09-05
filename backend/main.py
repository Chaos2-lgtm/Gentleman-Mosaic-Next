from functools import lru_cache
import configparser
import os
from pathlib import Path
import shutil
import tempfile
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

app = FastAPI(title="Gentleman Mosaic Next NSFW & YOLO API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
LAUNCH_INI = ROOT_DIR / "config" / "launch.ini"

# Device detection for PyTorch
DEVICE = "cpu"
GPU_NAME = "CPU"
try:
    import torch
    if torch.cuda.is_available():
        DEVICE = "cuda:0"
        GPU_NAME = torch.cuda.get_device_name(0)
except Exception:
    pass

# Try importing Ultralytics YOLO
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except Exception:
    HAS_YOLO = False

# Try importing NudeNet
try:
    from nudenet import NudeDetector
    HAS_NUDENET = True
except Exception:
    HAS_NUDENET = False

MODEL_RESOLUTION = {
    "320n": 320,
    "640m": 640,
}

_loaded_yolo_models: Dict[str, Any] = {}

class UISettings(BaseModel):
    language: str = "zh"
    theme: str = "system"


def normalize_language(value: str) -> str:
    return "en" if str(value).strip().lower() == "en" else "zh"


def normalize_theme(value: str) -> str:
    v = str(value).strip().lower()
    if v in ("dark", "light", "system"):
        return v
    return "system"


def read_launch_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if not LAUNCH_INI.exists():
        return cfg

    try:
        raw = LAUNCH_INI.read_text(encoding="utf-8-sig")
    except Exception:
        raw = LAUNCH_INI.read_text(encoding="gbk", errors="ignore")

    cfg.read_string(raw)
    return cfg


def write_launch_config(cfg: configparser.ConfigParser) -> None:
    with LAUNCH_INI.open("w", encoding="utf-8") as f:
        cfg.write(f)


def get_ui_settings_from_ini() -> dict:
    cfg = read_launch_config()
    language = "zh"
    theme = "system"
    if cfg.has_section("ui"):
        language = normalize_language(cfg["ui"].get("language", "zh"))
        theme = normalize_theme(cfg["ui"].get("theme", "system"))
    return {"language": language, "theme": theme}


def save_ui_settings_to_ini(language: str, theme: str) -> dict:
    cfg = read_launch_config()
    if not cfg.has_section("ui"):
        cfg.add_section("ui")
    cfg.set("ui", "language", normalize_language(language))
    cfg.set("ui", "theme", normalize_theme(theme))
    write_launch_config(cfg)
    return get_ui_settings_from_ini()


def get_model_search_paths() -> List[Path]:
    paths = [
        ROOT_DIR / "models",
    ]
    cfg = read_launch_config()
    if cfg.has_section("models") and "model_dir" in cfg["models"]:
        raw = cfg["models"]["model_dir"].strip()
        custom_dir = (ROOT_DIR / raw) if not Path(raw).is_absolute() else Path(raw)
        if custom_dir.exists() and custom_dir not in paths:
            paths.insert(0, custom_dir)
    return [p for p in paths if p.exists()]


def discover_available_models() -> Dict[str, Dict[str, Any]]:
    models = {}

    if HAS_YOLO:
        for search_dir in get_model_search_paths():
            for ext in ("*.pt", "*.onnx"):
                for p in search_dir.glob(ext):
                    key = p.stem.lower()
                    if key not in models:
                        # Friendly labels
                        display_name = p.name
                        if "sensitive_detect" in key:
                            display_name = f"通用高精度 ({p.name})"
                        elif "anime_nsfw" in key or "ntd11" in key:
                            display_name = f"二次元動漫 ({p.name})"
                        elif "face" in key:
                            display_name = f"人臉部位 ({p.name})"

                        models[key] = {
                            "id": key,
                            "filename": p.name,
                            "path": str(p),
                            "name": display_name,
                            "type": "yolo",
                        }

    if HAS_NUDENET:
        for m_id, res in MODEL_RESOLUTION.items():
            models[m_id] = {
                "id": m_id,
                "filename": f"nudenet_{m_id}",
                "name": f"NudeNet {m_id} (CPU 備用)",
                "type": "nudenet",
            }

    return models


def load_yolo_model(model_key_or_path: str):
    if not HAS_YOLO:
        raise RuntimeError("Ultralytics YOLO is not installed.")

    if model_key_or_path in _loaded_yolo_models:
        return _loaded_yolo_models[model_key_or_path]

    available = discover_available_models()
    model_path = None
    if model_key_or_path in available and "path" in available[model_key_or_path]:
        model_path = available[model_key_or_path]["path"]
    elif Path(model_key_or_path).is_file():
        model_path = model_key_or_path
    else:
        # Match by partial name
        for k, v in available.items():
            if model_key_or_path.lower() in k or k in model_key_or_path.lower():
                model_path = v.get("path")
                break

    if not model_path:
        raise FileNotFoundError(f"YOLO model not found for: {model_key_or_path}")

    model = YOLO(model_path)
    _loaded_yolo_models[model_key_or_path] = model
    return model


@lru_cache(maxsize=2)
def get_nudenet_detector(model: str):
    if not HAS_NUDENET:
        raise RuntimeError("NudeNet is not installed.")
    resolution = MODEL_RESOLUTION.get(model, 320)
    return NudeDetector(inference_resolution=resolution)


@app.get("/health")
def health():
    models = discover_available_models()
    return {
        "ok": True,
        "device": DEVICE,
        "gpu_name": GPU_NAME,
        "has_yolo": HAS_YOLO,
        "has_nudenet": HAS_NUDENET,
        "models_count": len(models),
        "available_models": list(models.values()),
    }


@app.get("/models")
def get_models():
    models = discover_available_models()
    # Also inspect classes for YOLO models
    model_list = []
    for key, info in models.items():
        classes = []
        if info["type"] == "yolo" and "path" in info:
            try:
                m = load_yolo_model(key)
                if hasattr(m, "names") and isinstance(m.names, dict):
                    classes = list(m.names.values())
            except Exception:
                pass
        elif info["type"] == "nudenet":
            classes = ["FEMALE_GENITALIA_EXPOSED", "MALE_GENITALIA_EXPOSED", "FEMALE_BREAST_EXPOSED", "ANUS_EXPOSED"]

        model_list.append({
            **info,
            "classes": classes,
        })

    return {
        "device": DEVICE,
        "gpu_name": GPU_NAME,
        "models": model_list,
    }


@app.get("/ui-settings")
def get_ui_settings():
    return get_ui_settings_from_ini()


@app.post("/ui-settings")
def set_ui_settings(settings: UISettings):
    saved = save_ui_settings_to_ini(settings.language, settings.theme)
    return {"ok": True, **saved}


@app.post("/detect-nsfw")
async def detect_nsfw(
    file: UploadFile = File(...),
    threshold: float = Query(0.25, ge=0.01, le=1.0, description="Confidence threshold between 0.01 and 1.0"),
    model: str = Query("sensitive_detect_v06"),
    classes: Optional[str] = Query(None, description="Comma-separated target classes, e.g. pussy,penis,nipple,anus"),
    padding: int = Query(6, ge=0, le=100, description="Expand bounding box by N pixels"),
):
    available = discover_available_models()

    # Determine which engine to use
    chosen_type = "yolo"
    if model in MODEL_RESOLUTION or (model in available and available[model]["type"] == "nudenet"):
        chosen_type = "nudenet"
    elif not HAS_YOLO and HAS_NUDENET:
        chosen_type = "nudenet"

    suffix = os.path.splitext(file.filename or "image.png")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Get image dimensions
        with Image.open(tmp_path) as img:
            img_w, img_h = img.size

        filter_classes = set([c.strip().lower() for c in classes.split(",") if c.strip()]) if classes else set()

        out = []

        if chosen_type == "yolo":
            yolo_model = load_yolo_model(model)
            results = yolo_model(tmp_path, conf=threshold, device=DEVICE, verbose=False)

            for r in results:
                names = r.names
                boxes = r.boxes
                masks = getattr(r, "masks", None)
                if boxes is not None and len(boxes) > 0:
                    for i in range(len(boxes)):
                        box_tensor = boxes.xyxy[i].cpu().numpy()
                        cls_idx = int(boxes.cls[i].item())
                        score = float(boxes.conf[i].item())
                        cls_name = names.get(cls_idx, str(cls_idx))

                        if filter_classes and cls_name.lower() not in filter_classes:
                            continue

                        x1, y1, x2, y2 = box_tensor[:4]
                        # Apply padding
                        x1 = max(0, int(x1) - padding)
                        y1 = max(0, int(y1) - padding)
                        x2 = min(img_w, int(x2) + padding)
                        y2 = min(img_h, int(y2) + padding)

                        w = max(1, x2 - x1)
                        h = max(1, y2 - y1)

                        polygon = None
                        if masks is not None and hasattr(masks, "xy") and i < len(masks.xy):
                            raw_pts = masks.xy[i]
                            if len(raw_pts) >= 3:
                                polygon = [[round(float(pt[0]), 1), round(float(pt[1]), 1)] for pt in raw_pts]

                        out.append({
                            "class": cls_name,
                            "score": round(score, 3),
                            "box": [x1, y1, w, h],
                            "polygon": polygon,
                            "model": model,
                        })

        else:
            # Fallback to NudeNet
            detector = get_nudenet_detector(model)
            preds = detector.detect(tmp_path) or []
            for p in preds:
                score = float(p.get("score", 0))
                if score < threshold:
                    continue

                box = p.get("box") or [0, 0, 0, 0]
                if len(box) != 4:
                    continue

                x, y, w, h = box
                cls_name = p.get("class", "unknown")
                if filter_classes and cls_name.lower() not in filter_classes:
                    continue

                x1 = max(0, int(x) - padding)
                y1 = max(0, int(y) - padding)
                w = min(img_w - x1, int(w) + padding * 2)
                h = min(img_h - y1, int(h) + padding * 2)

                out.append({
                    "class": cls_name,
                    "score": round(score, 3),
                    "box": [x1, y1, w, h],
                    "model": model,
                })

        return {
            "ok": True,
            "detections": out,
            "count": len(out),
            "model": model,
            "device": DEVICE,
            "gpu_name": GPU_NAME,
        }
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
