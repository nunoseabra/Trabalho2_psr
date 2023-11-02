#!/usr/bin/env python3
# Shebang line

# Universidade de Aveiro, ano letivo 2023/2024
# Programação de Sistemas Robóticos
# Trabalho nº2 - Augmented Reality Paint

# Maria Rodrigues, nº 102384
# Nuno Seabra, nº 102889
# Ricardo Baptista, nº 40170


#--------- IMPORT FUNCTIONS ---------#

import json
import argparse
from random import randint, shuffle
import sys
from colorama import Fore, Style
import cv2 
import pyautogui
import numpy as np
from math import sqrt
from datetime import datetime
#from functions import get_centroid, initialization, key_press, getLimits, shapesFunc, square, windowSetup, draw_color,pencil_thick,shake_limit


#--------- INITIALIZATION ---------#

# global vars
draw_color = (0,0,255)
pencil_thick = 5
shake_limit = 50


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
    parser.add_argument('-ucm','--use_cam_mode', action='store_true', help='Use camera frame as canvas')
    parser.add_argument('-umm','--use_mouse_mode', action='store_true', help='Use mouse as pencil')
    parser.add_argument('-utm','--use_test_mode', action='store_true', help='Paint a matrix by number')
    parser.add_argument('-ufm','--use_figure_mode', action='store_true', help='Draw figures')

    args = vars(parser.parse_args())

    # Initizalizing argparser arguments
    file_path = 'limits.json' if not args['json'] else args['json'] # JSON file path
    usp = args['use_shake_prevention']                              # Use shake prevention mode
    ucm = args['use_cam_mode']                                      # Use video as canvas
    umm = args['use_mouse_mode']                                    # Use mouse as pencil
    utm = args['use_test_mode']  
    ufm = args['use_figure_mode']                                    # Paint by numbers

    # Mode description - modes used
    print(Fore.CYAN+'\nDrawing modes:'+ Style.RESET_ALL)
    if usp:                                                         # If usp is active prints message
        print(Fore.CYAN+'-Shake prevention mode'+ Style.RESET_ALL)
    if ucm:                                                         # If ucm is active prints message
        print(Fore.CYAN+'-Camera as canvas mode'+ Style.RESET_ALL)
    if umm:                                                         # If umm is active prints message
        print(Fore.CYAN+'-Mouse mode'+ Style.RESET_ALL)
    if utm:
        print(Fore.CYAN+'-Paint by numbers test mode'+ Style.RESET_ALL)                         # If utm is active prints message
    if ufm:
        print(Fore.CYAN+'-Draw figures mode'+ Style.RESET_ALL)                                  # If ufm is active prints message
    if not(usp) and not (ucm)and not (umm) and not (utm) and not (ufm):
        print(Fore.CYAN+'-Default'+ Style.RESET_ALL)                                                      
    print()
    return file_path , usp, ucm, umm, utm,ufm

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
    global draw_color, pencil_thick,mode

    # If key is preesed:
    if key_input=='r':                              # Red
        draw_color = (0,0,255)
        print('Pencil is '+Fore.RED+'RED'+Style.RESET_ALL+'\n')
        
    elif key_input=='g':                            # Green
        draw_color = (0,255,0)
        print('Pencil is '+Fore.GREEN+'GREEN'+Style.RESET_ALL+'\n')

    elif key_input=='b':                            # Blue
        draw_color = (255,0,0)
        print('Pencil is '+Fore.BLUE + 'BLUE'+Style.RESET_ALL+'\n')

    elif key_input=='-':                            # Decrease pencil size
        pencil_thick=max(1,(pencil_thick-2))
        print('Decreased pencil size to '+Fore.CYAN+ str(pencil_thick)+Style.RESET_ALL+'\n')

    elif key_input=='+':                            # Increase pencil size
        pencil_thick=min(30,(pencil_thick+2))
        print('Increased pencil size to '+ Fore.CYAN+ str(pencil_thick)+Style.RESET_ALL+'\n')

    elif key_input == "o":                                                                # If 'o' pressed draws circle
        mode='circle'
        print(Fore.CYAN+'Circle\n'+Style.RESET_ALL)

    elif key_input == "e":                                                                # If 'e' pressed draws ellipse
        mode='ellipse'
        print(Fore.CYAN+'Ellipse\n'+Style.RESET_ALL)    

    elif key_input == "s":                                                                # If 'e' pressed draws square
        mode='square'
        print(Fore.CYAN+'Square\n'+Style.RESET_ALL)   

    elif key_input=='w':                            # Saves canva in dated file

        # Gets current date and time
        date = datetime.now()
        formatted_date = date.strftime("%a_%b_%d_%H:%M:%S")
        name_canvas = 'drawing_' + formatted_date + '.png'
        name_canvas_colored = 'drawing_' + formatted_date + '_colored.jpg'

        # Creates file
        cv2.imwrite(name_canvas, canvas)
        cv2.imwrite(name_canvas_colored, canvas)

        print(Fore.GREEN+'Your draw was saved!\n'+Style.RESET_ALL)

    elif key_input=='q':                            # Quits program
        print(Fore.RED+'Program interrupted!\n'+Style.RESET_ALL)

        return False
    
    return True

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
    
# Function to draw shapes
def shapesFunc(frame, figures):
    for figure in figures:
       
        if  figure.type == "line":                                                                   # Draw line
            cv2.line(frame, figure.coord_origin,figure.coord_final, figure.color,figure.thickness)
        
        elif figure.type == "dot":                                                                    # Draw dot
            cv2.circle(frame, figure.coord_final, 1, figure.color,figure.thickness) 
    return frame

def draw_shape(event,x,y,flags, param):
    global mode,draw_color,image,drawing,start_point,end_point,drawing_shapes
    
    
    if event == cv2.EVENT_LBUTTONDOWN:                             # sets start point position to draw our shape
        drawing = True
        start_point = (x, y)
        
    elif event == cv2.EVENT_MOUSEMOVE:                             #gives position feedback
        if drawing:
            if mode == 'circle':
                image_copy =image.copy()
                radius = int(np.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2))
                cv2.circle(image_copy, start_point, radius, draw_color, 2)
                cv2.imshow(drawing_shapes, image_copy)

            elif mode == 'square':
                image_copy =image.copy()
                cv2.rectangle(image_copy, start_point, (x, y), draw_color, 2)
                cv2.imshow(drawing_shapes, image_copy)
            
            elif mode == 'ellipse':
                image_copy =image.copy()
                # Calcule o tamanho da elipse
                a = abs(x - start_point[0])
                b = abs(y - start_point[1])
                # Desenhe a elipse
                cv2.ellipse(image_copy, start_point, (a, b), 0, 0, 360, draw_color, 2)
                cv2.imshow(drawing_shapes, image_copy)

            elif mode == 'break': #to cancel shape
                pass

    elif event == cv2.EVENT_LBUTTONUP: # draw shape when mouse button is up
        drawing = False
        end_point = (x, y)
        if mode == 'circle':
            radius = int(np.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2))
            cv2.circle(image, start_point, radius, draw_color, 2)

        elif mode == 'square':
            cv2.rectangle(image, start_point, end_point, draw_color, 2)

        elif mode == 'ellipse':
            #image_copy = image.copy()
            a = abs(end_point[0] - start_point[0])
            b = abs(end_point[1] - start_point[1])
            cv2.ellipse(image, start_point, (a, b), 0, 0, 360, draw_color, 2)
        elif mode == 'break':
                mode='circle'
        
    

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
    file,usp,ucm,umm,utm ,figure= init()

    # Initializing drawing
    draws = []
    draw_mode = False
     
    if figure:
        # Printing usage information
        print('Press '+ Fore.CYAN + 'c'+Style.RESET_ALL + ' to draw circles, '+Fore.CYAN+ 's'+ Style.RESET_ALL + ' to draw squares and '+Fore.CYAN+ 'e'+ Style.RESET_ALL + ' to draw ellipses!\n')
        print('To change color press '+ Fore.RED + 'r'+Style.RESET_ALL + ' for RED, '+Fore.GREEN+ 'g'+ Style.RESET_ALL + ' for GREEN and '+Fore.BLUE+ 'b'+ Style.RESET_ALL + ' for BLUE!\n')
        print('To clear canvas press '+ Fore.CYAN + 'c '+Style.RESET_ALL + '!\n')
        print('To cancel shape press '+ Fore.CYAN + 'k '+Style.RESET_ALL + '!\n')
        print('To save your draw press '+ Fore.CYAN + 'w '+Style.RESET_ALL + '!\n')
        print('To quit press '+ Fore.CYAN + 'q '+Style.RESET_ALL + '!\n')

        global mode,image,drawing,start_point,end_point,drawing_shapes #variaveis globais para o modo shapes

        mode = 'circle'  # Inicialmente, o modo é definido para círculo
        start_point = (0, 0)
        end_point = (0, 0)
        image=np.full((700, 1000,3),0, dtype=np.uint8)
        drawing=False

        drawing_shapes='windowww'
        cv2.namedWindow(drawing_shapes)
        cv2.resizeWindow(drawing_shapes, (1000, 700))
        cv2.moveWindow(drawing_shapes, 500, 200)

        while True:
            

            cv2.setMouseCallback(drawing_shapes, draw_shape)   #desenha a figura selecionada com recurso ao mouse  
            cv2.imshow(drawing_shapes,image)

            # Reads key
            k = cv2.waitKey(1) & 0xFF
            key = str(chr(k))

            if key=='c':          #New canvas for shapes
                image.fill(0)
                print(Fore.YELLOW+'New canvas\n'+Style.RESET_ALL)

            elif key=='k':        #cancel shape
                mode='break'
                print(Fore.YELLOW+'Canceled...back to circle mode\n'+Style.RESET_ALL)

            # if key pressed is q, break the loop
            elif not key_press(key,image): 
                break
                  
    else:
        # Printing usage information
        print('To activate/deactivate modes:\n')
        print('Shake prevention - press '+Fore.CYAN+ 'n'+ Style.RESET_ALL + ' \n')
        print('Camera as canvas - press '+Fore.CYAN+ 'l'+ Style.RESET_ALL + ' \n')
        print('Mouse mode - press '+Fore.CYAN+ 'm'+ Style.RESET_ALL + ' \n')
        print('To change color press '+ Fore.RED + 'r'+Style.RESET_ALL + ' for RED, '+Fore.GREEN+ 'g'+ Style.RESET_ALL + ' for GREEN and '+Fore.BLUE+ 'b'+ Style.RESET_ALL + ' for BLUE!\n')
        print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'p'+ Style.RESET_ALL + ' to pause!\n')
        print('To clear canvas press '+ Fore.CYAN + 'c '+Style.RESET_ALL + '!\n')
        print('To save your draw press '+ Fore.CYAN + 'w '+Style.RESET_ALL + '!\n')
        print('To quit press '+ Fore.CYAN + 'q '+Style.RESET_ALL + '!\n')


        # Calling limits function
        limits = getLimits(file) 

        # Open video and windows
        capture = cv2.VideoCapture(0)
        _, frame = capture.read()
    
        # Getting limints
        low_limits = (limits['B']['min'], limits['G']['min'], limits['R']['min'])
        high_limits = (limits['B']['max'], limits['G']['max'], limits['R']['max'])

        camera_window, mask_window, drawing_window, drawing_cache = windowSetup(frame) #windows setup plus canvas for free drawing
    
        # Showing windows
        cv2.imshow(camera_window,frame)
        cv2.imshow(drawing_window,drawing_cache)

        if utm: # Function 4 - test mode
                
            # Creating matrix for test
            grid_size = 5
            canvas_size = 500
                
            # Generating both colored and correspondent grey matrix
            colored_canvas, colored_numbers = create_colored_matrix(grid_size, canvas_size)
            matrix = create_grey_matrix(colored_numbers, grid_size, canvas_size)
                
            # Showing grey matrix 
            cv2.imshow(drawing_window, matrix)
            stop = str(chr(cv2.waitKey(1)& 0xFF))      

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

            # Setting our canvas
            if ucm:  
                drawing_canvas = frame_flip #for camera as canvas mode
            elif utm:
                drawing_canvas = matrix #for function 4 - grid
            else:
                drawing_canvas = drawing_cache #fro free drawing

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

                try:  #draw cross marker to have feedback of position where we painting
                    cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                    cv2.imshow(drawing_window,image_copy)
                    
                except: (cx,cy)==(None,None)                    # If coordenates are none type, stops
            else:                                               # Using mouse mode
                cx = mouse.coords[0]
                cy = mouse.coords[1]
                
                if cx:                                          # If x is not none, draws
                    image_copy=drawing_canvas.copy()
                    cv2.line(image_copy, (cx-5, cy-5), (cx+5, cy+5), draw_color, 5)
                    cv2.line(image_copy, (cx+5, cy-5), (cx-5, cy+5), draw_color, 5)
                    cv2.imshow(drawing_window,image_copy)

            #----------- TEST MODE

            # Open Test Mode Window
            if utm:
                
                # Fecha todas as janelas, exceto a drawing_window"
                #cv2.destroyAllWindows()
                #cv2.imshow(drawing_window, matrix)  # Exibe a janela específica que se deseja manter aberta

                # Ending the test
                if stop == 'q':
                    print(Fore.YELLOW+'The test has ended!'+Style.RESET_ALL)
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


            #----------- ACCURACY OF TEST MODE - Nao resulta por incompatibilidade de tamanhos na comparaçao final

                """
            # Capture the user's drawing from the screen
            #user_drawing = cv2.captureScreen(region=(cx, cy, canvas_size,canvas_size))  # Adjust the region to capture the drawing area
                screenshot = pyautogui.screenshot(region=(cx, cy, canvas_size, canvas_size))

                # Converte a captura de tela em uma imagem OpenCV
                user_drawing = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Convert the captured image to grayscale
                user_drawing_gray = cv2.cvtColor(user_drawing, cv2.COLOR_BGR2GRAY)

                # Convert the colored_canvas to grayscale
                colored_canvas_color = cv2.cvtColor(colored_canvas, cv2.COLOR_GRAY2BGR)

                # Ensure the dimensions match (resize if necessary)
                user_drawing_gray = cv2.resize(user_drawing_gray, (user_drawing.shape[1], user_drawing.shape[0]))
                print(user_drawing_gray.shape)
                print(colored_canvas_color.shape)
                # Threshold both images
                _, user_binary = cv2.threshold(user_drawing_gray, 1, 255, cv2.THRESH_BINARY)
                _, initial_binary = cv2.threshold(colored_canvas_color, 1, 255, cv2.THRESH_BINARY)

                # Calculate pixel-wise difference
                difference = cv2.bitwise_xor(user_binary, initial_binary)

                # Accuracy %
                total_pixels = initial_binary.size
                differing_pixels = cv2.countNonZero(difference)
                accuracy = 100 * (1 - differing_pixels / total_pixels)

                print("Accuracy: {:.2f}%".format(accuracy))

                """
            #----------- READING INSTRUCTIONS AND DRAWING

            # Reads key
            k = cv2.waitKey(1) & 0xFF
            key = str(chr(k)) 

            # Safety measure if key is not pressed
            if not key_press(key,drawing_canvas): 
                break
            
            # If key pressed: 
            if key == "p":                                      # Alternates between drawing mode
                draw_mode = not draw_mode
                (prev_cx,prev_cy) = (None,None)

                if draw_mode:
                    print(Fore.YELLOW+'Back to drawing...\n'+Style.RESET_ALL)
                else: 
                    print(Fore.YELLOW+'Drawing paused...\n'+Style.RESET_ALL)
                
            elif key == 'c':                                    # Clears canvas
                draws = []
                drawing_canvas.fill(255)
                prev_cx,prev_cy = cx,cy
                print(Fore.CYAN+'New canvas\n'+Style.RESET_ALL)

            elif key == " ":                                    # Begins test
                draw_mode= True
                print(Fore.CYAN+'\n Drawing mode started! \n'+Style.RESET_ALL)

            elif key == "m":                                    # Alternates between having or not mouse mode
                umm= not umm
                print('Mouse mode: '+Fore.CYAN+ str(umm)+Style.RESET_ALL+'\n')

            elif key == "n":                                    # Alternates between having or not shake prevention mode
                usp= not usp
                print('Shake prevention mode: '+Fore.CYAN+ str(usp)+Style.RESET_ALL+'\n')

            elif key == "l":                                    # Alternates between having or not canvas mode
                ucm= not ucm
                print('Camera as canvas mode: '+Fore.CYAN+ str(ucm)+Style.RESET_ALL+'\n')

            elif key == 'c':                                                                # If 'c' pressed cleares canvas
                draws = []
                drawing_canvas.fill(255)
                prev_cx,prev_cy = cx,cy
                print(Fore.CYAN+'New canvas\n'+Style.RESET_ALL)
                
            # If drawing mode is active
            if draw_mode :
                if (cx,cy) != (None,None): # If coordenates are different to none type
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
                        
                        prev_cx,prev_cy = cx,cy

                # Calling shapes function        
                shapesFunc(drawing_canvas,draws)
            
            # Shows windows
            cv2.imshow(camera_window,drawing_canvas)

        capture.release()
        


#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()