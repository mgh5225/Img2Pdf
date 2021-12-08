import cv2
import numpy as np


class Writer:
    frames = []
    unique_frames = []
    alpha = 0
    writers_number = 0
    last_frame_index = 0

    def __init__(self, frames, alpha):
        self.frames = frames
        self.alpha = alpha
        self.unique_frames = []
        self.last_frame_index = 0
        Writer.writers_number += 1

    def recursive_check(self, cur_frame_index):
        frame = self.frames[cur_frame_index]
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for last_frame in self.unique_frames:
            gray_last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)

            frame_diff = cv2.absdiff(gray_frame, gray_last_frame)

            if np.mean(frame_diff) < self.alpha:
                return False
        return True

    def normal_check(self, cur_frame_index):
        frame = self.frames[cur_frame_index]
        last_frame = self.frames[self.last_frame_index]

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)

        frame_diff = cv2.absdiff(gray_frame, gray_last_frame)

        if np.mean(frame_diff) >= self.alpha:
            return True
        return False

    def run(self, recursive_check=False):
        if Writer.writers_number == 1:
            self.unique_frames.append(self.frames[0])

        while self.last_frame_index < len(self.frames):
            flag = False
            for i in range(self.last_frame_index + 1, len(self.frames)):
                check = False

                if recursive_check:
                    check = self.recursive_check(i)
                else:
                    check = self.normal_check(i)

                if check:
                    self.unique_frames.append(self.frames[i])
                    self.last_frame_index = i
                    flag = True
                    break

            if flag == False:
                break

        return self.unique_frames
