# 工地安全影像辨識
## 前言
為了降低或避免發生工地勞工意外之安全事故，透過事先之風險辨識與處置，改善工地勞安意外問題。利用影像辨識(OpenCV)、影像標註(LabelImg)和物件偵測(YOLOv8)訓練辨識模型，達成人臉辨識、偵測安全裝備配戴狀況，並結合MySQL資料庫實現紀錄存取之功能。
## 系統架構圖
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/d2859420-00f2-4f99-845c-ceaca82a93b9)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/d0af77df-1ea6-4da1-9d3c-0ddd65d0a428)
## LabelImg & YOLOv8
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/be1250ac-fec1-499f-a092-482e89d8f273)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/0ca2c191-ad62-4c31-a747-e8286e0914d8)  
利用LabelImg先標註裝備蒐集素材，之後使用YOLOv8進行訓練，並查看訓練結果。
## 手勢辨識
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/e103d0b6-b204-4b5e-8b47-1dfab73addae)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/7e1641db-6a8b-41e8-b0cf-15f57751b523)  
利用OpenCV的Cvzone套件進行手部動作檢測，其函數接受RGB影像，並檢測畫面中的手且定位關鍵點再繪製出圖標。
## MySQL資料庫
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/6f14d244-fcfd-47e7-933b-93c446e45634)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/c9697639-fb5c-4d94-9a83-230f720c83f3)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/76c9e5c6-2e14-477c-a328-99ea9c7e8081)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/e65ba438-8269-4ff8-a0d1-c11ace477cb0)  
利用MySQL 資料庫表單存取人員註冊狀況以及出入紀錄，內容包括工號、姓名、圖片等資訊，並結合Flask將表單內容顯示於網頁上。
## Flask
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/609a87d4-7499-4164-a41d-d3c7fa6ae8bd)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/5395f93f-8bbe-4cdb-a9cb-8141bb314f8a)
![image](https://github.com/Chenxpy/Construction-site-safety-image-recognition/assets/136484111/e253dda9-f537-428d-8d17-425641e59dda)  
Flask網頁內容包含註冊頁面、辨識頁面以及查詢頁面，與MySQL資料庫表單皆有連結，實現資料存入/讀取功能。
## 結論
在勞動人員進行高危險的工作項目時，其配戴的安全裝備是不可或缺的。本專題目的是透過裝備辨識並搭配網頁顯示出入紀錄等資訊，達到方便管理且提升人員安全裝備穿戴率。在學習影像辨識或網頁架設時，了解其中的原理，並將兩種領域結合在樹莓派上，進而實現專題成果。
