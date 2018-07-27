#python facecogv5.py "stream name"

import face_recognition
import cv2
import requests
import time
import datetime
import glob
import os
import flask
import sys
import json
url = 'http://ec2-50-112-136-119.us-west-2.compute.amazonaws.com:9090/signUpJson'
start = time.time()
#Receive the users as a list in JSON format from the DB
nameArray = []
namePicArray = []
priorityNameArray = []
priorityPicArray = []
priority = sys.argv[1]
allNames = []
response = requests.get('http://ec2-50-112-136-119.us-west-2.compute.amazonaws.com:9090/userList')
if(response.ok):
    jData = response.json()
    OGLength = len(jData)
    for row in jData:
        if(row['user_priority'] == priority):
            priorityNameArray.append(row['user_name'])
            priorityPicArray.append(row['user_pic_name'])
        else:
            nameArray.append(row['user_name'])
            namePicArray.append(row['user_pic_name'])
totalLength = (len(namePicArray) + len(priorityPicArray))
allNames.extend(priorityNameArray)
allNames.extend(nameArray)
    
end = time.time()
elapsed = end - start
print("Time it took to receive users", elapsed)

start = time.time()
#Initialize video feed
#IP Camera
#video_capture = cv2.VideoCapture("rtsp://foscam:venki1@66.25.14.17:8505/videoMain")
#Webcam
video_capture = cv2.VideoCapture(-1)
#Video
#video_capture = cv2.VideoCapture("/home/local/facecog/videos/group_vid_07.mp4")
end = time.time()
elapsed = end - start
print("Time it took to initialize video feed", elapsed)
time.sleep(2)


start = time.time()
#Create face encodings for all of the names and filenames in the list
#Takes the longest amount of time in the file
encodingArr = []
for filename in priorityPicArray:
    currentImage = face_recognition.load_image_file(filename)
    faceEncoding = face_recognition.face_encodings(currentImage)[0]
    encodingArr.append(faceEncoding)

for filename in namePicArray:
    currentImage = face_recognition.load_image_file(filename)
    faceEncoding = face_recognition.face_encodings(currentImage)[0]
    encodingArr.append(faceEncoding)

end = time.time()
elapsed = end - start
print("Time it took to create face encodings", elapsed)

# Initialize some variables
nameArr = []
face_locations = []
face_encodings = []
face_names = []
firstFrame = None
process_this_frame = True

n=0
p=0

while True:
    start = time.time()
    # Grab a single frame of video
    ret, frame = video_capture.read()
    text = "Unoccupied"

    #cv2.imshow('frame', frame)

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    small_frame = cv2.resize(frame, None,fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
    

    #Check every 200 counts whether there is any new added users
    if p==200:
        p=0
        response = requests.get('http://ec2-50-112-136-119.us-west-2.compute.amazonaws.com:9090/userList')
        if(response.ok):
            jData = response.json()
            newLength = len(jData)
            #If there is a newly added user, add them to the list and create face encoding for them
            if (newLength > OGLength):
                print("Updating Users")
                for row in jData[OGLength:]:
                    if(row['user_priority'] == priority):
                        priorityNameArray.append(row['user_name'])
                        priorityPicArray.append(row['user_pic_name'])
                    else:
                        nameArray.append(row['user_name'])
                        namePicArray.append(row['user_pic_name'])
                for filename in priorityPicArray:
                    currentImage = face_recognition.load_image_file(filename)
                    faceEncoding = face_recognition.face_encodings(currentImage)[0]
                    encodingArr.append(faceEncoding)
                for filename in namePicArray:
                    currentImage = face_recognition.load_image_file(filename)
                    faceEncoding = face_recognition.face_encodings(currentImage)[0]
                    encodingArr.append(faceEncoding)
                OGLength = newLength

   # Only process every other frame of video to save time
    if n==15:
        n=0
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray=cv2.GaussianBlur(gray, (21, 21), 0)
        
        if firstFrame is None:
            firstFrame = gray
            continue
        
        frameChange = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameChange, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _ ,cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for c in cnts:
        
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            text = "Occupied"
            end = time.time()
            elapsed = end - start
            print("Time it took to set up motion detection", elapsed)
            start = time.time()
            if text == "Occupied":
                print(text)
                face_locations = face_recognition.face_locations(frame)
                end = time.time()
                    
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                print(elapsed)
                    
                face_names = []
                for face_encoding in face_encodings:
                    current_time = time.localtime()
                    match = face_recognition.compare_faces(encodingArr, face_encoding, tolerance = 0.5)
                    name = "Unknown"

                    for i in range(totalLength):
                        if match[i]:
                            name = allNames[i]
                            break
                                
                    end = time.time()
                    elapsed = end - start
                    print("Time it took to locate and compare faces", elapsed)
                        
                    print(name)
                    face_names.append(name)
                        
                    if name in allNames:
                        data = {'inputName' : name,
                            'inputLocation' : priority,
                            'inputTime' : time.strftime('%a, %d %b %Y %H: %M: %S CST', current_time)}
                                
                    print(time.strftime('%a, %d %b %Y %H: %M: %S CST', current_time))
                    
                    headers = {'Content-type': 'application/json'}
                    response = requests.post(url, json = data, headers = headers)
                        
                    print('sent response')
                break


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        #top *= 4
        #right *= 4
        #bottom *= 4
        #left *= 4
        font = cv2.FONT_HERSHEY_DUPLEX
        #print(left)
        #print(top)
        #print(right)
        #print(bottom)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    n+=1 
    p+=1
    print("p", p)
    print("n", n)
    
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
