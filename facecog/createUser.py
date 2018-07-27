#use best lighting possible, have camera centered on face

import face_recognition
import cv2
import requests
import time

#cam = cv2.VideoCapture("rtsp://foscam:venki1@66.25.14.17:8505/videoMain")
cam = cv2.VideoCapture(-1)
detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
url = 'http://ec2-50-112-136-119.us-west-2.compute.amazonaws.com:9090/createUser'

sampleNum=0
userID = input('Enter userID: ')
name = input('Enter name: ')
priority = input("Enter user's priority: ")
        
while(True):
    ret, img = cam.read()
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(img, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        
        #incrementing sample number 
        sampleNum=sampleNum+1
        #saving the captured face in the dataset folder
        #picName = "dataSet/"+str(userID)+str(sampleNum)+".jpg"
        picName = str(userID)+str(sampleNum)+".jpg"
        
        cv2.imwrite(picName, img[y:y+h,x:x+w])
        #cv2.imwrite(picName, img)

#        currentImage = face_recognition.load_image_file(picName)        
#        faceEncoding = face_recognition.face_encodings(currentImage)[0]
#        print(faceEncoding)
        
        data = {'inputID' : userID, 
          'inputName' : name,
          'inputPicName' : picName,
          'inputPriority' : priority}
#          'inputEncoding' : faceEncoding} 
        
        response = requests.post(url, data = data)
        print('added pic to dataSet and sqlDB')
        
#        cv2.imshow('frame',img)
    #wait for 100 miliseconds 
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    # break if the sample number is morethan 5
    elif sampleNum>3:
        break
cam.release()
cv2.destroyAllWindows()
