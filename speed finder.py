import cv2
import imutils
import winsound
import time

# declaration of variables  
initialTime = 0
initialDistance = 0
changeInTime = 0  
changeInDistance = 0  
  
listDistance = []  
listSpeed = []


determined_distance = 24#cm (distance between camera and object)
actual_width= 300#pixels - convert cm into pixels(diameter of the detected circle in the frame)

#enter the values of HSV using the HSV value.
lower = (0,52,175)
upper = (179,255,255)

#address= "https://192.168.154.64:8080/video"  #if we use webcam
camera = cv2.VideoCapture(0)
#camera = cv2.VideoCapture(address) # access frame from webcam
camera.set(cv2.CAP_PROP_FPS, int(10))


#determined distance between camera and reference image
    
def distance_finder(determined_distance,rf_width, actual_width):
    distance = (rf_width*determined_distance)/actual_width
    return distance

###############################################


def averageFinder(completeList, averageOfItems):  
    lengthOfList = len(completeList)  
    selectedItems = lengthOfList - averageOfItems  
    selectedItemsList = completeList[selectedItems:]  
    average = sum(selectedItemsList) / len(selectedItemsList)
    return average

###########################################

def speedFinder(coveredDistance, timeTaken):    
    speed = coveredDistance / timeTaken    
    return speed

################################################
while True:
    _,frame = camera.read()
    frame = imutils.resize(frame, width=1150)
    blurred = cv2.GaussianBlur(frame, (11,11),0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange( hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask =cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None  
    if len(cnts)>0:
        c = max(cnts, key=cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]),int(M["m01"] / M["m00"]))
        font = cv2.FONT_HERSHEY_SIMPLEX
        if radius > 10 :
                cv2.circle(frame, (int(x),int(y)),int(radius),(255,255,255),2)
                cv2.circle(frame, center,5,(0,255,255),-1)
        diameter = radius*2
        rf_width= round(diameter, 1)
        if diameter !=0:
            distanceInMeters = distance_finder(determined_distance,actual_width,rf_width)
            listDistance.append(distanceInMeters)
            averageDistance = averageFinder(listDistance, 2)
            #converting into meters
            distanceInMeters = averageDistance/100
            #print(averageDistance)        
            if initialDistance != 0:
                #change in distance
                changeInDistance = initialDistance - distanceInMeters
                if changeInDistance <0:
                    changeInDistance*-1
                #change in time
                changeInTime = time.time() - initialTime
                #change in speed
                speed = speedFinder(coveredDistance=changeInDistance, timeTaken=changeInTime)
                listSpeed.append(speed)  
                averageSpeed = averageFinder(listSpeed, 10)
                if averageSpeed <0:
                    averageSpeed = averageSpeed * -1
                averageSpeed= averageSpeed*3.6  
                cv2.line(frame, (45, 70), (235, 70), (0, 0, 0), 22)
                cv2.putText(frame, f"Speed: {round(averageSpeed, 2)} km/h", (50, 75), font, 0.6, (0, 255, 220), 2)
                #winsound condition (if the relative acceleration is greater than 40km within 10 m)
                if averageSpeed>=40 and distanceInMeters<=10: 
                    duration=2000
                    freq=450
                    winsound.Beep(freq, duration)
        initialDistance = distanceInMeters
        initialTime = time.time()
        cv2.line(frame, (45, 25), (255, 25), (255, 0, 255), 30)  
        cv2.line(frame, (45, 25), (255, 25), (0, 0, 0), 22)  
        cv2.putText(frame, f"Distance = {round(distanceInMeters,2)} m", (50, 30), font, 0.6, (255,255,255), 2)          
   # Recorder.write(frame)                     
    cv2.imshow("frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"): #press q to exit 
        break
camera.release()
cv2.destroyAllWindows()
