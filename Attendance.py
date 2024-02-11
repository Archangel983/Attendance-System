import face_recognition
import cv2
import time
import mysql.connector as mysql 
from datetime import datetime

def search(rfid = 0):
    if rfid != 0:
        robject=mysql.connect(host = "localhost",user="root", password = "Your_DB_Password",database="Your_DB_Name")
        mycursor=robject.cursor()
        query="select * from MDB where rfid=%s"
        value=(rfid,)
        mycursor.execute(query,value)
        result = mycursor.fetchone()
        person=result[2]
        return person
    else:
        print("Scan Again")
    

#Textfile
f = open("textfile.txt","r")
rfid=f.read()
res = search(rfid)
print(res)
def load_known_faces():
    # Load images with faces
    images = [
        "Joe Biden.jpg"
        ]
    known_face_encodings = []
    known_face_names = []

    for image_path in images:
        image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(image_path.split(".")[0])

    return known_face_encodings, known_face_names

def recognize_faces(frame, known_face_encodings, known_face_names):
    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Update face_detected variable based on the presence of faces
    global face_detected
    face_detected = len(face_locations) > 0

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        global name
        name = "Unknown"

        # If a match is found, use the name of the known face
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Draw a rectangle around the face and display the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    return frame

def check_continuous_presence():
    global start_time
    global face_detected
    current_time = time.time()

    # If a face is detected, update start_time
    if face_detected and name in res:
        if start_time is None:
            start_time = current_time
    else:
        # If no face is detected, reset start_time
        start_time = None

    # If face is continuously detected for 2 seconds, print attendance done
    if start_time is not None and name in res and current_time - start_time >= 2:
        def markattendance(name):
            with open ('attendance.txt','r+') as f:
                myDataList=f.readlines()
                nameList=[]
                for line in myDataList:
                    entry=line.split(',')
                    nameList.append(entry[0])
                if name not in nameList:
                    now=datetime.now()
                    dtString=now.strftime('%H:%M:%S')
                    f.writelines(f'\n{name},{dtString}')
        markattendance(name)
        
# Open the webcam
video_capture = cv2.VideoCapture(0)

# Load known faces
known_face_encodings, known_face_names = load_known_faces()

# Initialize variables for continuous face presence check
face_detected = False
start_time = None

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Recognize faces and update the frame
    frame = recognize_faces(frame, known_face_encodings, known_face_names)

    # Check continuous face presence
    check_continuous_presence()

    # Display the resulting frame
    cv2.imshow('Video', frame)
    
    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
video_capture.release()
cv2.destroyAllWindows()
