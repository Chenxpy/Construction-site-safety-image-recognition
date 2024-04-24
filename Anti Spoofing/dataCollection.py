from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone
from time import time

# ==============================
outFolderPath = 'Dataset/DataCollect'
save = True
debug = False
classID = 0  # 0 -> fake, 1-> real
blurThreshold = 35
confidence = 0.8
offsetPercentageW = 10
offsetPercentageH = 20
camWidth, camHeigh = 640, 480
floatingPoint = 6
# ==============================

cap = cv2.VideoCapture(0)
detector = FaceDetector()
cap.set(3, camWidth)
cap.set(4, camHeigh)

while True:
    success, img = cap.read()
    imgOut = img.copy()
    img, bboxs = detector.findFaces(img, draw=False)

    listBlur = []
    listInfo = []

    if bboxs:
        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            score = bbox["score"][0]
            # print(x, y, w, h)

            if score > confidence:  # 確認是辨識到人臉
                # =================加上在人臉辨識上偏移量==========================

                offsetW = (offsetPercentageW / 100) * w
                x = int(x - offsetW)
                w = int(w + offsetW*2)

                offsetH = (offsetPercentageH / 100) * h
                y = int(y - offsetH*3)
                h = int(h + offsetH*3.5)

            # =================避免超出畫面框========================
                if x < 0:
                    x = 0
                if y < 0:
                    y = 0
                if h < 0:
                    h = 0
                if w < 0:
                    w = 0

            # =================找到模糊數值==========================
                imgFace = img[y:y + h, x:x + w]
                cv2.imshow("Face", imgFace)
                blurValue = int(cv2.Laplacian(imgFace, cv2.CV_64F).var())
                if blurValue > blurThreshold:
                    listBlur.append(True)
                else:
                    listBlur.append(False)
            # =================找到一般數值==========================
                ih, iw, _ = img.shape
                xc, yc = x + w / 2, y + h / 2

                xcn, ycn = round(
                    xc / iw, floatingPoint), round(yc / ih, floatingPoint)
                wn, hn = round(
                    w / iw, floatingPoint), round(h / ih, floatingPoint)
                # print(xcn, ycn, wn, hn)

            # =================避免超出畫面框==========================
                if xcn > 1:
                    xcn = 1
                if ycn > 1:
                    ycn = 1
                if hn > 1:
                    hn = 1
                if wn > 1:
                    wn = 1

                listInfo.append(f"{classID} {xcn} {ycn} {wn} {hn}\n")

            # =================畫進行標示============================
                cv2.rectangle(imgOut, (x, y, w, h), (255, 0, 0), 3)
                cvzone.putTextRect(
                    imgOut, f'Score:{int(score*100)}% Blur:{blurValue}', (x, y-20), scale=2, thickness=2)

                if debug:  # 測試用 將標示框的圖存入資料夾
                    cv2.rectangle(img, (x, y, w, h), (255, 0, 0), 3)
                    cvzone.putTextRect(
                        img, f'Score:{int(score*100)}% Blur:{blurValue}', (x, y-20), scale=2, thickness=2)

        # =================儲存dataset============================
        if save:

            # =================image============================
            if all(listBlur) and listBlur != []:
                timeNow = time()
                timeNow = str(timeNow).split('.')
                timeNow = timeNow[0]+timeNow[1]
                print(timeNow)
                cv2.imwrite(f'{outFolderPath}/{timeNow}.jpg', img)
            # =================Label===============================
                for info in listInfo:
                    f = open(f'{outFolderPath}/{timeNow}.txt', 'a')
                    f.write(info)
                    f.close()

    cv2.imshow("Image", imgOut)
    cv2.waitKey(1)
