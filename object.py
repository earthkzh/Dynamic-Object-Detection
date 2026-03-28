# ===================================
# Dynamic Image Detection with Voice
# ===================================

import cv2
import numpy as np
from ultralytics import YOLO
from tkinter import Tk, filedialog
from gtts import gTTS
import pygame
import os
import uuid

Tk().withdraw()
image_path = filedialog.askopenfilename(
    title="Select an Image",
    filetypes=[
    ("Supported Images", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
    ("All Files", "*.*")
]
)
if not image_path:
    print("No image selected. Exiting.")
    exit()

img = cv2.imread(image_path)
img_copy = img.copy()

max_width, max_height = 940 ,680
scale = min(max_width / img.shape[1], max_height / img.shape[0])
if scale < 1:
    img = cv2.resize(img, (int(img.shape[1]*scale), int(img.shape[0]*scale)), interpolation=cv2.INTER_AREA)
    img_copy = img.copy()

model = YOLO("yolov8n.pt")

def speak(text):
    filename = f"{uuid.uuid4()}.mp3"

    tts = gTTS(text=text, lang='en', tld='com')
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(50)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    os.remove(filename)
    pygame.mixer.quit()   

def estimate_color(roi, label):
    if roi is None or roi.size == 0:
        return "Unknown"
    if label == "person":
        h, w = roi.shape[:2]
        y1 = int(0.05 * h)
        y2 = int(0.30 * h)
        x1 = int(0.25 * w)
        x2 = int(0.75 * w)

        roi = roi[y1:y2, x1:x2]

        if roi.size == 0:
            return "Unknown"
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    H = hsv[:, :, 0]
    S = hsv[:, :, 1]
    V = hsv[:, :, 2]
    mask = (V > 40) & (S > 20)

    H = H[mask]
    S = S[mask]
    V = V[mask]

    if len(H) < 30:
        return "Unknown"
    h_med = float(np.median(H))
    s_med = float(np.median(S))
    v_med = float(np.median(V))
    if label == "person":

        # Black hair (dark value)
        if v_med < 65:
            return "Black"

        # White / gray hair
        elif s_med < 40 and v_med > 170:
            return "White / Gray"

        # Brown hair
        elif 8 <= h_med < 25 and 50 <= s_med <= 170:
            return "Brown"

        # Blonde hair (yellowish, bright)
        elif 20 <= h_med <= 38 and s_med < 140 and v_med > 120:
            return "Blonde"

        # Dyed colors
        elif 125 <= h_med < 160:
            return "Purple / Pink"

        else:
            return "Mixed Hair"
    else:

        if v_med < 60:
            return "Black"

        elif v_med > 200 and s_med < 40:
            return "White"

        # Red wraps HSV circle
        elif h_med < 10 or h_med >= 170:
            return "Red"

        elif 10 <= h_med < 25:
            return "Orange"

        elif 25 <= h_med < 35:
            return "Yellow / Brown"

        elif 35 <= h_med < 85:
            return "Green"

        elif 85 <= h_med < 125:
            return "Blue"

        elif 125 <= h_med < 160:
            return "Purple / Pink"

        else:
            return "Mixed"

clicked_x, clicked_y = -1, -1
def mouse_event(event, x, y, flags, param):
    global clicked_x, clicked_y
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_x, clicked_y = x, y

cv2.namedWindow("Dynamic Object Detection")
cv2.setMouseCallback("Dynamic Object Detection", mouse_event)

results = model(img)

selected_box = None
selected_label = ""
selected_color = ""
situation = ""
description = ""
spoken = False

while True:
    display = img_copy.copy()
    if clicked_x != -1 and clicked_y != -1:
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                if x1 < clicked_x < x2 and y1 < clicked_y < y2:
                    cls = int(box.cls[0])
                    selected_label = model.names[cls]
                    roi = img[y1:y2, x1:x2]
                    selected_color = estimate_color(roi, selected_label)
                    selected_box = (x1, y1, x2, y2)

                    pos_x = "left" if clicked_x < img.shape[1]//3 else "right" if clicked_x > 2*img.shape[1]//3 else "center"
                    pos_y = "top" if clicked_y < img.shape[0]//3 else "bottom" if clicked_y > 2*img.shape[0]//3 else "middle"
                    situation = f"{pos_y}-{pos_x} of image"

                    description = f"This is a {selected_label} with {selected_color} color, located at {situation}."

                    clicked_x, clicked_y = -1, -1
                    spoken = False
                    break

    if selected_box is not None:
        x1, y1, x2, y2 = selected_box
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            display,f"{selected_label}, {selected_color}, {situation}",
            (x1, y1 - 10),cv2.FONT_HERSHEY_SIMPLEX,
            0.6,(255, 0, 0),2)
        cv2.imshow("Dynamic Object Detection", display)
        cv2.waitKey(1)
        if not spoken:
            print(description)
            speak(description)
            spoken = True
    else:
        cv2.imshow("Dynamic Object Detection", display)
    key = cv2.waitKey(20) & 0xFF
    if key == 27:
        break
    if cv2.getWindowProperty("Dynamic Object Detection", cv2.WND_PROP_AUTOSIZE) < 1:
        break

cv2.destroyAllWindows()



