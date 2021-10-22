import numpy as np
import cv2
import time
from directkeys import PressKey, ReleaseKey, W, A, S, D
from grabscreen import grab_screen
from getkeys import getkeys
from vjoy import vJoy, setJoy

vj = vJoy()

XYRANGE = 16393.0
ZRANGE = 327860.0

colorthreshold = 75
amountthreshold = 200
resolution = 8

screenrange = 10

paused = False
targetX = 512.0

lastErrorX = None

def process_img(game_screen):
    global paused
    global lastErrorX
    
    xPos = []
    yPos = []

    processed_img = cv2.cvtColor(game_screen, cv2.COLOR_BGR2GRAY)
    nbpixels = 0

    for y in range(int(len(processed_img)/resolution)):
        for x in range(int(len(processed_img[y])/resolution)):
            if processed_img[y*resolution][x*resolution] < colorthreshold:
                nbpixels += 1
                xPos.append(x*resolution)
                yPos.append(y*resolution)

    if nbpixels != 0:
        meanx = np.mean(xPos)
        meany = np.mean(yPos)
        varx = np.var(xPos)
        vary = np.var(yPos)
    else:
        meanx = 500
        meany = 40


    errorX = targetX - meanx

    if lastErrorX is None:
        lastErrorX = errorX

    derivX = errorX - lastErrorX

    if not paused:

        controllerinput(nbpixels ,amountthreshold, errorX, derivX)

    lastErrorX = errorX

    return processed_img



def controllerinput(nbpixels, amountthreshold, errorX, derivX):

    kd = 15  #15
    kp = 1.3 # 1.3
    xPos = float(errorX)/160.0*kp + derivX/160*kd     #160
    #print(float(errorX)/160.0*kp,' + ',derivX/160*kd)
    yPos = 0
    scale = XYRANGE
    setJoy(xPos, yPos, scale)



def play():
    global paused
    last_time = time.time()
    PressKey(W)
    while(True):

        game_screen = grab_screen([0, 330-screenrange, 1024, 390+screenrange])
        used_image = process_img(game_screen)
        #print('{} fps'.format(round(1/(time.time()-last_time),1)))
        last_time = time.time()
        cv2.imshow('used_image',cv2.cvtColor(used_image, cv2.COLOR_BGR2RGB))
        gray_used_image = cv2.inRange(used_image, 0, colorthreshold)
        cv2.imshow('gray_used_image', gray_used_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            reset_joy()
            ReleaseKey(W)
            cv2.destroyAllWindows()
            break
        
        keys = getkeys()
        if 'P' in keys:
            if paused:
                print('unpaused!')
                paused = False
                time.sleep(0.5)

            else:
                print('Pausing!')
                paused = True
                time.sleep(0.5)
                ReleaseKey(W)

def reset_joy():
    setJoy(0, 0, 1000)
    time.sleep(1)
    setJoy(0, 0, 1000)
    time.sleep(0.5)
    vj.close()


if __name__ == '__main__':
    vj.open()
    time.sleep(1)
    play()

