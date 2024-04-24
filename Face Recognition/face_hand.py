import cv2
import pickle
import face_recognition
import numpy as np
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random

# 隨機產生指定動作
x = random.randrange(1, 5)
print(x)
hand_type = ["Right", "Left"]
y = random.choice(hand_type)
print(y)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
detector = HandDetector(detectionCon=0.5, maxHands=1)


# Load the encoding file
print("Loading Started...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithNames = pickle.load(file)
file.close()
encodeListKnown, peopleName = encodeListKnownWithNames
print(peopleName)
print("Encode File Loaded")


while True:
    success, img = cap.read()
    hands, img_hand = detector.findHands(img)

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if hands:
        hand = hands[0]
        bbox = hand['bbox']
        fingers = detector.fingersUp(hand)
        totalFingers = fingers.count(1)
        print(hand['type'])  # 取出左右手
        if (hand['type'] == y and totalFingers == x):
            print("success!!!")

            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(
                    encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(
                    encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)
                print("Match Index", matchIndex)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 230+y1, x2-x1, y2-y1

                if matches[matchIndex] & (faceDis[matchIndex] <= 0.5):
                    print("Known Face Detected")
                    print(peopleName[matchIndex])

                else:
                    print("Don't Known Face Detected")

    cv2.imshow("Camera", img)

    # cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
