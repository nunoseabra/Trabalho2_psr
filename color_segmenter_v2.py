#!/usr/bin/env python3

#--------- IMPORT FUNCTIONS ---------#

from asyncio import sleep
import pprint
import cv2
import json


#--------- INITIALIZATION ---------#  

# Initizalizes camera video capture
cap = cv2.VideoCapture(0)

# Initializing min and max color variables
prev_minr=0
prev_ming=0
prev_minb=0

prev_maxb=0
prev_maxg=0
prev_maxr=0

i= 0

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
    # Converte a imagem para o espaço de cores HSV 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Obtenha os valores atuais das trackbars
    min_b = cv2.getTrackbarPos('Bmin', 'Color Mask')
    max_b = cv2.getTrackbarPos('Bmax', 'Color Mask')

    min_g = cv2.getTrackbarPos('Gmin', 'Color Mask')
    max_g = cv2.getTrackbarPos('Gmax', 'Color Mask')

    min_r = cv2.getTrackbarPos('Rmin', 'Color Mask')
    max_r = cv2.getTrackbarPos('Rmax', 'Color Mask')

    color_data = [
            {'color':'Blue', 'min': min_b, 'prev_min': prev_minb},
            {'color':'Red', 'min': min_r, 'prev_min': prev_minr},
            {'color':'Green', 'min': min_g, 'prev_min': prev_ming}]
    
    return color_data, hsv, min_b, min_g, min_r, max_b, max_g, max_r

# Function to update window
def updatewin(color_data, hsv, frame, min_b, min_g, min_r, max_b, max_g, max_r):
        
    color_data[0]['prev_min']=min_b
    color_data[1]['prev_min']=min_r
    color_data[2]['prev_min']=min_g

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


# Function to save color limits data in a JSON file
def savefile(min_b, min_g, min_r, max_b, max_g, max_r):

    if key == ord('w'):     # If 'w' pressed gets limit dictionary
        limits = {'limits': {'B': {'min': min_b, 'max': max_b}, 'G': {'min': min_g, 'max': max_g}, 'R': {'min': min_r, 'max': max_r}}}
        
        with open('limits.json', 'w') as file:          # Save limits in a JSON file
            json.dump(limits,file)
            print('Saved.....') 


#--------- MAIN FUNCTION ---------#

def main():

    # Open window function
    openwin()

    color_data, hsv, min_b, min_g, min_r, max_b, max_g, max_r = trackbars(frame)

    while True:
        # If a frame is not captured the code breaks
        ret, frame = cap.read()
        if not ret:
          break

        # Reading all minimum values
        def getMin(dict):
           i = 1
           min = dict[i]['min']
           return min
        
        # Calling all previous minimum values
        def getPrevMin(dict):
           i = 1
           prevmin = dict[i]['prev_min']
           return prevmin
        
        # Comparing minimum values to previous minimum values
        if getMin(color_data) != getPrevMin(color_data):        # If limits change prints warning message with new parameters
                print('The color ' + str(color_data[i]['color']) + ' minimum changed to: '+ str(color_data[i]['min']))

        # Updates window                  
        updatewin(color_data, hsv, frame, min_b, min_g, min_r, max_b, max_g, max_r)

        key = cv2.waitKey(1)

        # Visiualization function
        if key == ord('q'):            # when 'q' pressed quits program
            print('Interrupted.....')
            break
        else:
            savefile(min_b, min_g, min_r, max_b, max_g, max_r)


#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()