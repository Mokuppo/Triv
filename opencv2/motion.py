import cv2
import time 
import os
import HandDetector as hd

width, height = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)
#hand detector


#previous Frame
pTime = 0

while True:

    ret, img = cap.read()
    

    
    #fpsDisplay
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,str(int(fps)),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

    cv2.imshow("Frame", img)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()