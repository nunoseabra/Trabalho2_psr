#!/usr/bin/env python3
# Shebang line

# Universidade de Aveiro, ano letivo 2023/2024
# Programação de Sistemas Robóticos
# Trabalho nº2 - Augmented Reality Paint

# Maria Rodrigues, nº 102384
# Nuno Seabra, nº
# Ricardo Baptista, nº


#--------- IMPORT FUNCTIONS ---------#

import json
import argparse
import sys
from colorama import Fore, Style
import cv2
import numpy as np
from math import sqrt
from datetime import datetime



#--------- FUNCTIONS ---------#


# Function to initialize arguments and give information about selected modes
def initialization():
    # Input Arguments
    parser = argparse.ArgumentParser(description='Ar Paint ')
    parser.add_argument('-j','--json',type = str, required= False , help='Full path to json file', default='limits.json')
    parser.add_argument('-usp','--use_shake_prevention', action='store_true', help='Use shake prevention mode')
    parser.add_argument('-ucc','--use_cam_mode', action='store_true', help='Use camera frame as canvas')
    parser.add_argument('-umm','--use_mouse_mode', action='store_true', help='Use mouse as pencil')
    args = vars(parser.parse_args())

    file_path = 'limits.json' if not args['json'] else args['json']         # Path to JSON file
    usp = args['use_shake_prevention']                                      # Shake prevention mode
    ucm = args['use_cam_mode']                                              # Use video as canvas
    umm = args['use_mouse_mode']                                            # Use mouse as the pencil

    # Prints selected modes
    print('\n Drawing modes selected:')
    if usp:
        print('Use_shake_prevention')
    if ucm:
        print('Use_cam_mode')
    if umm:
        print('Use_mouse_mode')
    if (not usp)and (not ucm) and (not umm):
        print('Default')
    print()
    return file_path , usp, ucm,umm


# Function to get limits
def getLimits(file_path):
    try:
        with open(file_path, 'r') as file:
            json_object = json.load(file)
            limits = json_object['limits']
            
    # If there is no file, quits
    except FileNotFoundError:
        sys.exit('The .json file doesn\'t exist.')

    return limits


# Function to get centroid
def get_centroid(mask) :
    # Try to find contours in the limit range
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # If there are contours, selects the biggest and turns it green
    if contours:

        # Finds biggest contour
        contour = max(contours, key=cv2.contourArea)

        # Truns the object green
        for_green_obj = np.zeros(mask.shape, np.uint8)
        cv2.drawContours(for_green_obj, [contour], -1, 255, cv2.FILLED)
        for_green_obj = cv2.bitwise_and(mask, for_green_obj)
        for_others = cv2.bitwise_xor(mask, for_green_obj)           # Pixels from the rest of the image all turn the same colour
        
        # Red and blue pixels ignored
        b = for_others
        g = mask
        r = for_others

        # Final image after masks and main object turning green
        image_result = cv2.merge((b, g, r))

        # Centroid coordinates
        M = cv2.moments(contour)
        cX = int(M["m10"] / M["m00"]) if (M["m00"]!=0) else None
        cY = int(M["m01"] / M["m00"]) if (M["m00"]!=0) else None

        # Center cross in the centroid mark
        if cX:                                                      # Checks to see if cx is a number
            cv2.line(image_result, (cX-3, cY-3), (cX+3, cY+3), draw_color, 3)
            cv2.line(image_result, (cX+3, cY-3), (cX-3, cY+3), draw_color, 3)
    
    # iElse show mask as it is
    else:
        image_result = cv2.merge((mask, mask, mask))
        cX = None
        cY = None
        
    return cX,cY, image_result 


# Defines key functions to change color, size and format of the pencil 
def key_press(key_input,canvas):
    global draw_color, pencil_thick

    # If key is preesed:
    if key_input=='r':                              # Red
        draw_color = (0,0,255)
        print('Pencil is RED'+'\n')
        
    elif key_input=='g':                            # Green
        draw_color = (0,255,0)
        print('Pencil is GREEN'+'\n')

    elif key_input=='b':                            # Blue
        draw_color = (255,0,0)
        print('Pencil is BLUE'+'\n')

    elif key_input=='-':                            # Decrease pencil size
        pencil_thick=max(1,(pencil_thick-2))
        print('Decreased pencil size to '+ str(pencil_thick)+'\n')

    elif key_input=='+':                            # Increase pencil size
        pencil_thick=min(30,(pencil_thick+2))
        print('Increased pencil size to '+ str(pencil_thick)+'\n')

    elif key_input=='w':                            # Saves canva in dated file
        # Gets current date and time
        date = datetime.now()
        formatted_date = date.strftime("%a_%b_%d_%H:%M:%S")
        name_canvas = 'drawing_' + formatted_date + '.png'
        name_canvas_colored = 'drawing_' + formatted_date + '_colored.jpg'
        # Creates file
        cv2.imwrite(name_canvas, canvas)
        cv2.imwrite(name_canvas_colored, canvas)
        print('Your draw was saved!\n')

    elif key_input=='q':                            # Quits program
        print('Program interrupted!\n')
        return False
    
    return True


# Function to draw shapes
def shapesFunc(frame, figures):
    for step in figures:
        if step.type == "square":                                                                   # Draw squares
            cv2.rectangle(frame,step.coord_origin,step.coord_final,step.color,step.thickness)
        
        elif step.type == "circle":                                                                 # Draw circles
            difx = step.coord_final[0] - step.coord_origin[0]
            dify = step.coord_final[1] - step.coord_origin[1]
            radious = round(sqrt(difx**2 + dify**2))
            cv2.circle(frame,step.coord_origin,radious,step.color,step.thickness) 

        elif step.type == "ellipse":                                                                # Draw elipse
            meanx = (step.coord_final[0] - step.coord_origin[0])/2                                  # Mean for x coordinate
            meany = (step.coord_final[1] - step.coord_origin[1])/2                                  # Mean for y coordinate
            center = (round(meanx + step.coord_origin[0]), round(meany + step.coord_origin[1]))     # Defines center
            axes = (round(abs(meanx)), round(abs(meany)))
            cv2.ellipse(frame,center,axes,0,0,360,step.color,step.thickness)
        
        elif step.type == "line":                                                                   # Draw line
            cv2.line(frame, step.coord_origin,step.coord_final, step.color,step.thickness)
        
        elif step.type == "dot":                                                                    # Draw dot
            cv2.circle(frame, step.coord_final, 1, step.color,step.thickness) 
    

# Function to configure windows
def windowSetup(frame):
    # Window dimentions and scale
    scale = 0.6
    window_width = int(frame.shape[1]* scale)
    window_height = int(frame.shape[0]* scale)

    # Video capture
    camera_window = 'Original window'
    cv2.namedWindow(camera_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camera_window, (window_width, window_height))

    # Window with mask on
    mask_window = 'Masked capture'
    cv2.namedWindow(mask_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(mask_window, (window_width, window_height))

    # Drawing window
    drawing_window= 'Drawing window'
    cv2.namedWindow(drawing_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(drawing_window, (window_width, window_height))

    # define positions of each window on screen (this way, they don't overlap)
    cv2.moveWindow(camera_window, 200, 100)
    cv2.moveWindow(mask_window, 1000, 100)
    cv2.moveWindow(drawing_window, 1000, 600)

    drawing_cache = np.full((window_height,window_width,3),255,dtype=np.uint8)
    return camera_window,mask_window,drawing_window,drawing_cache


# Function to define squares   
def square(event,x,y,image):
    if event == cv2.EVENT_LBUTTONDOWN:  # For key mode  - key down, start point
        start_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:  # For key mode - key up, draws 
        end_point = (x, y)   
        cv2.rectangle(image, start_point, end_point, draw_color, 2)

    elif event == cv2.EVENT_MOUSEMOVE:  # For mouse mode
        image_copy=image.copy()
        cv2.rectangle(image_copy, start_point, (x, y), draw_color, 2)