
import imp
from itertools import count
from pickle import FALSE, TRUE
from random import random
from time import time
from unittest import result
import numpy as np
import cv2 as cv
import torch
import sys
import time
from centroidtracker import *


ENTER_AREA=0
EXIT_AREA=0


def isObjectCounted(id,detectedObjects):
    result=FALSE
    for obj in detectedObjects:
        if obj['id'] == id and obj['counted'] == TRUE:
            result= TRUE
            break
    return result

if __name__ == '__main__':
    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    cap = cv.VideoCapture(sys.argv[1:][0])
    ct = CentroidTracker()
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH )
    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT )
    detectedObjects=[]
    initialTotalArea1=0
    initialTotalArea2=0
    while cap.isOpened():
        ret, frame = cap.read()
        boxes=[]
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        results=model(frame)
        pandaFrameRes=results.pandas().xyxy[0]
        
        # height, width
        height = frame.shape[0]/2
        width = frame.shape[1]/2
        lineStart=(0,int(height))
        lineEnd=(int(frame.shape[1]),int(height))
    
        cv.line(frame,lineStart, lineEnd, (0,0,255), 2)
        cv.putText(frame, "EXIT AREA:"+str(EXIT_AREA),(0,int(height)+20), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv.LINE_AA)
        cv.putText(frame, "ENTER AREA:"+str(ENTER_AREA),(0,int(height)-20), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv.LINE_AA) 
        
        for boundingBox in pandaFrameRes.values:
            xmin=int(boundingBox[0])
            ymin=int(boundingBox[1]) #ymin
            xmax=int(boundingBox[2]) #xmax
            ymax=int(boundingBox[3])
            className=boundingBox[6]
            confidence=boundingBox[4]
            if confidence > 0.20 and className == 'person':
                boxes.append([xmin,ymin,xmax,ymax])
           
        currentFrameObjects = ct.update(np.array(boxes))

        if initialTotalArea1 == 0 and initialTotalArea2 == 0:
            for (objectID, centroid) in currentFrameObjects.items():
                if  centroid[1] > int(height/2):
                    initialTotalArea2+=1
                elif centroid[1] < int(height/2):
                    initialTotalArea1+=1
       
       # loop over the tracked objects
        for (objectID, centroid) in currentFrameObjects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            cv.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            if isObjectCounted(objectID,detectedObjects) == FALSE:
                #split people by area
                if int(centroid[1]) > int(height/2):
                    EXIT_AREA+= (initialTotalArea2-initialTotalArea2) + 1
                    detectedObjects.append({"id":objectID,"counted":TRUE})
                elif int(centroid[1]) < int(height/2):
                    ENTER_AREA+= (initialTotalArea1-initialTotalArea1) + 1
                    detectedObjects.append({"id":objectID,"counted":TRUE})
                
	    # show the output frame
        cv.imshow("Frame", frame)
        if cv.waitKey(1) == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()

