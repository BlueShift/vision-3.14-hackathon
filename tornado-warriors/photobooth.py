import subprocess
import numpy as np
import cv2
import os
import time
import sys
import math
import glob
import signal
from PIL import Image

pics = glob.glob('/run/shm/test*.jpg')
for t in range(0, len(pics)):
  os.remove(pics[t])

def Camera_start(wx, hx):
  global p
  rpistr = \
      'libcamera-vid -t 0 --framerate 30 --autofocus --codec mjpeg --segment 1 -n -o /run/shm/test%06d.jpg --width ' \
      + str(wx) + ' --height ' + str(hx)
  p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)

width = 640
height = 480
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')
open_eyes_detected = 0
smile_detected = 0
face_detected = 0
start = 0
tilted = False

_img = None
_x = 0
_y = 0
_w = 0
_h = 0

cv2.namedWindow('Frame')
Text = ''
ttrat = time.time()

def mouse_action(event,x,y,flags,param):
  global p
  if event == cv2.EVENT_LBUTTONDOWN:
    if len(eyes) == 2 and smile_detected == 0 and tilted is False:
      os.killpg(p.pid, signal.SIGTERM)
      cv2.destroyAllWindows()
      cv2.imwrite('PHOTO_BOOTH.jpg', _img)
      with Image.open('PHOTO_BOOTH.jpg') as img:
        img.load()
        cropped_img = img.crop((_x-70, _y-100, _x + _h + 70, _y + _h + 40 ))
        cropped_img.show()
    else:
      print('PHOTO DEMANDS ARE NOT MET!')

cv2.setMouseCallback('Frame', mouse_action)

Camera_start(width, height)

while True:
  if time.time() - ttrat > 3 and ttrat > 0:
    Text = ''
    ttrat = 0

  pics = glob.glob('/run/shm/test*.jpg')
  while len(pics) < 2:
    pics = glob.glob('/run/shm/test*.jpg')

  pics.sort(reverse=True)
  img = cv2.imread(pics[1])
  _img = img
  if len(pics) > 2:
    for tt in range(2, len(pics)):
      os.remove(pics[tt])

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray, 1.1, 5)
  face_detected = 0

  for (x, y, w, h) in faces:
    _x = x
    _y = y
    _w = w
    _h = h

    face_detected = 1
    face_size = math.sqrt(w * w + y * y)
    roi_gray = gray[y:y + h, x:x + w]
    roi_color = img[y:y + h, x:x + w]

    open_eyes_detected = 0
    eyes_tilt = eye_cascade.detectMultiScale(gray[y:y + h, x:x + w], 1.1, 4)
    eyes = eye_cascade.detectMultiScale(roi_gray, 1.25, 5)
    index = 0
    eye_1 = [None, None, None, None]
    eye_2 = [None, None, None, None]

    for (ex, ey, ew, eh) in eyes:
      open_eyes_detected = 1
      cv2.putText(img, 'Eyes Open: ' + str(len(eyes)), (10, height - 30), 0, 0.6, (0, 255, 0))

    for (ex, ey, ew, eh) in eyes_tilt:
      if index == 0:
        eye_1 = [ex, ey, ew, eh]
      elif index == 1:
        eye_2 = [ex, ey, ew, eh]

      index = index + 1
      if eye_1[0] is not None and eye_2[0] is not None:
        if eye_1[0] < eye_2[0]:
          left_eye = eye_1
          right_eye = eye_2
        else:
          left_eye = eye_2
          right_eye = eye_1

        left_eye_center = (int(left_eye[0] + left_eye[2] / 2), int(left_eye[1] + left_eye[3] / 2))
        right_eye_center = (int(right_eye[0] + right_eye[2] / 2), int(right_eye[1] + right_eye[3] / 2))

        left_eye_x = left_eye_center[0]
        left_eye_y = left_eye_center[1]
        right_eye_x = right_eye_center[0]
        right_eye_y = right_eye_center[1]

        delta_x = right_eye_x - left_eye_x
        delta_y = right_eye_y - left_eye_y
        if delta_x == 0:
          continue

        angle = np.arctan(delta_y / delta_x)
        # Converting radians to degrees
        angle = angle * 180 / np.pi

        # Provided a margin of error of 10 degrees
        # (i.e, if the face tilts more than 10 degrees
        # on either side the program will classify as right or left tilt)

        if angle > 10:
          tilted = True
          cv2.putText(img, 'RIGHT TILT :' + str(int(angle)) + ' degrees', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_4)
        elif angle < -10:
          tilted = True
          cv2.putText(img, 'LEFT TILT :' + str(int(angle)) + ' degrees', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_4)

      smile, rejectLevels, levelWeights = smile_cascade.detectMultiScale3(roi_gray, 1.25, 5, outputRejectLevels=True)
      if len(levelWeights) == 0:
        smile_detected = 0
        cv2.putText(img, 'Not Smiling', (400, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
      else:
          if max(levelWeights) < 2:
            smile_detected = 0
            cv2.putText(img, 'Not Smiling', (400, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
          else:
            smile_detected = 1
            cv2.putText(img, 'Smiling', (400, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

  cv2.imshow('Frame', img)
  cv2.waitKey(10)
