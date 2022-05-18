#BASKET BALL SHOT PREDICTOR USING OPENCV PYTHON-COMPUTER VISION

IMPORT PACKAGES START WITH VIDEO RESIZE 

import cv2
import cvzone.ColorModule
from cvzone.ColorModule import ColorFinder
import numpy as np
#Initialize the Video
cap = cv2.VideoCapture('Videos/vid (3).mp4')
# CREATE THE COLOR FINDER OBJECT
#false means no debug mode we are running the code
#True means debug mode we are debugging

myColorFinder = ColorFinder(False) #false means no debug mode we are runing the code
hsvVals ={'hmin': 0, 'smin': 107, 'vmin': 86, 'hmax': 15, 'smax': 255, 'vmax': 255}
#variables
posListX, posListY= [], []   #to display for all frame  AND 
WE ARE RELLYING ON THE LIST TO FIND THE CURVE
xList = [item for item in range(0, 1300)]         #x-axis from 0 -1300

while True:
    # Grab the image
    success, img = cap.read()
    #Display image
DISPLAY IMAGE TO FIND COLOR OF BALL and then can apply on our video
    #img = cv2.imread("Ball.png")
IMAGE RESIZE
    img = img[0:900, :]

    #find color of ball/contours in an image
    # returning image color and mask
    imgColor, mask = myColorFinder.update(img, hsvVals)

#FIND LOCATION OF THE BALL (original image and make a copy of that.)
#IT WILL RETURM IMAGE CONTOURS (and move the trackbars)
    imgContours, contours = cvzone.findContours(img, mask, minArea=500)

#DISPLAY POINTS ,BY POINTS PUT CIRCLES.TAKE A BIGGEST CONTOUR(0 IS THE BIGEST CONTOUR) AND ALSO CENTER POINTS
if contours:
        posListX.append(contours[0]['center'][0])
        posListY.append(contours[0]['center'][1])
        #print(cx,cy)                   cx,cy    center points
    
#POLYNOMIAL REGRESSION Y=AX^2+BX+C  use numpy
# Find the Coefficients
if posListX:
A, B, C = np.polyfit(posListX, posListY, 2) #2nd order polynomial function and also QUADRATIC

#DRAWING A LINER POINT TO POINT     
for i, (posX,posY) in enumerate(zip(posListX, posListY)): #because we want to run two for loops
pos = (posX,posY)
cv2.circle(imgContours, pos, 10, (0, 255, 0), cv2.FILLED)

 #for previous position
if i ==0:
cv2.line(imgContours,  pos, pos, (0, 255, 0), 2)
else:
cv2.line(imgContours, pos, (posListX[i-1], posListY[i-1]), (0, 255, 0), 2)   #[i-1] previous position

#CALCULATING y VALUES FROM CORESPONDING X-VALUES
for x in xList:
y = int(A * x ** 2 + B * x + C)     #TAKE VALUES FROM    
if posListX:
cv2.circle(imgContours, (x, y), 2, (255, 0, 255), cv2.FILLED)  #THE PREDICTED LINE

#posListX.append(contours[0]['center'][0]) #bigs will be first one
#posListY.append(contours[0]['center'][1])

# PREDICTION
# X values 331 to 435  Y 590
#find value of x when y is 590.if value of x is in between 331 to 435 then the ball is in the basket
a = A
b = B
c = C-590
x = (-b- math.sqrt(b**2-(4*a*c)))/(2*a) 
print(x)
if 331 < x < 436:
cvzone.putTextRect(imgContours, "In the Basket", (50, 150), scale=5, thickness=5, colorR=(0, 255, 0))
else:
cvzone.putTextRect(imgContours, "No Basket", (50, 150), scale=5, thickness=5, colorR=(0, 0, 255))


#Display
imgContours = cv2.resize(imgContours, (0, 0), None, 0.7, 0.7) #through this we will find counturs
#cv2.imshow("Image",img)
cv2.imshow("Imagecolor",imgContours)
#WAIT KEY 
cv2.waitKey(60)


