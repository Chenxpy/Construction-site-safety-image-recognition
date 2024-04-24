from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import os
import base64
import secrets
from datetime import datetime, date, timedelta
import io
from PIL import Image
import cv2
import face_recognition
import pickle
import numpy as np
from sqlalchemy import create_engine, select
# from sqlalchemy.orm import session
from flask_socketio import SocketIO
from ultralytics import YOLO
import matplotlib.pyplot as plt  # 新增這一行
from ultralytics.utils.plotting import Annotator
from cvzone.HandTrackingModule import HandDetector
import random


# 取得啟動文件資料夾路徑
pjdir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# -------------資料庫設定---------------#
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test:12345678@localhost/Topics'
# 隨機設定密碼
app.config['SECRET_KEY'] = secrets.token_hex(16)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
socketio = SocketIO(app)
# -------------------------------------#


# ------------資料庫Table建置-----------#
class UserRegister(db.Model):
    """資料庫紀錄"""
    __tablename__ = 'UserRegisters'
    number = db.Column(db.String(9), unique=True,
                       nullable=False, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    signup_time = db.Column(db.DateTime, default=datetime.utcnow)
    captured_image = db.Column(db.LargeBinary)
    encode_data = db.Column(db.LargeBinary)

    def __repr__(self):
        return 'ID:%d, Username:%s' % (self.number, self.username)
# ------------第二個表格建置-----------#


class History(db.Model):
    __tablename__ = 'History'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(9), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'ID: {self.id},Number: {self.number}, Username: {self.username}, In Time: {self.in_time}'
# ------------第三個表格建置-----------#


class EntranceRecord(db.Model):
    __tablename__ = 'EntranceRecord'  # 要記得加
    entry_id = db.Column(db.String(9), nullable=False)
    entry_name = db.Column(db.String(80), nullable=False)
    entry_time = db.Column(db.DateTime, primary_key=True)
    in_out = db.Column(db.String(2), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        in_out_text = "入" if self.in_out == "入" else "出"  # 根據字串欄位的值來判斷出入狀態並使用中文表示
        return f"Entry ID: {self.entry_id}, Entry Name: {self.entry_name}, Entry Time: {self.entry_time}, In/Out: {in_out_text},photo:{self.photo}"


# ---------------------------------------#
# 創建表格（如果還不存在）
with app.app_context():
    db.create_all()
# --------------------------------------#

# -----------------------------------------註冊網頁---------------------------------------------#


@app.route('/register', methods=['GET', 'POST'])
def register():
    error1 = False
    error2 = False
    error3 = False
    success = False
    if request.method == 'POST':
        number = request.form['number']
        username = request.form['username']
        capturedImageData = request.form['capturedImageData']
        signup_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 判斷是否有輸入
        if not number or not username:
            error1 = True
        elif len(number) < 9:
            error3 = True
        else:
            # 檢查是否存在相同工號
            existing_user = UserRegister.query.filter_by(number=number).first()
            if existing_user:
                error2 = True
            else:
                binary_data = base64.b64decode(capturedImageData.split(',')[1])

                # 轉face recognition encode
                image_pil = Image.open(io.BytesIO(binary_data))
                image_np = np.array(image_pil)
                img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encode_data = pickle.dumps(encode)

                new_user = UserRegister(
                    number=number, username=username, signup_time=signup_time, captured_image=binary_data, encode_data=encode_data)
                db.session.add(new_user)
                db.session.commit()
                success = True
    return render_template('register.html', error1=error1, error2=error2, success=success)
# --------------------------------------------------------------------------------------------#

# -----------------------------------------已註冊查看網頁---------------------------------------------#


@app.route('/view_users', methods=['GET'])
def view_users():
    search_query = request.args.get('search_query')

    if search_query:
        pass
    else:
        # 如果沒有搜尋條件，顯示本日的刷臉紀錄
        today = date.today()
        entrance_record = EntranceRecord.query.filter(
            db.func.DATE(EntranceRecord.entry_time) == today
        ).all()
        return render_template('view.html', entrance_record=entrance_record)


@app.route('/search', methods=['GET'])
def search():
    search_date = request.args.get('search_date')
    search_id = request.args.get('search_id')
    selected_date = search_date  # 將選定的日期設定為selected_date

    if search_date and search_id:
        # 如果日期和工號都存在，則執行日期和工號的同時搜尋
        try:
            formatted_date = datetime.strptime(search_date, '%Y-%m-%d')
            entrance_record = EntranceRecord.query.filter(
                db.func.DATE(EntranceRecord.entry_time) == formatted_date,
                EntranceRecord.entry_id == search_id
            ).all()
            return render_template('view.html', entrance_record=entrance_record, selected_date=search_date, selected_id=search_id)
        except ValueError:
            # 處理無效日期格式的情況
            error_message = "請提供有效的日期格式（YYYY-MM-DD）"
            return render_template('view.html', error_message=error_message)

    elif search_date:
        # 如果只有日期存在，則執行日期的搜尋
        try:
            formatted_date = datetime.strptime(search_date, '%Y-%m-%d')
            entrance_record = EntranceRecord.query.filter(
                db.func.DATE(EntranceRecord.entry_time) == formatted_date
            ).all()
            return render_template('view.html', entrance_record=entrance_record, selected_date=selected_date)
        except ValueError:
            # 處理無效日期格式的情況
            error_message = "請提供有效的日期格式（YYYY-MM-DD）"
            return render_template('view.html', error_message=error_message)

    elif search_id:
        # 如果只有工號存在，則執行工號的搜尋
        entrance_record = EntranceRecord.query.filter(
            EntranceRecord.entry_id == search_id
        ).all()
        if entrance_record:
            return render_template('view.html', entrance_record=entrance_record, selected_date=None, selected_id=search_id)
        else:
            # 如果沒有找到相應的工號記錄，返回無效請求
            error_message = "查無此工號"
            return render_template('view.html', error_message=error_message)

    else:
        # 如果沒有提供有效的搜尋條件，返回錯誤消息
        error_message = "請提供有效的搜尋條件"
        return render_template('view.html', error_message=error_message)


@app.route('/check_absentees_by_date', methods=['GET'])
def check_absentees_by_date():
    specified_date = None
    date_str = request.args.get('date')

    if date_str:
        specified_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        specified_date = date.today()

    # 指定日期的未到班
    entrance_record_numbers = [record.entry_id for record in EntranceRecord.query.filter(
        EntranceRecord.entry_time >= specified_date, EntranceRecord.entry_time < specified_date + timedelta(days=1)).all()]

    # 拉出所有工號
    registered_user_numbers = [
        user.number for user in UserRegister.query.all()]

    # 比對未到工號
    absent_user_numbers = list(
        set(registered_user_numbers) - set(entrance_record_numbers))

    # 未到人的所有資訊
    absent_users = UserRegister.query.filter(
        UserRegister.number.in_(absent_user_numbers)).all()

    return render_template('absent.html', absent_users=absent_users, selected_date=specified_date)


@app.route('/view_list', methods=['GET'])
def view_list():
    users = UserRegister.query.all()

    # 渲染模板，并将检索到的图像数据传递给模板
    return render_template('list.html', users=users)

# --------------------------------------------------------------------------------------------#


@app.route('/delete/<number>', methods=['POST'])
def delete_user(number):
    user_to_delete = UserRegister.query.get(number)  # 根據工號查找要刪除的用戶
    if user_to_delete:
        db.session.delete(user_to_delete)  # 從資料庫中刪除用戶記錄
        db.session.commit()
    return redirect(url_for('view_list'))


@app.route('/showphoto/<number>', methods=['POST'])
def showphoto(number):
    user_photo = UserRegister.query.get(number)  # 根據工號查找要刪除的用戶
    if user_photo:
        image_data = user_photo.captured_image
        # image_data = user_photo.captured_image
        image_pil = Image.open(io.BytesIO(image_data))
        # 顯示圖片
        image_pil.show()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No data!")
        db.session.commit()
    return redirect(url_for('view_list'))


@app.route('/showphoto1/<entry_time>', methods=['POST'])
def showphoto1(entry_time):
    user_photo = EntranceRecord.query.get(entry_time)
    if user_photo:
        image_data = user_photo.photo
        # image_data = user_photo.captured_image
        image_pil = Image.open(io.BytesIO(image_data))
        # 顯示圖片
        image_pil.show()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No data!")
        db.session.commit()
    return redirect(url_for('view_users'))


@app.route('/')
def home():
    return render_template('home.html')


peopleName = []  # 儲存姓名list
encodeListKnown = []  # 儲存encode
peopleID = []
dataSave = []
dataSave1 = []
# 手勢辨識


def generate_frames5():
    camera0 = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.5, maxHands=1)
    name = None
    id = None
    while True:
        success, img = camera0.read()
        if not success:
            break

        if name == None:
            point_color = (0, 0, 255)  # BGR

            cv2.circle(img, (320, 240), 180, point_color, 0)

        success, buffer = cv2.imencode('.jpg', img)
        # 将缓存里的流数据转成字节流
        frame = buffer.tobytes()
        # 指定字节流类型image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera0.release()
    cv2.destroyAllWindows()
# ---------------------------入場人臉----------------------------#


def generate_frames():
    dataSave.clear()
    x = random.randrange(0, 6)
    print(x)
    hand_type = ["Right", "Left"]
    y = random.choice(hand_type)
    print(y)
    camera0 = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.5, maxHands=1)
    name = None
    id = None
    while True:
        send_data_to_frontend_numandhand(x, y)
        success, img = camera0.read()
        hands, img_hand = detector.findHands(img)
        if not success:
            break

        if name == None:
            point_color = (0, 0, 255)  # BGR

            cv2.circle(img, (320, 240), 180, point_color, 0)

            # 將image縮小並轉換成RGB
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            # 將臉轉換成encode
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(
                imgS, faceCurFrame)

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
                        if matches[matchIndex] and faceDis[matchIndex] <= 0.5:
                            id, name = get_dectecded_people(matchIndex)
                            print(id)
                            print(name)
                            send_data_to_frontend(id, name)
                            dataSave.append(id)
                            dataSave.append(name)
                            # save_to_database(id, name, entry_time)
                            break
                        else:
                            print("Don't Known Face Detected")

        success, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera0.release()
    cv2.destroyAllWindows()
    return None, None
# ---------------------------------------出場人臉辨識-----------------------------------#


def generate_frames3():
    dataSave1.clear()
    x = random.randrange(0, 6)
    print(x)
    hand_type = ["Right", "Left"]
    y = random.choice(hand_type)
    print(y)
    camera0 = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.5, maxHands=1)
    name = None
    id = None
    while True:
        send_data_to_frontend_numandhand(x, y)
        success, img = camera0.read()
        hands, img_hand = detector.findHands(img)
        if not success:
            break

        if name == None:
            point_color = (0, 0, 255)  # BGR

            cv2.circle(img, (320, 240), 180, point_color, 0)

            # 將image縮小並轉換成RGB
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            # 將臉轉換成encode
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(
                imgS, faceCurFrame)

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
                        if matches[matchIndex] and faceDis[matchIndex] <= 0.5:
                            id, name = get_dectecded_people(matchIndex)

                            print(id)
                            print(name)
                            send_data_to_frontend1(id, name)
                            dataSave1.append(id)
                            dataSave1.append(name)

                            break
                        else:
                            print("Don't Known Face Detected")

        success, buffer = cv2.imencode('.jpg', img)
        # 将缓存里的流数据转成字节流
        frame = buffer.tobytes()
        # 指定字节流类型image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera0.release()
    cv2.destroyAllWindows()
# -----------------------------------------------------------------------------------------#


def get_dectecded_people(matchIndex):
    id = peopleID[matchIndex]
    name = peopleName[matchIndex]
    return (id, name)

# SocketIO 把工號姓名輸出到入場網頁上


def send_data_to_frontend(id, name):
    socketio.emit('update_data', {'id': id, 'name': name})


def send_data_to_frontend_numandhand(x, y):
    socketio.emit('update_data1', {'x': x, 'y': y})

# 刷臉時間存進資料庫當作入場紀錄


def save_to_database(id, name, entry_time, photo):
    with app.app_context():
        new_record = EntranceRecord(
            entry_id=id, entry_name=name, entry_time=entry_time, in_out="入", photo=photo)
        db.session.add(new_record)
        db.session.commit()

# SocketIO 把工號姓名輸出到出場網頁上


def send_data_to_frontend1(id, name):
    socketio.emit('update_data', {'id': id, 'name': name})

# 刷臉時間存進資料庫當作出場紀錄


def save_to_database1(id, name, entry_time, photo):
    with app.app_context():
        new_record = EntranceRecord(
            entry_id=id, entry_name=name, entry_time=entry_time, in_out="出", photo=photo)
        db.session.add(new_record)
        db.session.commit()


# -------------------------入場裝備-----------------------------------------#
def generate_frames1():
    my_dict = {"0.0": 0, "1.0": 0, "2.0": 0, "3.0": 0}
    camera1 = cv2.VideoCapture(0)
    model = YOLO('Equipment.pt')
    while True:
        success, img = camera1.read()
        if not success:
            break
        if (my_dict["0.0"] == 0) | (my_dict["1.0"] == 0) | (my_dict["2.0"] == 0) | (my_dict["3.0"] == 0):
            results = model(img, conf=0.5)
            annotated_frame = results[0].plot()
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
                    # name = result.names
                print(class_ids)
                data_array = np.array(class_ids)
                for value in data_array[0]:
                    # print(value)
                    val = str(value)
                    # print(val)
                    # print(type(val))
                    my_dict[val] = 1

                print(my_dict)
                socketio.emit('detection', my_dict)

            except Exception as e:
                print(f"Error during prediction: {e}")

            success, buffer = cv2.imencode('.jpg', annotated_frame)
            # 將緩衝區中的流數據轉換為字節流

            frame = buffer.tobytes()
            # 指定字節流類型image/jpeg
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            id = dataSave[0]
            name = dataSave[1]
            entry_time = datetime.now()
            photo = cv2.imencode('.jpg', img)[1].tobytes()

            save_to_database(id, name, entry_time, photo)
    camera1.release()
    cv2.destroyAllWindows()


# -------------------------出場裝備-----------------------------------------#
def generate_frames4():
    my_dict = {"0.0": 0, "1.0": 0, "2.0": 0, "3.0": 0}
    camera1 = cv2.VideoCapture(0)
    model = YOLO('Equipment.pt')
    while True:
        success, img = camera1.read()
        if not success:
            break
        if (my_dict["0.0"] == 0) | (my_dict["1.0"] == 0) | (my_dict["2.0"] == 0) | (my_dict["3.0"] == 0):
            results = model(img, conf=0.5)
            annotated_frame = results[0].plot()
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
                    # name = result.names
                print(class_ids)
                data_array = np.array(class_ids)
                for value in data_array[0]:
                    # print(value)
                    val = str(value)
                    # print(val)
                    # print(type(val))
                    my_dict[val] = 1

                print(my_dict)
                socketio.emit('detection', my_dict)

            except Exception as e:
                print(f"Error during prediction: {e}")

            success, buffer = cv2.imencode('.jpg', annotated_frame)
            # 將緩衝區中的流數據轉換為字節流

            frame = buffer.tobytes()
            # 指定字節流類型image/jpeg
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            id = dataSave1[0]
            name = dataSave1[1]
            entry_time = datetime.now()
            photo = cv2.imencode('.jpg', img)[1].tobytes()

            save_to_database1(id, name, entry_time, photo)
    camera1.release()
    cv2.destroyAllWindows()


@app.route('/camera', methods=['GET', 'POST'])
def camera():
    peopleName.clear()
    encodeListKnown.clear()
    peopleID.clear()
    read_data = UserRegister.query.all()

    for user_data in read_data:
        retrieved_data = pickle.loads(user_data.encode_data)
        peopleName.append(user_data.username)
        encodeListKnown.append(retrieved_data)
        peopleID.append(user_data.number)

    return render_template('camera.html', peopleID=peopleID, peopleName=peopleName, encodeListKnown=encodeListKnown)


@app.route('/exit', methods=['GET', 'POST'])
def exit():
    peopleName.clear()
    encodeListKnown.clear()
    peopleID.clear()
    read_data = UserRegister.query.all()

    for user_data in read_data:
        retrieved_data = pickle.loads(user_data.encode_data)
        peopleName.append(user_data.username)
        encodeListKnown.append(retrieved_data)
        peopleID.append(user_data.number)

    return render_template('exit.html', peopleID=peopleID, peopleName=peopleName, encodeListKnown=encodeListKnown)


@socketio.on('detection')
def handle_detection(data):
    # 接收來自前端的物件辨識結果
    print('Received detection result:', data)


@app.route('/camera1')
def camera1():

    return render_template('camera1.html')


@app.route('/exit1')
def exit1():

    return render_template('exit1.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed1')
def video_feed1():
    return Response(generate_frames1(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed2')
def video_feed2():
    return Response(generate_frames3(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed3')
def video_feed3():
    return Response(generate_frames4(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed4')
def video_feed4():
    return Response(generate_frames5(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/success1')
def success1():
    return render_template('success1.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
if __name__ == '__main__':
    app.run(debug=True)
