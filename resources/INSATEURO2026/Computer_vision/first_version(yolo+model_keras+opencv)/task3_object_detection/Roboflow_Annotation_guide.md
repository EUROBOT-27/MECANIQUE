# ENSI Cubes & Triangles Annotation Guide

## 1️⃣ Purpose
The goal of this project is to label all cubes and triangles visible in the images so that the YOLO model can be trained to detect and count them during the ENSI competition.

---

## 2️⃣ Classes
- **cube** → any cube object in the image.  
- **triangle** → any triangle object in the image.

> **Tip:** Keep naming consistent (always lowercase: `cube`, `triangle`).

---

## 3️⃣ How to Draw Bounding Boxes
1. Draw the box **tight around the object**, but include the full shape.  
2. Avoid including too much background.  
3. Ensure boxes **don’t overlap** unless there are multiple stacked objects.  
4. Include partially visible objects only if **at least 50% is visible**.

---

## 4️⃣ Tips for Consistency
- Zoom in if necessary to draw precise boxes.  
- Use the **Instant Annotator suggestions** when available; correct them if inaccurate.  
- Keep the same labeling style throughout the dataset.  
- If the object is **unclear or blurry**, mark it with a comment instead of labeling.

---

## 5️⃣ Workflow
1. Open images in **Roboflow Instant Annotator**.  
2. Select the class (`cube` or `triangle`).  
3. Draw bounding box around each object in the image.  
4. Review boxes before submitting the annotation.  
5. Move on to the next image.

---

## 6️⃣ Quality Control
- Every 20–50 images, review labels for consistency.  
- Make sure all objects are labeled — none should be missed.  
- Keep images in proper folders: `train`, `val`, `test`.

---

## 7️⃣ Optional Notes
- Use uniform lighting and camera angles when capturing new images.  
- Save backups of your dataset regularly.
