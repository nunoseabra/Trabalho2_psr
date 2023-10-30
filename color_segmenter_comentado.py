#!/usr/bin/env python3
# Shebang line

# Programação de Sistemas Robóticos
# Trabalho nº2 - Augmented Reality Paint

# Maria Rodrigues, nº 102384
# Nuno Seabra, nº
# Ricardo Baptista, nº


#--------- IMPORT FUNCTIONS ---------#

from asyncio import sleep
import pprint
import cv2
import json


#--------- INITIALIZATION ---------#  

# Initizalizes camera video capture
cap = cv2.VideoCapture(0)

# Initializes min and max color variables
prev_minr=0
prev_ming=0
prev_minb=0

prev_maxb=0
prev_maxg=0
prev_maxr=0



#--------- FUNCTIONS ---------#

# Callback function to update trackbars color limits
def update_limits(x):
    pass

# Funtion to open window with six trackbars for color segmentation
def openwin():
    # Creates OpenCV windows - original and segmentation mask
    cv2.namedWindow('Original Image')
    cv2.namedWindow('Color Mask')

    # Create trackbars for color limits
    cv2.createTrackbar('Bmin', 'Color Mask', 0, 255, update_limits)
    cv2.createTrackbar('Bmax', 'Color Mask', 255, 255, update_limits)
    cv2.createTrackbar('Gmin', 'Color Mask', 0, 255, update_limits)
    cv2.createTrackbar('Gmax', 'Color Mask', 255, 255, update_limits)
    cv2.createTrackbar('Rmin', 'Color Mask', 0, 255, update_limits)
    cv2.createTrackbar('Rmax', 'Color Mask', 255, 255, update_limits)

# Function to update trackbar limits
def trackbars(frame):
    # Image converted to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Gets current values from the trackbars
    min_b = cv2.getTrackbarPos('Bmin', 'Color Mask')
    max_b = cv2.getTrackbarPos('Bmax', 'Color Mask')

    min_g = cv2.getTrackbarPos('Gmin', 'Color Mask')
    max_g = cv2.getTrackbarPos('Gmax', 'Color Mask')

    min_r = cv2.getTrackbarPos('Rmin', 'Color Mask')
    max_r = cv2.getTrackbarPos('Rmax', 'Color Mask')

    # Previous value dictionary
    color_data = {"color":
            {'Blue':
            {'min': min_b, 'prev_min': prev_minb,'max': max_b, 'prev_max': prev_maxb},
            'Red':
            {'min': min_r, 'prev_min': prev_minr,'max': max_r, 'prev_max': prev_maxr},
            'Green': 
            {'min': min_g, 'prev_min': prev_ming,'max': max_g, 'prev_max': prev_maxg}
            }}

    return color_data, hsv, min_b, min_g, min_r, max_b, max_g, max_r

#Function to print selected values on trackbars
def selectPrint(color_data):
    # Minimum
    min_b=color_data['color']['Blue']['min']
    min_r=color_data['color']['Red']['min']
    min_g=color_data['color']['Green']['min']
    # Maximum
    max_b=color_data['color']['Blue']['max']
    max_r=color_data['color']['Red']['max']
    max_g=color_data['color']['Green']['max']
    # Previous minimum
    prev_minb=color_data['color']['Blue']['prev_min']
    prev_minr=color_data['color']['Red']['prev_min']
    prev_ming=color_data['color']['Green']['prev_min']
    # Previous maximum
    prev_maxb=color_data['color']['Blue']['prev_max']
    prev_maxr=color_data['color']['Red']['prev_max']
    prev_maxg=color_data['color']['Green']['prev_max']
    
    # If the current value differs from the previous value, prints new value for the trackbar limits
    if   min_b != prev_minb:
        print('Selected Threshold ' + str(min_b) + ' for limit Bmin')
    elif min_g != prev_ming:
        print('Selected Threshold ' + str(min_g) + ' for limit Gmin')
    elif min_r != prev_minr:
        print('Selected Threshold ' + str(min_r) + ' for limit Rmin')
    elif max_b != prev_maxb:
        print('Selected Threshold ' + str(max_b) + ' for limit Bmax')
    elif max_g != prev_maxg:
        print('Selected Threshold ' + str(max_g) + ' for limit Gmax')
    elif max_r != prev_maxr:
        print('Selected Threshold ' + str(max_r) + ' for limit Rmax')


# Function to update window
def updatewin(color_data, hsv, frame, min_b, min_g, min_r, max_b, max_g, max_r):
    # Updates previous trackbar value
    # Previous minimum   
    color_data['color']['Blue']['prev_min']= min_b
    color_data['color']['Red']['prev_min']= min_r
    color_data['color']['Green']['prev_min']= min_g
    # Previous maximum  
    color_data['color']['Blue']['prev_max']= max_b
    color_data['color']['Red']['prev_max']= max_r
    color_data['color']['Green']['prev_max']= max_g

    # Defines color limits based on trackbars
    lower_bound = (min_b, min_g, min_r)
    upper_bound = (max_b, max_g, max_r)

    #  Creates color detection mask
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
 
    # Updates OpenCv frame window
    frame_sized=cv2.resize(frame,(600,400))
    cv2.imshow('Original Image', cv2.flip(frame_sized,1))

    # Updates OpenCv mask window
    mask_sized=cv2.resize(mask,(600,400))
    cv2.imshow('Color Mask', cv2.flip(mask_sized,1))    

    return color_data

# Function to save color limits data in a JSON file
def savefile(min_b, min_g, min_r, max_b, max_g, max_r):

    # If a key is pressed, reads key
    key = cv2.waitKey(1)

    if key == ord('w'):                                 # If 'w' is pressed, gets limits dictionary
        limits = {'limits': {'B': {'min': min_b, 'max': max_b}, 
                             'G': {'min': min_g, 'max': max_g}, 
                             'R': {'min': min_r, 'max': max_r}}}
        
        with open('limits.json', 'w') as file:          # Save limits in a JSON file
            json.dump(limits,file)
            print('Saved.....') 


#--------- MAIN FUNCTION ---------#

def main():

    # Open window function
    openwin()

    while True:
        # If a frame is not captured the code breaks
        ret, frame = cap.read()

        # Calling trackbars
        color_data, hsv, min_b, min_g, min_r, max_b, max_g, max_r = trackbars(frame)

        # If a frame is not captured the code breaks
        if not ret:
          break
        
        # Comparing minimum values to previous minimum values
        #selectPrint(color_data) nao funciona
        
        
        # Updates window                  
        color_data=updatewin(color_data, hsv, frame, min_b, min_g, min_r, max_b, max_g, max_r)

        

        # Visiualization function
        key=cv2.waitKey(1)
        if key == ord('w'):            # when 'q' pressed quits program
            savefile(min_b, min_g, min_r, max_b, max_g, max_r)
            print('\n Limits Saved.....\n ')
            break
        elif key == ord('d'): 
            print('\n Interrupted.....\n ')
            break
        


#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()
