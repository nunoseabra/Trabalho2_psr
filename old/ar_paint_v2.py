#!/usr/bin/env python3

#--------- IMPORT FUNCTIONS ---------#

from asyncio import sleep
from colorama import Fore, Style
import cv2
import json
import argparse
import numpy as np
from datetime import datetime


#--------- INITIALIZATION ---------#

# Initializes video capture
cap = cv2.VideoCapture(0)

# Definies initial variables for color (red) and pencil size
pencil_color = (0, 0, 255)
pencil_size = 2 


# Defines blank canvas
screen = np.full((480, 640, 3),255, dtype=np.uint8)
    

#--------- FUNCTIONS ---------#

# Funtion to open the JSON file and read the limits
def jsonfile():

    # Argparse description and arguments
    parser = argparse.ArgumentParser(description='Augmented Reality Paint')

    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = parser.parse_args()
    print(args)

    # Loads color limitis from the JSON file
    with open(args.json, 'r') as file:
        limits=json.load(file)

    return limits


# Function to calculate the centroid based on JSON file limits
def centroid(frame,limits,pencil_size,pencil_color):

    # Image converted to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detects color based on JSON file limits
    mask = cv2.inRange(hsv, (limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']),
                       (limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']))

    # Finds the contours of the largest object in the mask area
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # If contours are found, the largest contour is the one with the biggest area
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)

        # If contour is no zero, calculate centroid
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Draws centroid in the original image with a red cross
            cv2.drawMarker(frame, (cX, cY), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)

            # Uses the center of the image to paint canvas
            if pencil_size % 2 == 0:                                                   # Checks if the pencil size is even (and its half the diameter)       
                cv2.circle(frame, (cX, cY), pencil_size // 2, pencil_color, -1)        # Draws a circle in the centroid - frame
                cv2.circle(screen, (cX, cY), pencil_size // 2, pencil_color, -1)       # Draws a circle in the centroid - screen

            else:                                                                      # For odd numbers pencil size is not an integer
                cv2.circle(frame, (cX, cY), pencil_size // 2 + 0.5, pencil_color, -1)  # Draws a circle in the centroid - screen
                cv2.circle(screen, (cX, cY), pencil_size // 2 + 0.5, pencil_color, -1) # Draws a circle in the centroid - screen


# Advanced Function 2 - Using video stream as canvas
def videocanvas(frame):

    # Shows original frame
    frame_sized = cv2.resize(frame,(600,400))
    key = cv2.waitKey(1)
    new_background = screen

    if key == ord('s'):         # when 's' key pressed        
        # Resizes new background to the original screen size
        new_background = cv2.resize(frame, (screen.shape[1], screen.shape[0]))
        print("\n" + Fore.YELLOW + 'New frame'+ Style.RESET_ALL)
            
    elif key == ord('n'):       # when'n' key pressed opens new blank screen
        canvas = np.full((480, 640, 3),255, dtype=np.uint8)

        # Resizes new background to the original screen size
        new_background = cv2.resize(canvas, (screen.shape[1], screen.shape[0]))
        print("\n" + Fore.YELLOW + 'New canvas'+ Style.RESET_ALL)

    # Converts screen to grayscale.
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    # Applies a binary threshold to grayscale image.
    _, maskbinary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Inverts mask
    mask_inverted = cv2.bitwise_not(maskbinary)

    # Extracts the object (drawing) from the original window
    object = cv2.bitwise_and(screen, screen, mask=mask_inverted)

    # Combines object with new canvas
    screen = cv2.bitwise_and(new_background, new_background, mask=maskbinary) + object

    return frame_sized, key


# Visualization funtion defines visualization parameters and opens screen
def visualization(frame_sized,pencil_color):
    
    # Original image
    cv2.imshow('Original Image', cv2.flip(frame_sized,1))

    # Blank canvas
    cv2.imshow('Drawing', cv2.flip(screen,1))

    key = cv2.waitKey(1)

    # When certain keys are pressed, visualization parameters change
    if key == ord('r'):             # 'r' pressed
        pencil_color = (0, 0, 255)  # Red pencil
        print('Selected color ' + Fore.RED + 'red' + Style.RESET_ALL)

    elif key == ord('g'):           # 'g' pressed
        pencil_color = (0, 255, 0)  # Green pencil
        print('Selected color ' + Fore.GREEN + 'green' + Style.RESET_ALL)

    elif key == ord('b'):           # 'b' pressed
        pencil_color = (255, 0, 0)  # Blue pencil
        print('Selected color '+ Fore.BLUE +  'blue' + Style.RESET_ALL)

    elif key == ord('+'):           # Increases pencil size when '+' pressed
        pencil_size += 2
        print('Pencil size increased to: '+ Fore.YELLOW + str(pencil_size)+ Style.RESET_ALL)

    elif key == ord('-'):           # Decreases pencil size when '-' pressed
        pencil_size = max(1, pencil_size - 2)
        print('Pencil size decreased to: '+ Fore.YELLOW + str(pencil_size)+ Style.RESET_ALL)

    elif key == ord('c'):           # Clears screen and opens new canvas when 'c' pressed
        screen = np.full((480, 640, 3),255, dtype=np.uint8)
        print("\n" + Fore.YELLOW + 'New canvas'+ Style.RESET_ALL)

    elif key == ord('w'):           # Generates file name based on current data and time when 'w' pressed
        current_time = datetime.now().strftime("%a_%b_%d_%H:%M:%S_%Y")
        filename = f'drawing_{current_time}.png'

        cv2.imwrite(filename, screen)
        print("\n" + Fore.YELLOW + 'Saved canvas'+ Style.RESET_ALL)


#--------- MAIN FUNCTION ---------#

def main():

    limits = jsonfile()

    while True:
        # If a frame is not captured the code breaks
        ret, frame = cap.read()
        if not ret:
            break
        
        # Centroid function
        centroid(frame,limits,pencil_size,pencil_color)

        # Video stream as canvas function
        frame_sized, key = videocanvas(frame)

        # Visiualization function
        if key == ord('q'):            # when 'q' pressed quits program
            print ("\n" + Fore.RED + 'Program interrupted'+ Style.RESET_ALL)
            break
        else:
            visualization(frame_sized,pencil_color)


#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()
