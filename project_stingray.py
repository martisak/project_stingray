
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import thunder
import json
import math
import datetime

numberOfMissiles = 4

colors = {
        'white': (255, 255, 255),
        'blue': (255, 0, 0),
        'red': (0,0,255)
    }


def addtimestamp(image):
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, ts, (15, frame.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,  0.40, colors['white'], 1)


def drawtarget(image, face):

    color = colors['blue']
    x, y, w, h = face

    # top left
    pt1 = (x, y)
    pt2 = (x+5, y)
    cv2.line(image, pt1, pt2, color)

    pt1 = (x, y)
    pt2 = (x, y+5)
    cv2.line(image, pt1, pt2, color)

    # top right
    pt1 = (x+w, y)
    pt2 = (x+w-5, y)
    cv2.line(image, pt1, pt2, color)

    pt1 = (x+w, y)
    pt2 = (x+w, y+5)
    cv2.line(image, pt1, pt2, color)

    # bottom right
    pt1 = (x+w, y+h)
    pt2 = (x+w-5, y+h)
    cv2.line(image, pt1, pt2, color)

    pt1 = (x+w, y+h)
    pt2 = (x+w, y+h-5)
    cv2.line(image, pt1, pt2, color)

    # bottom left
    pt1 = (x, y+h)
    pt2 = (x+5, y+h)
    cv2.line(image, pt1, pt2, color)

    pt1 = (x, y+h)
    pt2 = (x, y+h-5)
    cv2.line(image, pt1, pt2, color)


def drawcrosshair(image):

    color = colors['white']

    pt1 = ((screenWidth / 2) - 20, screenHeight / 2)
    pt2 = ((screenWidth / 2) - 5, screenHeight / 2)

    cv2.line(image, pt1, pt2, color)

    pt1 = ((screenWidth / 2) + 20, screenHeight / 2)
    pt2 = ((screenWidth / 2) + 5, screenHeight / 2)

    cv2.line(image, pt1, pt2, color)

    pt1 = (screenWidth / 2, (screenHeight / 2) - 20)
    pt2 = (screenWidth / 2, (screenHeight / 2) - 5)

    cv2.line(image, pt1, pt2, color)

    pt1 = (screenWidth / 2, (screenHeight / 2) + 20)
    pt2 = (screenWidth / 2, (screenHeight / 2) + 5)

    cv2.line(image, pt1, pt2, color)


# Create missile launch controller - make sure user has access to USB port
launcher = thunder.controller()

# Load configuration file
conf = json.load(open("config.json"))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf['camera']['resolution'])
camera.framerate = conf['camera']['fps']

# Output video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, camera.framerate/4,
                      tuple(conf['camera']['resolution']))

screenWidth, screenHeight = conf['camera']['resolution']

# Control loop parameters
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
    frame = cv2.flip(frame, -1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    biggestFace = None
    biggestFaceArea = 0

    for face in faces:
        x, y, w, h = face

        drawtarget(frame, face)

        if (w*h > biggestFaceArea):
            biggestFace = face
            biggestFaceArea = w*h

    if biggestFace is not None and conf['launcher']['fire']:

        (x, y, w, h) = biggestFace

        aimPoint = (x + w / 2, y + h / 2)

        x_diff = abs(aimPoint[0] - camera.resolution[0] / 2)
        y_diff = abs(aimPoint[1] - camera.resolution[1] / 2)

        print("[INFO] Found target at ({0}, {1})".format(x_diff, y_diff))

        # Assuming it takes about a second to
        # go from edge to edge of the screen
        x = aim_multiplier * x_diff / (1.0 * camera.resolution[0])
        y = aim_multiplier * y_diff / (1.0 * camera.resolution[1])

        if math.sqrt(x_diff**2 + y_diff**2) < fire_thresh and \
                numberOfMissiles > 0:

            launcher.fire()
            print("[INFO] Fire!")
            # numberOfMissiles -= 1

        elif conf['launcher']['slew']:

            if aimPoint[0] < camera.resolution[0]/2:
                launcher.left(x)
            elif aimPoint[0] > camera.resolution[0]/2:
                launcher.right(x)

            if aimPoint[1] < camera.resolution[1]/2:
                launcher.up(y)
            elif aimPoint[1] > camera.resolution[1]/2:
                launcher.down(y)

    # Add timestamp
    addtimestamp(frame)

    # Draw crosshairs
    drawcrosshair(frame)

    if launcher.isSlewing():
        cv2.putText(frame, "Slewing...", (15, 15),
                cv2.FONT_HERSHEY_SIMPLEX,  0.40, colors['red'], 1)

    if conf['camera']['show_video']:
        cv2.imshow("Frame", frame)

    if conf['camera']['save_video']:
        out.write(frame)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

out.release()
cv2.destroyAllWindows()
