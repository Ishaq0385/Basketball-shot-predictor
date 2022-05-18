import cv2
import cvzone
from cvzone.ColorModule import ColorFinder
import numpy as np
import math
import ctypes
import serial
import time

#ref_image = cv2.imread('b2.png')
#cv2.imshow("ref_image", ref_image)

cap = cv2.VideoCapture('Videos/vid (3).mp4')
#accessing ip cameras
#cap = cv2.VideoCapture('rtsp://user:vision@botix@192.168.1.64/H264?ch=1&subtype=0')

myColorFinder = ColorFinder(False)
#hsvVals = {'hmin': 0, 'smin': 174, 'vmin': 0, 'hmax': 179, 'smax': 255, 'vmax': 255}
hsvVals = {'hmin': 8, 'smin': 124, 'vmin': 13, 'hmax': 24, 'smax': 255, 'vmax': 255}
# hsvVals = {'hmin': 0, 'smin': 109, 'vmin': 0, 'hmax': 19, 'smax': 255, 'vmax': 255}


posListX = []
posListY = []
pt1X=0
pt2X=0
pt1Y=0
pt2Y=0
fps_start_time = 0
fps = 0


angle_deg = 90
listX = [item for item in range(0, 1300)]
start = True
prediction = False
location = 0
#arduino = serial.Serial(port='COM7', baudrate=115200, timeout=.1)
# def write_read(x):
#     #    arduino.write(bytes(x, 'utf-8'))
#     arduino.write(bytes(x,'utf-8'))
#     time.sleep(0.05)
#     print(x)
#     #data = arduino.readline()
#     #return data

while True:
    fps_start_time = time.time()

    if start:
        if len(posListX) == 15: start = False
        success, img = cap.read()
        #finding dimensions of image
        dimensions = img.shape
        height = img.shape[0]
        width = img.shape[1]
        print('video Dimension    : ', dimensions)
        print('video Height       : ', height)
        print('video Width        : ', width)
        #
        diagonal_pixels = math.sqrt((width)**2 + (height)**2)
        print("Diagonal of video in pixels :", diagonal_pixels)
        #Converting diagonal pixels into inches
        diagonal_inches = diagonal_pixels * 0.014
        print("Diagonal in  inches", diagonal_inches)
        #formula for PPI
        PPI = diagonal_pixels/diagonal_inches
        print("pixel per inches", PPI)
        #converting PPI TO PPM
        inches_into_meters = PPI * 0.025
        print("PPI TO PPM", inches_into_meters)
        #screen resolution
        resolution = ctypes.windll.user32
        screensize = resolution.GetSystemMetrics(78), resolution.GetSystemMetrics(79)
        print("screen resolution is ", screensize)

        #finding frame rate per second FPS
        #fps_end_time = time.time()
        #time_diff = fps_end_time - fps_start_time
        #fps = 1/time_diff
        #fps_start_time = fps_end_time
        #print("frames per second", fps)

        #img = img[200:750, 450:1600]
        img = img[0:900, :]
        imgPrediction = img.copy()
        imgResult = img.copy()

        imgBall, mask = myColorFinder.update(img, hsvVals)
        imgCon, contours = cvzone.findContours(img, mask, 200)
        if contours:
            posListX.append(contours[0]['center'][0])
            posListY.append(contours[0]['center'][1])

        if posListX:
            if len(posListX) < 15:
                coff = np.polyfit(posListX, posListY, 2)

            for i, (posX, posY) in enumerate(zip(posListX, posListY)):
                #print(posListX)
                pos = (posX, posY)
                cv2.circle(imgCon, pos, 10, (0, 255, 0), cv2.FILLED)
                print('Value of i is: ', i)
                if i == 0:
                    pt1X, pt1Y = pos
                    print('Value of X1: ', '+', pt1X)
                    print('Value of Y1: ', '+', pt1Y)
                if i == 16:
                    pt2X, pt2Y = pos
                    print('Value of X2: ', '+', pt2X)
                    print('Value of Y2: ', '+', pt2Y)
                if i == 0:
                    cv2.line(imgCon, pos, pos, (0, 255, 0), 2)
                    cv2.line(imgResult, pos, pos, (0, 255, 0), 2)
                else:
                    cv2.line(imgCon, (posListX[i - 1], posListY[i - 1]), pos, (0, 255, 0), 2)
                    cv2.line(imgResult, (posListX[i - 1], posListY[i - 1]), pos, (0, 255, 0), 2)

            for x in listX:
                y = int(coff[0] * x ** 2 + coff[1] * x + coff[2])
                cv2.circle(imgPrediction, (x, y), 2, (255, 0, 255), cv2.FILLED)
                cv2.circle(imgResult, (x, y), 2, (255, 0, 255), cv2.FILLED)



            # Predict
            if len(posListX) < 11:
                # y = int(coff[0] * x ** 2 + coff[1] * x + coff[2])
                a, b, c = coff
                c = c - 550
                location = int((-b - math.sqrt(b ** 2 - (4 * a * c))) / (2 * a))
                prediction = 200 < location < 650

        # cv2.circle(imgResult, (location-10, 593), 10, (0, 255, 0), cv2.FILLED)
                angle_rad = math.atan2(550, location)
                angle_deg = int(angle_rad * 180 / math.pi)
                if prediction:
                    # write_read(str(angle_deg))
                    print('Angle is: ', str(angle_deg))
#                    cvzone.putTextRect(imgResult, str(angle_deg), (location, 650), colorR=(0, 0, 255),
#                                       scale=3, thickness=6, offset=20)
                                       #cvzone.putTextRect(imgResult, "Basket", (50, 150), colorR=(0, 200, 0),
        #                                   scale=5, thickness=10, offset=20)
        #                cv2.circle(imgResult, (x, 593), 10, (0, 255, 0), cv2.FILLED)
        #            else:
        #                cvzone.putTextRect(imgResult, "No Basket", (50, 150), colorR=(0, 0, 200),
        #                                  scale=5, thickness=10, offset=20)

        cv2.circle(imgResult, (location, 550), 30, (0, 0, 255), cv2.FILLED)
        cvzone.putTextRect(imgResult, "Predicted Angle: " + str(angle_deg) + " degree", (location, 500), colorR=(0, 0, 255),
                           scale=2, thickness=4, offset=20)
        dist1 = math.sqrt((pt2X - pt1X)**2 + (pt2Y - pt1Y)**2)
        print('calculated distance in pixels: ', dist1)
        # Converting Distance pixels into distance in meters
        dist2 = (diagonal_pixels * 0.014) * 0.025
        print("Distance in meters", dist2)
        cvzone.putTextRect(imgResult, "Distance: " + str('%.4s' % dist2 ) + "m/s", (location, 400),
                           colorR=(0, 0, 255),
                           scale=2, thickness=4, offset=20)


        #        angle_rad = math.atan2(550, location)
#        angle_deg = angle_rad * 180 / math.pi
#        if (angle_deg<60):
        # cv2.line(imgCon, (330, 593), (430, 593), (255, 0, 255), 10)
        imgResult = cv2.resize(imgResult, (0, 0), None, 0.7, 0.7)
        # imgStacked = cvzone.stackImages([img,imgCon,imgPrediction,imgResult],2,0.35)
        cv2.imshow("imgCon", imgResult)
        #cv2.imshow("imgBall", imgCon)
    start =True
    key = cv2.waitKey(20)
    fps_end_time = time.time()
    time_diff = fps_start_time - fps_end_time
        # calculate Speed
    speed = (dist2 * time_diff)

    print("speed in meters per second", speed)

