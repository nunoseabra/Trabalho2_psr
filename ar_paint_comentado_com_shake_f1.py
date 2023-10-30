#!/usr/bin/env python3
# Shebang line

# Universidade de Aveiro, ano letivo 2023/2024
# Programação de Sistemas Robóticos
# Trabalho nº2 - Augmented Reality Paint

# Maria Rodrigues, nº 102384
# Nuno Seabra, nº
# Ricardo Baptista, nº


#--------- IMPORT FUNCTIONS ---------#

from colorama import Fore, Style
import cv2
import json
import argparse
import numpy as np
from datetime import datetime
import pygame as pygame

#--------- INITIALIZATION ---------#

# Initializes video capture
cap = cv2.VideoCapture(0)

# Global variables
drawing = False                                 # Monitors if the user is drawing 
mode = 'circle'                                 # Sets the mode to circle, at first

# Initializing drawing-shapes variables
start_point = (0, 0)
end_point = (0, 0) 
prev_centroid = None
centroid = (0,0)
mouse_pos = (0,0)

# Defines initial variables for color (red), pencil size and drawing mode
pencil_color = (0, 0, 255)
pencil_size = 2 
mode = 'circle'

# Defines blank canvas
screen = np.zeros((512, 512, 3), dtype=np.uint8)


#--------- FUNCTIONS ---------#

#----- Advanced feature 3
# Function to draw shapes in the canva
def draw_shape(event,x,y,flags, param):
    # Calling global variables
    global mode,drawing,start_point,end_point,screen

    # The function starts when the button is pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True                          # Drawing flag turns true
        start_point = (x, y)
        
    elif event == cv2.EVENT_MOUSEMOVE:          # If the mouse moves while pressed
        if drawing:
            if mode == 'circle':                # Circle mode
                image_copy =screen.copy()
                radius = int(np.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2))
                cv2.circle(image_copy, start_point, radius, pencil_color, 2)
                cv2.imshow("Drawing1", image_copy)

            elif mode == 'rectangle':           # Rectangle mode
                image_copy =screen.copy()
                cv2.rectangle(image_copy, start_point, (x, y), pencil_color, 2)
                cv2.imshow("Drawing1", image_copy)
            
            elif mode == 'ellipse':
                image_copy =image.copy()
                # Calcule o tamanho da elipse
                a = abs(x - start_point[0])
                b = abs(y - start_point[1])
                # Desenhe a elipse
                cv2.ellipse(image_copy, start_point, (a, b), 0, 0, 360, pencil_color, 2)
                cv2.imshow("F3", image_copy)

    # Button no longer pressed - program ends and defines the radious based on end point
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)

        if mode == 'circle':                    # Ends circle mode
            radius = int(np.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2))
            cv2.circle(screen, start_point, radius, pencil_color, 2)

        elif mode == 'rectangle':               # Ends rectangle mode
            cv2.rectangle(screen, start_point, end_point, pencil_color, 2)


#--------- MAIN FUNCTION ---------#

def main():

    # Argparse description and arguments
    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('--use_shake_prevention', action='store_true', help='Enable shake prevention')
    parser.add_argument('--use_mouse', action='store_true', help='Use mouse position for drawing')
    args = parser.parse_args()

    print('\n ' + 'Ready to Draw ...'+ '\n')

    # Loads color limitis from the JSON file
    with open(args.json, 'r') as file:
        limits=json.load(file)

    # Calling global variables
    global mode, pencil_color, screen
    
    if args.use_mouse: #If the user chooses to use mouse to test
        pygame.init()
        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Drawing App")
        mouse_pos = (0, 0)
    else:
        screen = np.full((480, 640, 3), 255, dtype=np.uint8)
        event = None

    # Defines blank canvas
    picture= np.full((480, 640, 3),255, dtype=np.uint8)
    
    while True:

        # If a frame is not captured the code breaks
        ret, frame = cap.read()
        if not ret:
            break
        
        # Image converted to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detects color based on JSON file limits
        mask = cv2.inRange(hsv, (limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']),
                       (limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']))

        # Finds the contours of the largest object in the mask area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #----- Advanced feature 1
        # Mouse mode conditions
        if args.use_mouse:                      #Using mouse mode
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    pass
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
        else:                                   # Using normal mode - Calculates centroid
            if contours:
                # If contours are found, the largest contour is the one with the biggest area
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
                
                # If contour is not zero, calculate centroid
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    centroid = (cX,cY)
                    # Draws centroid in the original image with a red cross
                    cv2.drawMarker(frame, (cX, cY), pencil_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)

                    # Uses the center of the image to paint canvas
                    if pencil_size % 2 == 0:
                        cv2.circle(frame, (cX, cY), pencil_size // 2, pencil_color, -1)
                        cv2.circle(screen, (cX, cY), pencil_size // 2, pencil_color, -1)
                    else: 
                        cv2.circle(frame, (cX, cY), pencil_size // 2, pencil_color, -1)
                        cv2.circle(screen, (cX, cY), pencil_size // 2, pencil_color, -1)

        
        if prev_centroid and args.use_shake_prevention:         # The program was already running and checks for shake in the centroid
            # Calculate the distance between the previous and current centroids
            distance = np.linalg.norm(np.array(prev_centroid) - np.array(centroid))

            # Define a threshold for shake prevention (you can adjust this)
            shake_threshold = 10

            if distance > shake_threshold:
                # If shake is detected, draw a single point
                cv2.circle(screen, pencil_color, pencil_size, centroid)
            else:
                # Draw a line between the previous and current centroids
                cv2.line(screen, pencil_color, pencil_size, prev_centroid, centroid)
        else:
            # Draw a point 
            cv2.circle(screen, pencil_color, pencil_size, centroid)

        prev_centroid = centroid
        cv2.imshow('Drawing 3', screen)

        # Shows initial frame
        #frame_sized=cv2.resize(frame,(600,400))
        
        # Draws a shape based on the drawing mode
        cv2.setMouseCallback("Drawing1", draw_shape)
       
        # Shows initial frame
        cv2.imshow('Original Image', cv2.flip(frame,1))

        # Shows blank canvas
        cv2.imshow('Drawing1',screen)
        cv2.imshow('Drawing2', picture)

        # If a key is pressed, reads key
        key=cv2.waitKey(1)

        if key == ord('r'):
             pencil_color = (0, 0, 255)  # Red pencil selected
             print('Selected color to ' + Fore.RED + 'red\n' + Style.RESET_ALL)

        elif key == ord('g'):
            pencil_color = (0, 255, 0)  # Green pencil selected
            print('Selected color to ' + Fore.GREEN + 'green\n' + Style.RESET_ALL)

        elif key == ord('b'):
            pencil_color = (255, 0, 0)  # Blue pencil selected
            print('Selected color to '+ Fore.BLUE +  'blue\n' + Style.RESET_ALL)

        elif key == ord('+'):           # Increases pencil size when '+' is pressed
            pencil_size += 2
            print('Pencil size increased to: '+ Fore.YELLOW + str(pencil_size)+ '\n' + Style.RESET_ALL)

        elif key == ord('-'):           # Decreases pencil size when '-' is pressed
            pencil_size = max(1, pencil_size - 2)
            print('Pencil size decreased to: '+ Fore.YELLOW + str(pencil_size)+ '\n' + Style.RESET_ALL)

        elif key == ord('o'):           # Circle drawing mode       
             mode = 'circle'
             print('circle mode\n')

        elif key == ord('e'):           # Ellipse drawing mode     
             mode = 'ellipse'
             print('ellipse mode\n')

        elif key == ord('s'):           # Square drawing mode     
             mode = 'square'
             print('square mode\n')

        elif key == ord('c'):
            # Clears screen and opens new canvas when 'c' pressed
            picture = np.full((480, 640, 3),255, dtype=np.uint8)
            print( Fore.YELLOW + 'New canvas\n'+ Style.RESET_ALL)

        elif key == ord('w'):
             # Generates file name based on current data and time when 'w' pressed
            current_time = datetime.now().strftime("%a_%b_%d_%H:%M:%S_%Y")
            filename = f'drawing_{current_time}.png'

            cv2.imwrite(filename, screen)
            print(Fore.YELLOW + 'Saved canvas\n'+ Style.RESET_ALL)

        elif key == ord('q'):
            # Quits program when "q" is pressed
            print ( Fore.RED + 'Program interrupted\n'+ Style.RESET_ALL)
            cv2.destroyAllWindows()
            break

#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()
