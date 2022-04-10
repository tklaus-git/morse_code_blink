from time import perf_counter
import numpy as np
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import mediapipe
import time
import keyboard
from typing import List

#           Binary Tree representation
letters = ['','E','T','I','A','N','M','S','U','R','W','D','K','G','O','H','V','F','','L','','P','J','B','X','C','Y','Z','Q','','']


# dots is a list of 0's and 1's; 0: short blink, 1: long blink
def choose_letter(dots: List[int]) -> str:
    if len(dots)>4:
        return 'TOO BIG'
    trace = 1
    for dot in dots:
        if dot == 0:
            trace = 2*trace
        else:
            trace = (2*trace)+1
    print(trace-1)
        
    return letters[int(trace-1)]


video = cv2.VideoCapture(1) # Opening my front camera 
if (video.isOpened() == False):
  print("Error opening video stream or file")

detector = FaceMeshDetector(maxFaces=1) # Find face mesh, keeps track of points in face

plotY= LivePlot(640, 360, [20, 50])


idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243] # Specific points I am keeping track of 


dList = [] # Going to keep track of distances between top and bottom of eye
horList = [] # Going to keep track of distance between left and right side of eye
r_list = []

counter = 0 # Keeps track of what blink we are on
blinking = 0 # are we blinking
timer = time.perf_counter()
notBlinking = 0

avg_d = [] # Will keep track of the average ratio between distances within eye

letter = []
word = ''
morse = ''
start = False


while not keyboard.is_pressed('q'):
    success, img = video.read()
    img, faces = detector.findFaceMesh(img, draw = False) # changed

    if keyboard.is_pressed('s'):
        start = True   

    

    if faces: # if face is detected
        # Setting up variables related to positions
        face = faces[0]
        leftUp = face[159]
        leftDown = face[23]

        leftLeft = face[130]
        leftRight = face[243]

        rightDown = face[374]
        rightUp = face[386]

        rightRight = face[359]
        rightLeft = face[398]


        # Getting distance
        distanceVert, _ = detector.findDistance(leftUp, leftDown)
        distanceHor, _ = detector.findDistance(leftLeft, leftRight)
        distanceVertR, _ = detector.findDistance(rightUp, rightDown)
        distanceHorR, _ = detector.findDistance(rightLeft, rightRight)

        # if (distanceVert >= 12 and distanceHor >= 30):


        # print('\nVert: '+str(distanceVert))
        # print('Hor: '+str(distanceHor))
        
    

        for id in idList:
            cv2.circle(img, face[id], 5, (255, 0, 255)) # just here to color eye
        
        # Getting the 4 points we will keep track of, the 4 corners of the eyes
        
        horList.append((distanceHor+distanceHorR)/2)
        if len(horList) > 1:
            horList.pop(0)
        else:
            blinking = 0
        distanceHor = sum(horList)/len(horList) # Average horizontal distance past 100 frames

        dList.append((distanceVert+distanceVertR)/2)
        if len(dList) > 2:
            dList.pop(0)
        distanceVert = sum(dList)/len(dList)

        ratio = (distanceVert/distanceHor)*100
        r_list.append(ratio)
        if len(r_list)>2:
            r_list.pop(0)
        ratio = sum(r_list)/len(r_list)
        
        # Blinking detection:

        avg_d.append(ratio)
        if len(avg_d) > 200:
            avg_d.pop(0)
        avg_ratio =   sum(avg_d)/len(avg_d)
        print(avg_ratio-ratio)


        if start:
            if avg_ratio-ratio > 3: 
                if blinking == 0:
                    startTime = time.perf_counter()
                    blinking = 1
                    counter+=1  
            else: # Wasn't blinking
                if blinking == 1: # end of blink
                    howLong = time.perf_counter() - startTime
                    notBlinking = time.perf_counter()
                    if (howLong<.28): # dot
                        letter.append(0)
                        morse+= '.'
                    elif(howLong < 1):
                        letter.append(1)
                        morse+= '_'                    
                if time.perf_counter() - notBlinking >= 1:
                    # LETTER IS COMPLETE:
                    if len(letter) < 5:
                        word += choose_letter(letter)
                    letter = []
                    morse = ''


                # IF IT IS A DASH OR A DOT


                blinking = 0 # not blinking
            # print(counter)
            
        cvzone.putTextRect(img, word+morse, (100,100))
        # cvzone.putTextRect(img, morse, (100,200))

        # Plotting
        
        imgPlot = plotY.update(ratio)


        cv2.line(img, leftUp, leftDown, (0, 200, 0), 1)
        cv2.line(img, leftUp, leftDown, (0, 200, 0), 1)
        cv2.imshow('ImagePlot', imgPlot)
        # print(round(time.perf_counter(),2))
        
        if keyboard.is_pressed('r'):
            letter = []
            morse = ''
            word = ''



    cv2.imshow('Image', img)
    cv2.waitKey(1)
