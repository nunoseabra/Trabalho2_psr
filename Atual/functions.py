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

def initialization():
    # Input Arguments
    parser = argparse.ArgumentParser(description='Ar Paint ')
    parser.add_argument('-j','--json',type = str, required= False , help='Full path to json file', default='limits.json')
    parser.add_argument('-usp','--use_shake_prevention', action='store_true', help='Use shake prevention mode')
    parser.add_argument('-ucc','--use_cam_mode', action='store_true', help='Use camera frame as canvas')
    parser.add_argument('-umm','--use_mouse_mode', action='store_true', help='Use mouse as pencil')
    args = vars(parser.parse_args())

    file_path = 'limits.json' if not args['json'] else args['json'] # Path for the json file
    usp = args['use_shake_prevention'] # Shake prevention mode
    ucm = args['use_cam_mode'] # Use live feed from the cam to be used as the canvas
    umm = args['use_mouse_mode'] # Use mouse as the pencil

    print('\nDrawing modes selected:')
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

def limitsRead(file_path):
    try:
        with open(file_path, 'r') as file:
            json_object = json.load(file)
            limits = json_object['limits']
            
    # if the file doesn't exist, send out an error message and quit
    except FileNotFoundError:
        sys.exit('The .json file doesn\'t exist.')

    return limits

def get_centroid(mask) :
    # find all contours (objects)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # if we detect objects, let's find the biggest one, make it green and calculate the centroid
    if contours:

        # find the biggest object
        contour = max(contours, key=cv2.contourArea)

        # make it green and other channels white
        for_green_obj = np.zeros(mask.shape, np.uint8)
        cv2.drawContours(for_green_obj, [contour], -1, 255, cv2.FILLED)
        for_green_obj = cv2.bitwise_and(mask, for_green_obj) # mkeep the pixeis that we want as green
        for_others = cv2.bitwise_xor(mask, for_green_obj) # the other pixels for null
        
        b = for_others
        g = mask
        r = for_others

        image_result = cv2.merge((b, g, r))

        # calculate centroid coordinates
        M = cv2.moments(contour)
        cX = int(M["m10"] / M["m00"]) if (M["m00"]!=0) else None
        cY = int(M["m01"] / M["m00"]) if (M["m00"]!=0) else None

        # draw small red cross to indicate the centroid point
        if cX: # it's enough to check either cX or cY, if one is None then both are None
            cv2.line(image_result, (cX-8, cY-8), (cX+8, cY+8), (0, 0, 255), 5)
            cv2.line(image_result, (cX+8, cY-8), (cX-8, cY+8), (0, 0, 255), 5)
    
    # if we don't detect any objects, we just show the mask as it is
    else:
        image_result = cv2.merge((mask, mask, mask))
        cX = None
        cY = None
        
    return cX,cY, image_result 

def key_press(key_input,canvas):
    global draw_color, pencil_thick

        # change color to Red
    if key_input=='r':
        draw_color = (0,0,255)
        print('Color changed to RED'+'\n')
        
        # change color to Green
    elif key_input=='g':
        draw_color = (0,255,0)
        print('Color changed to GREEN'+'\n')

        # change color to Blue
    elif key_input=='b':
        draw_color = (255,0,0)
        print('Color changed to BLUE'+'\n')

        # decrease pencil size
    elif key_input=='-':
        if pencil_thick > 0:
            pencil_thick -= 5
            print('Decreased pencil size to '+ str(pencil_thick)+'\n')

        # increase pencil size
    elif key_input=='+':
        if pencil_thick < 50:
            pencil_thick += 5
            print('Increased pencil size to '+ str(pencil_thick)+'\n')

        # save canvas 
    elif key_input=='w':
        date = datetime.now()
        formatted_date = date.strftime("%a_%b_%d_%H:%M:%S")
        name_canvas = 'drawing_' + formatted_date + '.png'
        name_canvas_colored = 'drawing_' + formatted_date + '_colored.jpg'
        cv2.imwrite(name_canvas, canvas)
        cv2.imwrite(name_canvas_colored, canvas)
        print('Your draw was saved!\n')

        # quit program
    elif key_input=='q':
        print('Program interrupted!\n')
        return False
    
    return True

def repaint(frame, figures):
    for step in figures:
        if step.type == "square":
            cv2.rectangle(frame,step.coord_origin,step.coord_final,step.color,step.thickness)
        
        elif step.type == "circle":
            difx = step.coord_final[0] - step.coord_origin[0]
            dify = step.coord_final[1] - step.coord_origin[1]
            radious = round(sqrt(difx**2 + dify**2))
            cv2.circle(frame,step.coord_origin,radious,step.color,step.thickness) 

        elif step.type == "ellipse":
            meanx = (step.coord_final[0] - step.coord_origin[0])/2
            meany = (step.coord_final[1] - step.coord_origin[1])/2
            center = (round(meanx + step.coord_origin[0]), round(meany + step.coord_origin[1]))
            axes = (round(abs(meanx)), round(abs(meany)))
            cv2.ellipse(frame,center,axes,0,0,360,step.color,step.thickness)
        
        elif step.type == "line":
            cv2.line(frame, step.coord_origin,step.coord_final, step.color,step.thickness)
        
        elif step.type == "dot":        
            cv2.circle(frame, step.coord_final, 1, step.color,step.thickness) 

def windowSetup(frame):
    # dimensions for all windows
    scale = 0.6
    window_width = int(frame.shape[1]* scale)
    window_height = int(frame.shape[0]* scale)

      # continuing video capture setup
    camera_window = 'Original window'
    cv2.namedWindow(camera_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camera_window, (window_width, window_height))

    # setting up the window that shows the mask being applied
    mask_window = 'Masked capture'
    cv2.namedWindow(mask_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(mask_window, (window_width, window_height))

    drawing_window= 'Drawing window'
    cv2.namedWindow(drawing_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(drawing_window, (window_width, window_height))

    # define positions of each window on screen (this way, they don't overlap)
    cv2.moveWindow(camera_window, 200, 100)
    cv2.moveWindow(mask_window, 1000, 100)
    cv2.moveWindow(drawing_window, 1000, 600)

    drawing_cache = np.full((window_height,window_width,3),255,dtype=np.uint8)
    

    return camera_window,mask_window,drawing_window,drawing_cache
     