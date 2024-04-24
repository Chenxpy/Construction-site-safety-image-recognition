import streamlit as st
from skimage import io
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt  # 新增這一行
from ultralytics.utils.plotting import Annotator
from PIL import Image  # 1024
import cv2
# 載入模型


model = YOLO('best.pt')
# image = Image.open("Image.jpg")
# results = model(image)
cap = cv2.VideoCapture(0)


while cap.isOpened():
    success, frame = cap.read()
    if success:

        results = model(frame)

        annotated_frame = results[0].plot()

        # print(results[0].names)

        try:
            # 顯示結果
            print("檢測結果")

            xyxys = []
            class_ids = []
            # 將辨識的結果逐一讀取
            for result in results:
                boxes = result.boxes.cpu().numpy()
                xyxys.append(boxes.xyxy)
                class_ids.append(boxes.cls)
                name = result.names
            print(class_ids)
            print(name)
        except Exception as e:
            print(f"Error during prediction: {e}")

        cv2.imshow("YOLOv8 Inference", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
