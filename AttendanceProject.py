import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# import images automatically from BaseImagesOfStudents folder
path = 'BaseImagesOfStudents'
imagesOfStudents = []
names_of_students = []
students_present = []

listWithJPGExtension = os.listdir(path)

# go through BaseImagesOfStudents folder and grab names
for fileName in listWithJPGExtension:
    currImg = cv2.imread(f'{path}/{fileName}')
    imagesOfStudents.append(currImg)
    # remove .jpg from name
    names_of_students.append(os.path.splitext(fileName)[0])

print(f'List of entire class: {names_of_students}')


# find encodings for each image and put in encodeList
def findEncodings(images):
    listOfEncodings = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(image)[0]
        listOfEncodings.append(encoding)
    return listOfEncodings


def markAttendance(studentName):
    # open csv with rw permissions
    with open('Attendance.csv', 'r+') as f:
        myCSVList = f.readlines()

        # iterate through each line and split between commas
        for line in myCSVList:
            entry = line.split(',')
            # since it splits name and time, we want name list to only have first entry (name)
            students_present.append(entry[0])

        # check if current name is present or not
        # if not present, then add current time into list
        if studentName not in students_present:
            now = datetime.now()
            dateString = now.strftime('%b %d at %I:%M %p')
            f.writelines(f'\n{studentName},{dateString}')


known_encodings = findEncodings(imagesOfStudents)
print('Finished Encoding...')

# initialize webcam
cap = cv2.VideoCapture(0)  # for webcam

while True:
    success, img = cap.read()  # for webcam
    # img = cv2.imread('ScreenshotOfZoomClassForAttendance/zoomCelebrity.jpg')  # for screenshot

    img_to_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # find face location and send each location to encoding
    faces_at_current_frame = face_recognition.face_locations(img_to_RGB)
    encodings_at_current_frame = face_recognition.face_encodings(img_to_RGB, faces_at_current_frame)

    # iterate through all faces found in current frame
    # compare all these faces with all the encodings in known_encodings
    # grabs one faceLoc in facesCurrFrame and grab encoding from encodeCurrFrame
    for face_encoding, face_location in zip(encodings_at_current_frame, faces_at_current_frame):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_dist = face_recognition.face_distance(known_encodings, face_encoding)

        # find index at lowest encoding value
        match_index = np.argmin(face_dist)

        # now we know who the person is.
        # display name and display rectangle
        if matches[match_index]:
            name = names_of_students[match_index]

            top, right, bottom, left = face_location

            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            markAttendance(name)

        cv2.imshow("Results", img)
        cv2.waitKey(1)
