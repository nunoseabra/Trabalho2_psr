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
from random import randint, shuffle
import sys
from colorama import Fore, Style
import cv2
import numpy as np
from math import sqrt
from datetime import datetime
#from functions import get_centroid, initialization, key_press, getLimits, shapesFunc, square, windowSetup, draw_color,pencil_thick,shake_limit


#--------- INITIALIZATION ---------#

draw_color = (0,0,255)
pencil_thick = 5
shake_limit = 100


#--------- CLASSES ---------#

class Shapes:
    # Defining shapes
    def __init__(self,type,origin,final,colour,thickness):
        self.type = type
        self.coord_origin = origin
        self.coord_final = final
        self.color = colour
        self.thickness = thickness

class Mouse:
    # Defining mouse
    def __init__(self):
        self.coords = (None,None)
        self.pressed = False

    def update_mouse(self,event,x,y,flags,param):
        self.coords = (x,y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pressed = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.pressed = False
                    

#--------- FREE PAINTING MODE FUNCTIONS ---------#


# Initial function to define argparser descriptiom and arguments
def init():
    # Argparser description
    parser = argparse.ArgumentParser(description='Augmented Reality Paint Test')
    # Argparser arguments
    parser.add_argument('-j','--json',type = str, required= False , help='Full path to json file', default='limits.json')
    parser.add_argument('-usp','--use_shake_prevention', action='store_true', help='Use shake prevention mode')
    parser.add_argument('-ucc','--use_cam_mode', action='store_true', help='Use camera frame as canvas')
    parser.add_argument('-umm','--use_mouse_mode', action='store_true', help='Use mouse as pencil')
    parser.add_argument('-utm','--use_test_mode', action='store_true', help='Paint a matrix by number')

    args = vars(parser.parse_args())

    # Initizalizing argparser arguments
    file_path = 'limits.json' if not args['json'] else args['json'] # JSON file path
    usp = args['use_shake_prevention']                              # Use shake prevention mode
    ucm = args['use_cam_mode']                                      # Use video as canvas
    umm = args['use_mouse_mode']                                    # Use mouse as pencil
    utm = args['use_test_mode']                                     # Paint by numbers

    # Mode description - modes used
    print('\n Drawing modes:')
    if usp:                                                         # If usp is active prints message
        print('Shake prevention mode')
    if ucm:                                                         # If ucm is active prints message
        print('Camera as canvas mode')
    if umm:                                                         # If umm is active prints message
        print('Mouse mode')
    if (not usp) and (not ucm) and (not umm):                       # If no mode is active let's user know default mode is active
        print('Default Mode')
    print()
    if utm:
        print('Paint by numbers test mode')                         # If utm is active prints message
    return file_path , usp, ucm, umm, utm


# Function to get RGB limits
def getLimits(file_path):
    try:
        with open(file_path, 'r') as file:                          # Open JSON file and get RGB limits
            json_object = json.load(file)
            limits = json_object['limits']
            
    except FileNotFoundError:                                       # If there is no file, program closes and prints message
        sys.exit('The .json file doesn\'t exist.')

    return limits


# Function to get centroid
def get_centroid(mask):
    global draw_color
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
    
    # If no contourns detected
    else:
        image_result = cv2.merge((mask, mask, mask))
        cX = 0
        cY = 0
        
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

    
# Function to divide image in a grid to paint and define color zones (a grid)
def getgrid(image):
    # Initizalizing grid
    h,w,_ = image.shape
    grid = np.zeros([h,w],dtype=np.uint8)
    grid[h-1,:] = 255
    grid[:,w-1] = 255
    
    # Initializing color numbers
    numbers_to_colors = [(0,0,255), (0,255,0), (255,0,0)]
    shuffle(numbers_to_colors)

    # Scaling and defining grid
    for y in range(0,h,int(h/3)):
        grid[y,:] = 255
    for x in range(0,w,int(w/4)):
        grid[:,x] = 255
    grid = cv2.bitwise_not(grid)

    # Gets contours
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours, numbers_to_colors


# Function to get the contours and associate each one with a retangular zone
def contours(original, contours, numbers):
    # Initialize color associacion 
    color = (255,255,255)

    for i in range(len(contours)):                              # For each zone (every contour represents a zone)
        c = contours[i]

        x,y,w,h = cv2.boundingRect(c)
        cX = int(x + w/2)
        cY = int(y + h/2)

        # Number the zones
        cv2.putText(original, str(numbers[i]), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return cv2.drawContours(original, contours, -1, color, 3)


# Function to attribute a color to a grid space and number
def colorswindow(numbers_to_colors, accuracy=None):
    # Initialize image
    bg = np.zeros([300,350,3],dtype=np.uint8)

    # Associates color to space
    for i in range(3):
        color = 'red' if numbers_to_colors[i]==(0,0,255) else ('green' if numbers_to_colors[i]==(0,255,0) else 'blue')
        cv2.putText(bg, str(i+1) + ' - ' + color, (50, 50+50*i), cv2.FONT_HERSHEY_SIMPLEX, 0.9, numbers_to_colors[i], 2)

    # Accuracu of the painting
    if accuracy!=None:
        cv2.putText(bg, 'Accuracy: ' + str(accuracy) + '%', (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
    
    return bg


# Function to calculate accuracy
def calc_accuracy(image, contours, zone_numbers, numbers_to_colors):
    # Initializes matrix pixels
    h,w,_ = image.shape
    total_pixels = h*w                                          # Total number of pixels
    right_pixels = 0                                            # Number of correctly painted pixels
    
    for i in range(len(contours)):                              # For each zone (every contour represents a zone)
        c = contours[i]                                         # Reads zone
        zone_number = zone_numbers[i]                           # Zone number, for that zone
        color = numbers_to_colors[zone_number-1]                # Zone color, for that zone

        # Corners of retangular zone
        minX = c[0][0][0]
        maxX = c[2][0][0]
        minY = c[0][0][1]
        maxY = c[1][0][1]

        _,_,depth = image.shape

        # Evalueates if the pixel was colored right
        for pixel_row in image[minY:maxY, minX:maxX, 0:depth]:
            for pixel in pixel_row:
                pixel = (pixel[0], pixel[1], pixel[2])           # Gets the color of the pixel
                right_pixels += 1 if pixel==color else 0         # If the color is right increments counter

    # Approval rate is calculated in %
    return int((right_pixels/total_pixels)*100)


#--------- PAINT BY NUMBERS RELATED FUNCTIONS ---------#

def create_canvas(grid_size, canvas_size):
    square_size = canvas_size // grid_size
    canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
    return canvas, square_size

def random_distribution(grid_size):
    color_mapping = [1, 2, 3]
    np.random.shuffle(color_mapping)
    colored_numbers = np.random.choice(color_mapping, size=(grid_size, grid_size), replace=True)
    return colored_numbers

def set_color_and_number(canvas, color, number, square_size, row, col):
    top_left = (col * square_size, row * square_size)
    bottom_right = ((col + 1) * square_size, (row + 1) * square_size)
    cv2.rectangle(canvas, top_left, bottom_right, color, -1)
    
    center_x = (top_left[0] + bottom_right[0]) // 2
    center_y = (top_left[1] + bottom_right[1]) // 2
    cv2.putText(canvas, str(number), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

def create_colored_matrix(grid_size, canvas_size):
    colored_canvas, square_size = create_canvas(grid_size, canvas_size)
    colored_numbers = random_distribution(grid_size)
    
    for i in range(grid_size):
        for j in range(grid_size):
            color = (0, 0, 255) if colored_numbers[i, j] == 1 else (0, 255, 0) if colored_numbers[i, j] == 2 else (255, 0, 0)
            set_color_and_number(colored_canvas, color, colored_numbers[i, j], square_size, i, j)

    return colored_canvas, colored_numbers

def create_grey_matrix(colored_numbers, grid_size, canvas_size):
    grey_canvas, square_size = create_canvas(grid_size, canvas_size)
    
    for i in range(grid_size):
        for j in range(grid_size):
            number = colored_numbers[i, j]
            set_color_and_number(grey_canvas, (128, 128, 128), number, square_size, i, j)
            
            # Add black lines around the square
            top_left = (j * square_size, i * square_size)
            bottom_right = ((j + 1) * square_size, (i + 1) * square_size)
            cv2.rectangle(grey_canvas, top_left, bottom_right, (0, 0, 0), 1)

    return grey_canvas


#--------- MAIN FUNCTION ---------#

def main():
    global draw_color, pencil_thick,shake_limit
 
    # Calling initialization function
    file,usp,ucm,umm,utm = init()

    # Initializing drawing
    draws = []
    draw_mode = False

    # Printing usage information
    print('To activate/deactivate modes:\n')
    print('Shake prevention - press '+Fore.CYAN+ 'n'+ Style.RESET_ALL + ' \n')
    print('Camera as canvas - press '+Fore.CYAN+ 'l'+ Style.RESET_ALL + ' \n')
    print('Mouse mode - press '+Fore.CYAN+ 'm'+ Style.RESET_ALL + ' \n')
    print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'd'+ Style.RESET_ALL + ' to pause!\n')
    
    # Calling limits function
    limits = getLimits(file) 

    # Open video and windows
    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    camera_window, mask_window, drawing_window, drawing_cache = windowSetup(frame)

    # Showing windows
    cv2.imshow( camera_window,frame)
    cv2.imshow(drawing_window,drawing_cache)

    # Getting limints
    low_limits = (limits['B']['min'], limits['G']['min'], limits['R']['min'])
    high_limits = (limits['B']['max'], limits['G']['max'], limits['R']['max'])

    # Reading mouse callback
    mouse = Mouse()
    cv2.setMouseCallback(drawing_window, mouse.update_mouse)
    
    while True:

        #----------- INITIALIZING MAIN

        ret,frame = capture.read()
        
        # Flip frame to get accurate image for easy access
        frame_flip = cv2.flip(frame, 1)
        cv2.imshow(camera_window,frame_flip)

        #----------- FREE DRAWING MODE

        # Activating camera mode
        if ucm:  
            drawing_canvas = frame_flip
        else:
            drawing_canvas = drawing_cache
        
        # Frames and showing mask
        frame_mask = cv2.inRange(frame_flip, low_limits, high_limits)
        frame_wMask = cv2.bitwise_and(frame_flip,frame_flip, mask = frame_mask)
        cv2.imshow(mask_window,frame_wMask)
        
        # Getting centroid
        cx,cy,frame_centroid= get_centroid(frame_mask)
        cv2.imshow( mask_window, frame_centroid)

        # Defining use mouse mode usage
        if not umm:                                         # Not using mouse mode
            cx,cy,frame_test = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            image_copy=drawing_canvas.copy()
            try:
                cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                cv2.imshow(drawing_window,image_copy)
                
            except: (cx,cy)==(None,None)                    # If coordenates are none type, stops
        else:                                               # Using mouse mode
            cx = mouse.coords[0]
            cy = mouse.coords[1]
            
            if cx:                                          # If cx is not none, draws
                image_copy=drawing_canvas.copy()
                cv2.line(image_copy, (cx-5, cy-5), (cx+5, cy+5), (0, 0, 255), 5)
                cv2.line(image_copy, (cx+5, cy-5), (cx-5, cy+5), (0, 0, 255), 5)
                cv2.imshow(drawing_window,image_copy)

        #----------- TEST MODE

        # Open Test Mode Window
        if utm:
            cv2.destroyAllWindows()

            # Creating matrix for test
            grid_size = 5
            canvas_size = 500

            # Generating both colored and correspondent grey matrix
            colored_canvas, colored_numbers = create_colored_matrix(grid_size, canvas_size)
            drawing_window = create_grey_matrix(colored_numbers, grid_size, canvas_size)

            # Showing grey matrix 
            cv2.imshow("Grey Matrix", image_copy)
            stop = str(chr(cv2.waitKey(1)))

            # Ending the test
            if stop == 'q':
                print('The test has ended!')
                # Showing correct matrix
                cv2.imshow("Colored Matrix", colored_canvas)

            # Drawing and painting matrix
            cx,cy,frame_test = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            image_copy=drawing_canvas.copy()

            try:
                cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                cv2.imshow(drawing_window,image_copy)
                
            except: (cx,cy)==(None,None)                    # If coordenates are none type, stops

        

        #----------- FREE DRAWING MODE

        # Activating camera mode
        if ucm:  
            drawing_canvas = frame_flip
        else:
            drawing_canvas = drawing_cache
        
        # Frames and showing mask
        frame_mask = cv2.inRange(frame_flip, low_limits, high_limits)
        frame_wMask = cv2.bitwise_and(frame_flip,frame_flip, mask = frame_mask)
        cv2.imshow(mask_window,frame_wMask)
        
        # Getting centroid
        cx,cy,frame_centroid= get_centroid(frame_mask)
        cv2.imshow( mask_window, frame_centroid)

        # Defining use mouse mode usage
        if not umm:                                         # Not using mouse mode
            cx,cy,frame_test = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            image_copy=drawing_canvas.copy()
            try:
                cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                cv2.imshow(drawing_window,image_copy)
                
            except: (cx,cy)==(None,None)                    # If coordenates are none type, stops
        else:                                               # Using mouse mode
            cx = mouse.coords[0]
            cy = mouse.coords[1]
            
            if cx:                                          # If cx is not none, draws
                image_copy=drawing_canvas.copy()
                cv2.line(image_copy, (cx-5, cy-5), (cx+5, cy+5), (0, 0, 255), 5)
                cv2.line(image_copy, (cx+5, cy-5), (cx-5, cy+5), (0, 0, 255), 5)
                cv2.imshow(drawing_window,image_copy)

        #----------- TEST MODE

        # Open Test Mode Window
        if utm:
            cv2.destroyAllWindows()

            # Creating matrix for test
            grid_size = 5
            canvas_size = 500

            # Generating both colored and correspondent grey matrix
            colored_canvas, colored_numbers = create_colored_matrix(grid_size, canvas_size)
            drawing_window = create_grey_matrix(colored_numbers, grid_size, canvas_size)

            # Showing grey matrix 
            cv2.imshow("Grey Matrix", drawing_window)
            stop = str(chr(cv2.waitKey(1)))

            # Ending the test
            if stop == 'q':
                print('The test has ended!')
                # Showing correct matrix
                cv2.imshow("Colored Matrix", colored_canvas)

            # Drawing and painting matrix
            cx,cy,frame_test = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            drawing_window=drawing_canvas.copy()

            try:
                cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                cv2.imshow(drawing_window,image_copy)
                
            except: (cx,cy)==(None,None)                    # If coordenates are none type, stops


        #----------- ACCURACY OF TEST MODE


        # Capture the user's drawing from the screen
        user_drawing = cv2.captureScreen(region=(cx, cy, canvas_size))  # Adjust the region to capture the drawing area

        # Convert the captured image to grayscale
        user_drawing_gray = cv2.cvtColor(user_drawing, cv2.COLOR_BGR2GRAY)

        # Ensure the dimensions match (resize if necessary)
        user_drawing_gray = cv2.resize(user_drawing_gray, (user_drawing.shape[1], user_drawing.shape[0]))

        # Threshold both images
        _, user_binary = cv2.threshold(user_drawing_gray, 1, 255, cv2.THRESH_BINARY)
        _, initial_binary = cv2.threshold(colored_canvas, 1, 255, cv2.THRESH_BINARY)

        # Calculate pixel-wise difference
        difference = cv2.bitwise_xor(user_binary, initial_binary)

        # Accuracy %
        total_pixels = initial_binary.size
        differing_pixels = cv2.countNonZero(difference)
        accuracy = 100 * (1 - differing_pixels / total_pixels)

        print("Accuracy: {:.2f}%".format(accuracy))


        #----------- READING INSTRUCTIONS AND DRAWING

        # Reads key
        k = cv2.waitKey(1)
        key = str(chr(k))

        # Safety measure if key is not pressed
        if not key_press(key,drawing_canvas): 
            break
        
        # If key pressed: 
        if key == "p":                                      # Alternates between drawing mode
            draw_mode = not draw_mode
            (prev_cx,prev_cy) = (None,None)

            if draw_mode:
                print('Back to drawing...\n')

            else: 
                print('Drawing paused...\n')
            
        elif key == 'c':                                    # Clears canvas
            draws = []
            drawing_canvas.fill(255)
            prev_cx,prev_cy = cx,cy
            print('New canvas\n')

        elif key == " ":                                    # Begins test
            draw_mode= True
            print('\n Drawing mode started! \n')

        elif key == "m":                                    # Alternates between having or not mouse mode
            umm= not umm
            print('Mouse mode: '+ str(umm)+'\n')

        elif key == "n":                                    # Alternates between having or not shake prevention mode
            usp= not usp
            print('Shake prevention mode: '+ str(usp)+'\n')

        elif key == "l":                                    # Alternates between having or not canvas mode
            ucm= not ucm
            print('Camera as canvas mode: '+ str(ucm)+'\n')
        
        # If drawing mode is active
        if draw_mode :
            if (cx,cy) != (None,None): # If coordenates are different to none type
                
                if key == "s":                                                                  # If 's' pressed draws square
                    draws[-1] = (Shapes("square",(cX,cY),(cx,cy),draw_color,pencil_thick))  
                    print('Square draw\n')
                        
                elif key == "o":                                                                # If 'o' pressed draws circle
                    draws[-1] = (Shapes("circle",(cX,cY),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Circle draw\n')

                elif key == "e":                                                                # If 'e' pressed draws ellipse
                    image_copy=drawing_canvas.copy()
                    
                    draws[-1] = (Shapes("ellipse",(cX,cY),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Ellipse draw\n')

                elif key == 'c':                                                                # If 'c' pressed cleares canvas
                    draws = []
                    drawing_canvas.fill(255)
                    prev_cx,prev_cy = cx,cy
                    print('New canvas\n')

                else: # If not in drawing mode
                    try:
                        if usp and (prev_cx,prev_cy) != (None,None):                            # If use shake prevention mode
                            diffX = abs(prev_cx - cx)
                            diffY = abs(prev_cy - cy)

                            if diffX>shake_limit or diffY>shake_limit:                          # If distance between points is bigger than shake limits, draws dot
                                draws.append(Shapes("dot",(0,0),(prev_cx,prev_cy),draw_color,pencil_thick))

                            else:                                                               # Draws line if distance is acceptable
                                draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))

                        elif (prev_cx,prev_cy) != (None,None):                                  # Draws line
                                draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))

                    except:
                        prev_cx, prev_cy = cx,cy                                                # Except if coordenates don't change

                # Reads and saves previous points
                if k == 0xFF:
                    cX,cY = cx,cy
                    prev_cx,prev_cy = cx,cy

            # Calling shapes function        
            shapesFunc(drawing_canvas,draws)
        
        # Shows windows
        cv2.imshow(camera_window,drawing_canvas)

    capture.release()
    


#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()