#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install dlib
#!pip install cmake
#!pip install face_recognition
#!pip install pyserial


# import the necessary libraries 



import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition
import serial
import time

#Intialize serial communication with arduino
ser = serial.Serial('COM12', 9600)
time.sleep(2)
ser.close()
#Initialize serial communication wiith sim900 gsm module
sim900 = serial.Serial('COM12', 9600)
time.sleep(2)
sim900.close()
#path to images folder 
path = "C:/Users/ADMIN/Downloads/cleared"
#url =  "arduino serial monitor"


#Create file attendance.csv, removes one if already exists
if 'Attendace.csv' in os.listdir(os.path.join(os.getcwd(),path)):
    print("there iss..")
    os.remove("Attendance.csv")
else:
    df = pd.DataFrame(list())
    df.to_csv("Attendance.csv")


images = []
studentNames = []
clearedStudents = os.listdir(path)
print(clearedStudents)


#Get student names
for student in clearedStudents:
    curImg = cv2.imread(f'{path}/{student}')
    images.append(curImg)
    studentNames.append(os.path.splitext(student)[0])
print(studentNames)


#Find the encodings of the images 
def findEndcodings(images):
    encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodings.append(encode)
    return encodings


#Opens the attendance.csv file, appends to it with name and time of exam entry
def authExam(name):
    with open("Attendance.csv", 'a+') as f:
        for name, timestamp in authorizedStudents.items():
            f.writelines(f'\n{name}, {timestamp}')


encodeListKnown = findEndcodings(images)
print('Encoding Complete')


#Initialize webcam
cap = cv2.VideoCapture(0)


authorizedStudents = {}


def blinkLED(color, duration):
    ser.write(color.encode()) # send color to Arduino to control LED
    time.sleep(duration)
    ser.write('OFF'.encode()) #Turn off LED


def sendSMS(sim900, phoneNumber, message):

    sim900.open()
    sim900.write(b'AT+CMGF=1\r\n')
    time.sleep(1)

    sim900.write(f'AT+CMGS="{phoneNumber}"\r\n'.encode('utf-8'))
    time.sleep(1)

    sim900.write(message.encode('utf-8'))
    time.sleep(1)

    sim900.write(bytes([26]))
    time.sleep(1)
    sim900.close()

#Match face on camera with face in folder, start the webcam, to terminate program press q
#Increase accuracy by adding toleracne 
while True:
    ret, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame) 

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.4)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        
        if np.any(faceDis > 0.6) or not any(matches):
            print("You do not appear in the exam list")
            #blinkLED("RED", 0.5) #Blink red LED for .5 seconds
            sendSMS(sim900, "+254703678264", "Unauthorized face detected!")
            
        else:
            name = studentNames[matchIndex].upper()
            if name in authorizedStudents:
                print(f'{name} has already checked in.')
                sendSMS(sim900, "+254703678264",f'{name} has already checked in')
                

                #blinkLED("RED", 0.5)# BLink red LED for 0.5 seconds
            else:
                canSit = f'{name} appears on the exam list'
                authorizedStudents[name] = datetime.now().strftime('%H:%M:%S')
                #send sms notification
                sendSMS(sim900, "+254703678264", canSit)
                
                #blinkLED("GREEN", 0.5) #BLink green LED for .5 seconds
        

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        

#Close the webcam
cv2.destroyAllWindows()
cv2.imread




