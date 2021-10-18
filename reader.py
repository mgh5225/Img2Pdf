import cv2
import numpy as np


class Reader:
    fileName = None
    cap = None

    def __init__(self, fileName):
        self.fileName = fileName
        self.cap = cv2.VideoCapture(self.fileName)
        if (self.cap.isOpened() == False):
            print("Error opening video file")

    def read(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret == True:
                yield ret, frame
            else:
                break
        return False, None
