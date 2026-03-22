from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from torchvision import transforms, models
from torch import nn
import json
import io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Fertilizer Mapping
# ============================================================
FERTILIZER_MAP = {
    "Pepper__bell___Bacterial_spot": {
        "disease": "Bacterial Spot",
        "crop": "Bell Pepper",
        "cause": "Xanthomonas bacteria",
        "fertilizer": "Copper-based fungicide spray",
        "treatment": "Remove infected leaves, apply copper hydroxide spray",
        "prevention": "Avoid overhead watering, use disease-free seeds"
    },
    "Pepper__bell___healthy": {
        "disease": "Healthy",
        "crop": "Bell Pepper",
        "cause": "No disease detected",
        "fertilizer": "Balanced NPK (10-10-10)",
        "treatment": "No treatment needed",
        "prevention": "Regular monitoring and watering"
    },
    "Potato___Early_blight": {
        "disease": "Early Blight",
        "crop": "Potato",
        "cause": "Alternaria solani fungus",
        "fertilizer": "Mancozeb + Potassium-rich fertilizer",
        "treatment": "Apply Mancozeb spray every 7-10 days",
        "prevention": "Crop rotation, remove infected leaves"
    },
    "Potato___Late_blight": {
        "disease": "Late Blight",
        "crop": "Potato",
        "cause": "Phytophthora infestans",
        "fertilizer": "Metalaxyl + Phosphorus fertilizer",
        "treatment": "Apply Metalaxyl-M spray immediately",
        "prevention": "Avoid excess moisture, use resistant varieties"
    },
    "Potato___healthy": {
        "disease": "Healthy",
        "crop": "Potato",
        "cause": "No disease detected",
        "fertilizer": "NPK 12-32-16 for tuber development",
        "treatment": "No treatment needed",
        "prevention": "Regular monitoring"
    },
    "Tomato_Bacterial_spot": {
        "disease": "Bacterial Spot",
        "crop": "Tomato",
        "cause": "Xanthomonas bacteria",
        "fertilizer": "Copper oxychloride spray",
        "treatment": "Apply copper-based bactericide weekly",
        "prevention": "Use certified disease-free seeds"
    },
    "Tomato_Early_blight": {
        "disease": "Early Blight",
        "crop": "Tomato",
        "cause": "Alternaria solani fungus",
        "fertilizer": "Chlorothalonil + Nitrogen fertilizer",
        "treatment": "Apply Chlorothalonil every 7 days",
        "prevention": "Mulching, avoid wetting leaves"
    },
    "Tomato_Late_blight": {
        "disease": "Late Blight",
        "crop": "Tomato",
        "cause": "Phytophthora infestans",
        "fertilizer": "Cymoxanil + Potassium fertilizer",
        "treatment": "Apply Cymoxanil spray immediately",
        "prevention": "Improve air circulation, avoid overhead irrigation"
    },
    "Tomato_Leaf_Mold": {
        "disease": "Leaf Mold",
        "crop": "Tomato",
        "cause": "Passalora fulva fungus",
        "fertilizer": "Mancozeb spray + Calcium fertilizer",
        "treatment": "Reduce humidity, apply fungicide",
        "prevention": "Good ventilation in greenhouse"
    },
    "Tomato_Septoria_leaf_spot": {
        "disease": "Septoria Leaf Spot",
        "crop": "Tomato",
        "cause": "Septoria lycopersici fungus",
        "fertilizer": "Chlorothalonil + Balanced NPK",
        "treatment": "Remove infected leaves, apply fungicide",
        "prevention": "Avoid overhead watering, crop rotation"
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "disease": "Spider Mites",
        "crop": "Tomato",
        "cause": "Tetranychus urticae mites",
        "fertilizer": "Abamectin miticide spray",
        "treatment": "Apply miticide, increase humidity",
        "prevention": "Regular inspection, avoid water stress"
    },
    "Tomato__Target_Spot": {
        "disease": "Target Spot",
        "crop": "Tomato",
        "cause": "Corynespora cassiicola fungus",
        "fertilizer": "Azoxystrobin fungicide",
        "treatment": "Apply Azoxystrobin spray",
        "prevention": "Crop rotation, remove plant debris"
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "disease": "Yellow Leaf Curl Virus",
        "crop": "Tomato",
        "cause": "Begomovirus (whitefly transmitted)",
        "fertilizer": "Imidacloprid insecticide (whitefly control)",
        "treatment": "Remove infected plants, control whiteflies",
        "prevention": "Use virus-resistant varieties, yellow sticky traps"
    },
    "Tomato__Tomato_mosaic_virus": {
        "disease": "Mosaic Virus",
        "crop": "Tomato",
        "cause": "Tomato mosaic virus (ToMV)",
        "fertilizer": "No chemical cure — remove infected plants",
        "treatment": "Remove and destroy infected plants immediately",
        "prevention": "Sanitize tools, use virus-free seeds"
    },
    "Tomato_healthy": {
        "disease": "Healthy",
        "crop": "Tomato",
        "cause": "No disease detected",
        "fertilizer": "Balanced NPK (8-32-16) for fruiting",
        "treatment": "No treatment needed",
        "prevention": "Regular monitoring and proper irrigation"
    }
}

# ============================================================
# Model Load
# ============================================================
print("Model load ho raha hai...")

with open("./classes.json") as f:
    classes = json.load(f)

device = torch.device("cpu")

model = models.resnet18(weights=None)
model.fc = nn.Sequential(
    nn.Dropout(p=0.4),
    nn.Linear(model.fc.in_features, len(classes))
)

checkpoint = torch.load("./cropdoc-model.pth", map_location=device)
model.load_state_dict(checkpoint["model_state"])
model.eval()
print("Model ready!")

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ============================================================
# Endpoints
# ============================================================
@app.get("/")
def root():
    return {"message": "CropDoc API ready!"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Image read karo
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Transform + predict
    img_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred_idx = torch.max(probs, dim=1)

    predicted_class = classes[pred_idx.item()]
    confidence_score = round(confidence.item() * 100, 2)

    # Fertilizer recommendation lo
    recommendation = FERTILIZER_MAP.get(predicted_class, {
        "disease": "Unknown",
        "fertilizer": "Consult an expert",
        "treatment": "Unknown",
        "prevention": "Unknown"
    })

    return {
        "predicted_class": predicted_class,
        "confidence": confidence_score,
        "recommendation": recommendation
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)