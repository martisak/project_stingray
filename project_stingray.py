
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import thunder
import json

numberOfMissiles = 4

colors = {
        'white': (255, 255, 255)
    }

def drawcrosshair(image):
    color = colors['white']
    pt1 = ((screenWidth / 2) - 20, screenHeight / 2)
    pt2 = ((screenWidth / 2) + 20, screenHeight / 2)
    cv2.line(image, pt1, pt2, color)

    pt1 = (screenWidth / 2, (screenHeight / 2) - 20)
    pt2 = (screenWidth / 2, (screenHeight / 2) + 20)

    cv2.line(image, pt1, pt2, color)

    return image

# Create missile launch controller - make sure user has access to USB port
launcher = thunder.controller()

# Load configuration file
conf = json.load(open("config.json"))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()

camera.resolution = tuple(conf['camera']['resolution'])
camera.framerate = conf['camera']['fps']

screenWidth, screenHeight = conf['camera']['resolution']

aim_multiplier = conf['launcher']['aim_multiplier']
fire_thresh = conf['launcher']['fire_threshold']

rawCapture = PiRGBArray(camera, size=camera.resolution)

face_cascade = cv2.CascadeClassifier(conf['camera']['classifier'])

# allow the camera to warmup
time.sleep(conf['camera']['warmup_time'])

avg = None

for frame in \
        camera.capture_continuous(
            rawCapture, format="bgr",
            use_video_port=True):

    frame = frame.array

    # Flip frame, since we have mouted camera upside-down
    frame = cv2.flip(frame,-1) 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    biggestFace = None
    biggestFaceArea = 0

    for face in faces:
        x,y,w,h = face
        cv2.rectangle(frame,(x,y),(x+w,y+h), (255,0,0) , 2)

        if (w*h > biggestFaceArea):
            biggestFace = face
            biggestFaceArea = w*h

    if biggestFace is not None:

        (x, y, w, h) = biggestFace

        aimPoint = (x + w / 2, y + h / 2 )

        color = (255,0, 0)

        cv2.circle(frame, aimPoint, 5, color, thickness = -1)

        x_diff = abs( aimPoint[0] - camera.resolution[0] / 2 )
        y_diff = abs( aimPoint[1] - camera.resolution[1] / 2 )

        print("[INFO] Found target at ({0}, {1})".format(x_diff, y_diff))
        
        # Assuming it takes about a second to go from edge to edge of the screen
        x = aim_multiplier * x_diff /(1.0 * camera.resolution[0])
        y = aim_multiplier * y_diff/(1.0 * camera.resolution[1])
        
        if x_diff < fire_thresh and y_diff < fire_thresh and numberOfMissiles > 0:
            launcher.fire()
            print("[INFO] Fire!")
            #numberOfMissiles -= 1
        else:
            if aimPoint[0] < camera.resolution[0]/2:
                launcher.left(x)
            elif aimPoint[0] > camera.resolution[0]/2:
                launcher.right(x)

            if aimPoint[1] < camera.resolution[1]/2:
                launcher.up(y)
            elif aimPoint[1] > camera.resolution[1]/2:
                launcher.down(y)

    # Draw crosshairs
    frame = drawcrosshair(frame)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)




