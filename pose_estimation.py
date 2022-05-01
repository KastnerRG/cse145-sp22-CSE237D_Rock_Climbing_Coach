# -*- coding: utf-8 -*-
"""Pose_Estimation.ipynb

Automatically generated by Colaboratory.
"""

# !pip install mediapipe

# from google.colab import drive
# drive.mount('/content/drive')

import cv2
import mediapipe as mp
import time
from scipy import spatial


# initialize mediapipe requirements
mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

# input video path
cap = cv2.VideoCapture('rock_dataset_0/clip2/climb.mp4')

# global dict to store the coordiantes (required towards MVP)
dict_coordinates = {'left_hand': [], 'right_hand': [], 'left_leg': [], 'right_leg': [], 'left_hip': [], 'right_hip': []}

# compute landmarks for a frame
def find_pose(img):
  break_signal = False
  results = []
  try:
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    print('Landmarks:', results.pose_landmarks)
  except:
    break_signal = True

  return img, results, break_signal

# retrieve coordinates from lm_list and store the coordinates in the global dict
def store_coordinates(lm_list):
  global dict_coordinates
  dict_coordinates['left_hand'].append((lm_list[38], lm_list[39])) #left_index - x, y 
  dict_coordinates['right_hand'].append((lm_list[40], lm_list[41])) #right_index - x, y
  dict_coordinates['left_hip'].append((lm_list[46], lm_list[47])) #left_hip - x, y
  dict_coordinates['right_hip'].append((lm_list[48], lm_list[49])) #right_hip - x, y
  dict_coordinates['left_leg'].append((lm_list[62], lm_list[63])) #left_foot - x, y
  dict_coordinates['right_leg'].append((lm_list[64], lm_list[65])) #right_foot - x, y

# compute cosine smilarity between two lm lists 
def check_similarity(list1, list2):
  result = 1 - spatial.distance.cosine(list1, list2)
  return result

# plot the image only when the frames are dissimilar
def plot_image(img, results, cx, cy, pTime):
  mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
  cv2.circle(img, (cx, cy), 5, (255,0, 150), cv2.FILLED)
  cTime = time.time()
  fps = 1 / (cTime - pTime)
  pTime = cTime
    
  cv2.putText(img, str(int(fps)), (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)
  cv2.imshow('image', img)
  cv2.waitKey(1)

def main():
  prev = []
  first_frame_flag = True
  total_frames_count = 0
  stored_frames_count = 0
  pTime = 0

  while True:
    print('----------------------')
    print('Processing a new frame')
    success, img = cap.read()
    img, results, main_break_signal = find_pose(img)
    
    # the signal means that there are no more input frames in the video, and thus the code must terminate
    if (main_break_signal == True):
      break
    
    lm_list = []

    if results.pose_landmarks:     
      # add all 66 cordinates to lm_list
      for id, lm in enumerate(results.pose_landmarks.landmark):  
        h, w, c = img.shape
        cx, cy = int(lm.x*w), int(lm.y*h)
        lm_list.append(cx)
        lm_list.append(cy)

      # for the first frame, compute and store the coordinates
      if(first_frame_flag == True):
        store_coordinates(lm_list)
        print("Similarity found for the first frame and coordinates stored")
        prev = lm_list
        first_frame_flag = False
        stored_frames_count += 1
        plot_image(img, results, cx, cy, pTime)


      # from next frame onwards, first check similarity and then store the coordinates
      else:
        result = check_similarity(prev, lm_list) #prev = 66 cordinates, lm_list = 66 cordinates
        print('Similarity Value:', result)
        if(result < 0.99999):
          store_coordinates(lm_list)
          print("Similarity found and coordinates stored")
          stored_frames_count += 1
          plot_image(img, results, cx, cy, pTime)
        
        prev = lm_list
          
      print('Prev list: ', prev)
      print('Length of prev list: ', len(prev))
      print('LM list: ', lm_list)
      print('Length of lm_list: ', len(lm_list))

    total_frames_count += 1

  print('---------- Processsing Completed ----------')
  print('Total frames processed: ', total_frames_count)
  print('Total frames stored: ', stored_frames_count)

if __name__ == "__main__":
    main()