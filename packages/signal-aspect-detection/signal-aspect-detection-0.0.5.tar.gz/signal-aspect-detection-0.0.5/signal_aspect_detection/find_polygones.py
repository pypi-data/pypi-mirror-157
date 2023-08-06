#https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/


import argparse
import imutils
import cv2
import matplotlib.pyplot as plt
import numpy as np


class Polygon:
    def __init__(self, cnts, approx, rect):
        self.contours = cnts
        self.polyline = approx
        self.rectangle = rect


def create_binary(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    threshi = cv2.bitwise_not(thresh)
    return threshi

def detect_polygones(image):
    polygones = []
   
    
    # find contours in the thresholded image and initialize the
    # shape detector
    cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)


    size = image.shape[0] * image.shape[1]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        s = w * h / size
        #filter smaller rectangles, <25 percent
        if s < 0.10: continue
        polygones.append(Polygon(cnts,approx,(x, y, w, h)))
        
    return polygones


def paint_polygones(image,polygones):
    for polygon in polygones:
        cv2.drawContours(image, polygon.contours, -1, color=(255, 255, 0), thickness=3) #thickness=cv2.FILLED
        #cv2.polylines(image, [polygon.polyline], True, (255,255,0), thickness=3) 
        x , y , w , h = polygon.rectangle
        cv2.rectangle(image, (x,y), (x + w,y + h), (0,0,255), thickness = 5)   