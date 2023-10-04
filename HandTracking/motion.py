import cv2
import time 
import os
import HandDetector as hd
import Xlib.display
import numpy as np
import uinput

#mouse input keys
keys = [
    uinput.BTN_LEFT,
    uinput.BTN_MIDDLE,
    uinput.BTN_RIGHT,
    uinput.REL_X,
    uinput.REL_Y,
    uinput.REL_WHEEL,
    uinput.REL_HWHEEL,
]

""" #starting Device
device = uinput.Device(keys)
time.sleep(1)

def move_mouse(x : int, y : int):
    device.emit(uinput.REL_X, -25000)
    device.emit(uinput.REL_Y, -25000)
    device.emit(uinput.REL_X, x//2)
    device.emit(uinput.REL_Y, y//2) 
    print(f"Post: {x//2} x {y//2}")
    
def click(x : int, y : int, btn : int = 0, count : int = 1):
    # Check each argument

    if btn > 2 or btn < 0 or type(btn) != int:
        raise ValueError('btn must be 0, 1 or 2')
    if count > 3 or count < 1 or type(count) != int:
        raise ValueError('count must be 1, 2 or 3')
    
    move_mouse(x, y)
    
    # Click the desired button
    if btn == 0:
        for i in range(count):
            device.emit(uinput.BTN_LEFT, 1)
            device.emit(uinput.BTN_LEFT, 0)
    elif btn == 1:
        for i in range(count):
            time.sleep(0.3)
            device.emit(uinput.BTN_MIDDLE, 1)
            device.emit(uinput.BTN_MIDDLE, 0)
    elif btn == 2:
        for i in range(count):
            time.sleep(0.3)
            device.emit(uinput.BTN_RIGHT, 1)
            device.emit(uinput.BTN_RIGHT, 0)
 """

def get_screen_resolution():
    display = Xlib.display.Display()
    screen = display.screen()
    width = screen.width_in_pixels
    height = screen.height_in_pixels
    return width, height

def main():
    #mouse input keys
    keys = [
        uinput.BTN_LEFT,
        uinput.BTN_MIDDLE,
        uinput.BTN_RIGHT,
        uinput.REL_X,
        uinput.REL_Y,
        uinput.REL_WHEEL,
        uinput.REL_HWHEEL,
    ]

    with uinput.Device(keys) as device:
        screen_width, screen_height = get_screen_resolution()
        print(f"Screen Resolution: {screen_width}x{screen_height}")

        reductionFrame = 100
        width, height = 640, 480

        cap = cv2.VideoCapture(0)
        cap.set(3,width)
        cap.set(4,height)
        #hand detector
        detector = hd.handDetector(maxHands=1)

        #close Hand Variable
        five_finger_timer = 0

        #previous Frame
        pTime = 0
        mouseClicking = False

        while True:
            #image and Hand Detection
            ret, img = cap.read()
            img = detector.findHand(img,draw=False)
            lmList, bbox = detector.findPosition(img)

            if five_finger_timer == 80:
                break

            #tip and thumb
            if len(lmList)!=0:
                x1,y1 = lmList[8][1:]
                x2,y2 = lmList[4][1:]
                #print(f"Tip: [{x1},{x2}] Thumb: [{x2},{y2}]")

                #fingers Up
                fingers = detector.fingersUp()

                if all(item == 1 for item in fingers):
                    five_finger_timer += 1
                    #print(five_finger_timer)
                else:
                    five_finger_timer = 0
                
                #tip Up, move Mode
                if fingers[1] == 1 and fingers[0] == 0:
                    cv2.rectangle(img,(reductionFrame,reductionFrame),(width-reductionFrame,height-reductionFrame),(255,255,255), 2)
                    x3 = np.interp(x1,(reductionFrame,width-reductionFrame),(0,screen_width))
                    y3 = np.interp(y1,(reductionFrame,height-reductionFrame),(0,screen_height))

                    #move_mouse(int(x3),int(y3))
                    #emit movements into uinput mouse
                    device.emit(uinput.REL_X, -25000)
                    device.emit(uinput.REL_Y, -25000)
                    device.emit(uinput.REL_X, (screen_width - int(x3))//2, syn=False)
                    device.emit(uinput.REL_Y, int(y3)//2) 

                    time.sleep(0.05)

                if fingers[1] == 1 and fingers[0] == 1:
                    cv2.rectangle(img,(reductionFrame,reductionFrame),(width-reductionFrame,height-reductionFrame),(255,255,255), 2)
                    lenght, img, linePoint = detector.findDistance(8,4,img,r=5)
                    if lenght>110 and not mouseClicking:
                        cv2.rectangle(img,(linePoint[4]-10,linePoint[5]-10),(linePoint[4]+10,linePoint[5]+10),(255,255,255),2)
                        #device.emit_click(uinput.BTN_LEFT, 1)
                        device.emit_click((0x01, 0x110), 1)
                        mouseClicking = True
                    else:
                        mouseClicking = False                    
                    device.emit(uinput.BTN_LEFT, 0)    

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

if __name__ == "__main__":
    main()