#training script for finetuning the yolo model on our custom dataset
# We will use the ultralytics library for this purpose
# Make sure to install it via pip install ultralytics
# We will use the yolov8n model for this purpose as it is lightweight and suitable for Raspberry Pi


from ultralytics import YOLO

# Load YOLOv8 nano model (lightweight for Raspberry Pi)
model = YOLO("yolov8n.pt")

# Train
model.train(
    data=r"C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\task3_object_detection\final_version\Cube_Triangle_recognition_ENSI.v2-second_version.yolov8\data.yaml",  # path to your yaml
    epochs=50,                 # can tune later
    imgsz=640,                 # image size
    batch=16,                  # depends on GPU RAM
    device="cpu"                # use GPU if available
)
# Export to TFLite (best for Pi)
model.export(format="tflite", int8=True)

# You can also keep ONNX as backup
model.export(format="onnx")
