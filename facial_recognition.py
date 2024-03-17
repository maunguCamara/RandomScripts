import pandas as pd
import cv2
import urllib.request
import numpy
import os
from datetime import datetime
import face_recogniton

path = "path/to/images/"
url =  "arduino serial monitor"

#Create Cleared.csv, removes one if already exists
if 'Cleared.csv' in os.listdir(os.path.join(os.getcwd(),'clearedStudents')):
    print("there iss..")
    os.remove("Cleared.csv")
else:
    df = pd.DataFrame(list())
    df.to_csv("Attendance.csv")

images = []
studentNames = []
clearedStudents = os.listdir(pathtodirectoryofclearedstudentnames)
print(clearedStudents)

for student in clearedStudents:
    curImg = cv2.imread(f'{path}/{student}')
    images.append(curImg)
    studentNames.append(os.path.splitext(student)[0])
print(studentNames)

def findEndcodings(images):
    encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recogniton.face_encodings(img)[0]
        encodings.append(encode)
    return encodings

def authExam(name):
    with open("Cleared.csv", 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')
encodeListKnown = findEndcodings(images)
print('Encoding Complete')

while True:
    imgResp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recogniton.face_locations(imgS)
    encodesCurFrame = face_recogniton.face_encodings(imgS, facesCurFrame) 

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recogniton.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recogniton.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = studentNames[matchIndex].upper()
            print(f'{name} appears on the exam list')
            authExam(name)
            break
        else:
            print(f'{name} is not on the exam list')
        

    cv2.imshow('img', imgS).imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
cv2.imread