#!/usr/bin/env python3
# Shebang line

# Universidade de Aveiro, ano letivo 2023/2024
# Programação de Sistemas Robóticos
# Trabalho nº2 - Augmented Reality Paint

# Maria Rodrigues, nº 102384
# Nuno Seabra, nº
# Ricardo Baptista, nº


#--------- IMPORT FUNCTIONS ---------#

from asyncio import sleep
from colorama import Fore, Style
import cv2
import json
import argparse
import numpy as np
from datetime import datetime
import pygame as pygame
from Atual.functions import applyMask,centroid_position,draw_shape,new_draw

#--------- INITIALIZATION ---------#

# Initializes video capture
capture = cv2.VideoCapture(0)

pencil_coords=(None,None)

# Defines blank canvas
#screen = np.full((512, 512, 3),255,dtype=np.uint8)

#--------- MAIN FUNCTION ---------#

def main():

    # Argparse description and arguments
    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=False, default='limits.json', help='provide the path to the .json file with the color data')
    parser.add_argument('-usp','--use_shake_prevention', action='store_true', help='Enable shake prevention')
    parser.add_argument('-um','--use_mouse', action='store_true', help='Use mouse position for drawing')
    args = parser.parse_args()

    #print('\n ' + 'Press SPACE to start drawing ...'+ '\n')

    # Loads color limitis from the JSON file
    with open(args.json, 'r') as file:
        limits=json.load(file)

     # boolean that determines if shake prevention is to be used or not
    if args.use_shake_prevention:
         usp = args['use_shake_prevention'] 
    else: 
         usp=False
    
    # boolean that determines if the mouse pointer is to be used or not
    if args.use_mouse:
         use_mouse = args['mouse'] 
    else: 
         use_mouse=False

    # list of all the draw moves done so far
    draw_moves = []


    # Calling global variables
    #global mode, pencil_color, screen, pencil_size, mouse_pos, prev_centroid,centroid,drawing,draw,o
    
    # setting up the video capture  
    capture = cv2.VideoCapture(0)
    _, frame = capture.read() # initial frame just to figure out proper window dimensions

    # dimensions for all windows
    scale = 0.6
    window_width = int(600 * scale)
    window_height = int(400 * scale)

      # continuing video capture setup
    camera_window = 'Camera capture'
    cv2.namedWindow(camera_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camera_window, (window_width, window_height))

    # setting up the window that shows the mask being applied
    mask_window = 'Masked capture'
    cv2.namedWindow(mask_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(mask_window, (window_width, window_height))

    drawing_window= 'Drawing Window'
    cv2.namedWindow(drawing_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(drawing_window, (window_width, window_height))

    # define positions of each window on screen (this way, they don't overlap)
    cv2.moveWindow(camera_window, 200, 100)
    cv2.moveWindow(mask_window, 1000, 100)
    cv2.moveWindow(drawing_window, 1000, 300)

    pencil_color = (0, 0, 255)
    pencil_size = 2 
    old_coords = (None,None)
    
    drawing = False                                 # Monitors if the user is drawing
    draw= False                                     # To stop drawing
    mode = 'circle'                                 # Sets the mode to circle, at first


    # Defines initial variables for color (red), pencil size and drawing mode
    pencil_color = (0, 0, 255)
    pencil_size = 2 
    mode = 'circle'
    global pencil_coords

    while True:
    
        # If a frame is not captured the code breaks
        ret, frame = capture.read()
        
        
        #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        low=(limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min'])
        print(low)
        high=(limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max'])
        print(high)
        #mask=cv2.inRange(frame, low,high)
        mask=frame
        

        pencil_position_frame = centroid_position(mask,pencil_color)

        print(pencil_position_frame)
        cv2.imshow(mask_window,pencil_position_frame)
        
        new_draw(old_coords,pencil_color,pencil_size,usp,screen)
        
        print(pencil_coords)
        sleep(1000)

        old_coords = pencil_coords

        print(old_coords)
        sleep(1000)

      
        # Draws a shape based on the drawing mode
        cv2.setMouseCallback(drawing_window, draw_shape(screen,pencil_color,mode))
        # shows initial frame
        cv2.imshow(camera_window,frame)
        # Shows blank canvas
        cv2.imshow(drawing_window,screen)
        #cv2.imshow('Drawing2', picture)

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
             o += 1

        elif key == ord('e'):           # Ellipse drawing mode     
             mode = 'ellipse'
             print('ellipse mode\n')

        elif key == ord('s'):           # Square drawing mode     
             mode = 'square'
             print('square mode\n')

        elif key== ord(' '):
            draw= not draw
            if draw:
                print('Drawing!\n')
            else:
                print('Program on hold...\n')
                

        elif key == ord('c'):
            # Clears screen and opens new canvas when 'c' pressed
            screen = np.full((window_width, window_height, 3),255)
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
