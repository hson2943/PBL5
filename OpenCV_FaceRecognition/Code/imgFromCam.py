from tensorflow.keras.models import model_from_json
from email.message import EmailMessage
from google.cloud import storage
from firebase import firebase
import socket
import datetime
import face_recognition as fr
import numpy as np
import os
import cv2
import smtplib
import imghdr
import urllib.request

EMAIL_ADDRESS = 'huunguyen4869@gmail.com'
EMAIL_PASSWORD = 'rvvvglljbbtyhyih'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('192.168.43.222', 65321))
s.listen(0)

imgScale = 0.25
timeDic = {}
#  =================setup firebase=============================
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="pbl5-camera-327b0-firebase-adminsdk-m00dj-7a33340ba9.json"
db_url='https://pbl5-camera-327b0-default-rtdb.asia-southeast1.firebasedatabase.app/'
firebase = firebase.FirebaseApplication(db_url,None)
client = storage.Client()
bucket = client.get_bucket('pbl5-camera-327b0.appspot.com')
imageBlob = bucket.blob("/")
# =================real/fake model=============================
root_dir = os.getcwd()
# Load Face Detection Model
face_cascade = cv2.CascadeClassifier(
    "models/haarcascade_frontalface_default.xml")
# Load Anti-Spoofing Model graph
json_file = open('antispoofing_models/antispoofing_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# load antispoofing model weights
model.load_weights('antispoofing_models/antispoofing_model.h5')
print("Model loaded from disk")
# =================face recognite==============================
pathToRec = "imagesRecognite"
imagesRec = []
namesRec = []
namesList = os.listdir(pathToRec)
# đọc từng folder của những người có trong danh sách nhận diện
for name in namesList:
    timeDic[name] = datetime.datetime.now()
    imagePath = f'{pathToRec}/{name}'
    imagesList = os.listdir(imagePath)
    # đọc từng ảnh trong từng folder, thêm ảnh và tên vào danh sách nhận diện
    for image in imagesList:
        currentImage = cv2.imread(f'{imagePath}/{image}')
        imagesRec.append(currentImage)
        namesRec.append(name)
timeDic["Unknown"] = datetime.datetime.now()
# hàm mã hoá hình ảnh


def encodingImages(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = fr.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = encodingImages(imagesRec)
print("Encoding complete")

# ==================nhận hình ảnh và xử lý========================
cap = cv2.VideoCapture(0)
url = 'http://192.168.43.116/cam-photo.jpg'
unknownTime = datetime.datetime.now()
unknownFlag = False
while True:
    fakeFlag = False
    # lấy image từ ESP32
    # success, img = cap.read()
    try:
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        img = cv2.imdecode(imgnp,-1)
        #img = cv2.addWeighted(img, 1, np.zeros(img.shape, img.dtype), 0, 100)
    except Exception as error:
        print(error)
        continue

    # cho ảnh nhỏ xuống và chỉnh lại định dạng màu RGB
    imgSmall = cv2.resize(img, (0, 0), None, imgScale, imgScale)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    # lấy vị trí tất cả khuôn mặt có trong frame hiện tại
    facesInCurrentFrame = fr.face_locations(imgSmall)

    # kiểm tra fake/real
    try:
        for y1, x2, y2, x1 in facesInCurrentFrame:
            y1, x2, y2, x1 = int(y1/imgScale), int(x2/imgScale), int(y2/imgScale), int(x1/imgScale)
            face = img[y1-5:y2+5, x1-5:x2+5]
            resized_face = cv2.resize(face, (160, 160))
            resized_face = resized_face.astype("float") / 255.0
            resized_face = np.expand_dims(resized_face, axis=0)
            preds = model.predict(resized_face)[0]
            print(preds)
            if preds > 0.5:
                cv2.putText(img, "Fake image detected!", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                fakeFlag = True
    except Exception as error:
        print("1")
        continue

    # so sánh các khuôn mặt hiện tại với List khuôn mặt đã biết
    if fakeFlag == False:
        # encode các khuôn mặt có trong frame hiện tại
        encodesCurrentFrame = fr.face_encodings(imgSmall, facesInCurrentFrame)
        for encode, face in zip(encodesCurrentFrame, facesInCurrentFrame):
            matches = fr.compare_faces(encodeListKnown, encode)
            faceDis = fr.face_distance(encodeListKnown, encode)
            # index của khuôn mặt khớp nhất(có face distance nhỏ nhất)
            matchIndex = np.argmin(faceDis)
            # lấy tên và vị trí khuôn mặt
            name = namesRec[matchIndex]
            y1, x2, y2, x1 = face
            y1, x2, y2, x1 = int(y1/imgScale), int(x2/imgScale), int(y2/imgScale), int(x1/imgScale)
            # xét có khớp không sau đó vẽ khung màu và tên
            print(faceDis[matchIndex])
            if faceDis[matchIndex] < 0.55:
                if unknownFlag == True:
                    unknownFlag = False
                    print("sending stop")
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            # gửi tín hiệu về client esp8266 để mở cửa
            # Nghe client
                client, addr = s.accept()
                client.send(b'1')
                client.close()
            else:
                name = "Unknown"
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                if unknownFlag == False:
                    unknownFlag = True
                    unknownTime = datetime.datetime.now()
                    now = datetime.datetime.now()
                    imgTimeUnknown = now.strftime("%d-%m-%y_%Hh%Mm%Ss")
                    imgPathUnknown = "./imagesSaved/" + imgTimeUnknown +"_"+ name + ".jpg"
                    cv2.imwrite(imgPathUnknown, img)
                    print("sending start")
                
            #lưu hình ảnh và gửi lên firebase
            now = datetime.datetime.now()
            pre = timeDic.get(name)
            if (now - pre).total_seconds() > 30:
                timeDic[name] = now
                imgTime = now.strftime("%d-%m-%y_%Hh%Mm%Ss")
                imgPath = "./imagesSaved/" + imgTime +"_"+ name + ".jpg"
                cv2.imwrite(imgPath, img)   
                imageBlob = bucket.blob(imgTime +"_"+ name + ".jpg")
                imageBlob.upload_from_filename(imgPath)
    #gửi cảnh báo qua gmail
    now = datetime.datetime.now()
    if unknownFlag == True and (now - unknownTime).total_seconds() > 10:
        # gửi tín hiệu về client esp8266 để rung chuông khi có người lạ
        # Nghe client
        # client, addr = s.accept()
        # client.send(b'2')
        # client.close()

        with open(imgPathUnknown, 'rb') as f:
            file_data = f.read()
            file_type = imghdr.what(f.name)
            file_name = f.name
            html = """\
                <!DOCTYPE html><html><body>
                <div style="width: 500px; height: 500px;background-color: orange; " class="unknow">
                <img style='margin-top: 90px; margin-right: 90px; margin-left: 90px;' src='https://thumbs.dreamstime.com/b/incognito-unknown-person-silhouette-man-incognito-unknown-person-silhouette-man-white-background-110196097.jpg' alt="" title="" width="300" height="300">
                <h1 style="margin-top: 10px;margin-left: 50px ; font-family: Arial, Helvetica, sans-serif;">Thời gian :""" + imgTimeUnknown + """</h1>
                </div></body></html>"""
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Có người lạ lúc ' + imgTimeUnknown
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = 'huunguyen4869@gmail.com'
                msg.add_alternative(html, subtype='html')
                msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)
            except:
                print("error sending email")
                continue     
        unknownFlag = False
        print("email sent")   

    cv2.imshow('ESP32', img)
    cv2.waitKey(1)
