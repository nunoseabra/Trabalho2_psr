#!/usr/bin/env python3
#shebang line to inform the OS that the content is in python

#!/usr/bin/env python3

import json
import argparse
from random import randint, shuffle
import sys
from colorama import Fore, Style
import cv2
import numpy as np
from math import sqrt
from datetime import datetime
#from functions import get_centroid, initialization, key_press, limitsRead, repaint, square, windowSetup, draw_color,pencil_thick,shake_limit

draw_color = (0,0,255)
pencil_thick = 5
shake_limit=100

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
    global draw_color
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
            cv2.line(image_result, (cX-8, cY-8), (cX+8, cY+8), draw_color, 5)
            cv2.line(image_result, (cX+8, cY-8), (cX-8, cY+8), draw_color, 5)
    
    # if we don't detect any objects, we just show the mask as it is
    else:
        image_result = cv2.merge((mask, mask, mask))
        cX = 0
        cY = 0
        
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
        pencil_thick=max(1,(pencil_thick-2))
        print('Decreased pencil size to '+ str(pencil_thick)+'\n')

        # increase pencil size
    elif key_input=='+':
        pencil_thick=min(30,(pencil_thick+2))
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
    
def square(event,x,y,image):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        
        start_point = (x, y)
        
    elif event == cv2.EVENT_MOUSEMOVE:

        image_copy=image.copy()
        cv2.rectangle(image_copy, start_point, (x, y),draw_color, 2)
    elif event == cv2.EVENT_LBUTTONUP: 
        end_point = (x, y)   
        cv2.rectangle(image, start_point, end_point, draw_color, 2)

def getgrid(image):
    """
    function getgrid: compute the grid (division into zones) according to the image size, as well as the correlation
                    between the numbers are the colors they represent
        INPUT:
            - image: original image, we will use its dimensions to figure out the coloring grid
        OUTPUT:
            - contours: the coloring zones the image is divided into
            - numbers_to_colors: a list of colors; the index i of a color in this list means that, in the zone
                                coloring mode, that color corresponds to zones with the number i+1
    """

    h,w,_ = image.shape
    grid = np.zeros([h,w],dtype=np.uint8)

    # coloring zones are a grid

    grid[h-1,:] = 255
    grid[:,w-1] = 255

    for y in range(0,h,int(h/3)):
        grid[y,:] = 255
    for x in range(0,w,int(w/4)):
        grid[:,x] = 255

    grid = cv2.bitwise_not(grid)

    # contours of each zone
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    numbers_to_colors = [(0,0,255), (0,255,0), (255,0,0)]
    shuffle(numbers_to_colors)

    return contours, numbers_to_colors

def colorswindow(numbers_to_colors, accuracy=None):
    """
    function colorswindow: works out what to display on the small colors window for the zone coloring mode,
                        where it informs the user which number corresponds to which color, and eventually the
                        accuracy of the last coloring
        INPUT:
            - numbers_to_colors: a list of colors; the index i of a color in this list means that, in the zone
                                coloring mode, that color corresponds to zones with the number i+1
            - accuracy: the accuracy of the last coloring, to be displayed on the small colors window
        OUTPUT:
            - bg: final image to be displayed on the colors window
    """

    bg = np.zeros([300,350,3],dtype=np.uint8)

    for i in range(3):
        color = 'red' if numbers_to_colors[i]==(0,0,255) else ('green' if numbers_to_colors[i]==(0,255,0) else 'blue')
        cv2.putText(bg, str(i+1) + ' - ' + color, (50, 50+50*i), cv2.FONT_HERSHEY_SIMPLEX, 0.9, numbers_to_colors[i], 2)

    if accuracy!=None:
        cv2.putText(bg, 'Accuracy: ' + str(accuracy) + '%', (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
    
    return bg

def calc_accuracy(image, contours, zone_numbers, numbers_to_colors):
    """
    function calc_accuracy: calculates the accuracy of a given coloring in the zones coloring mode
        INPUT:
            - image: the painted frame which we want to examine for the accuracy of its painting
            - contours: the zones into which the initial frame was divided for coloring
            - zone_numbers: the numbers randomly attributed to each zone
            - numbers_to_colors: a list of colors; the index i of a color in this list means that, in the zone
                                coloring mode, that color corresponds to zones with the number i+1
        OUTPUT:
            - [return value]: final accuracy value, rounded to be an int
    """

    h,w,_ = image.shape
    total_pixels = h*w

    right_pixels = 0 # this will hold the number of pixels with the correct color
    # for each zone...
    for i in range(len(contours)):

        c = contours[i]                             # the zone
        zone_number = zone_numbers[i]               # the zone number
        color = numbers_to_colors[zone_number-1]    # the zone color

        # corners of this zone (zones are always rectangles)
        minX = c[0][0][0]
        maxX = c[2][0][0]
        minY = c[0][0][1]
        maxY = c[1][0][1]

        _,_,depth = image.shape

        # evaluate each pixel
        for pixel_row in image[minY:maxY, minX:maxX, 0:depth]:
            for pixel in pixel_row:
                pixel = (pixel[0], pixel[1], pixel[2])
                right_pixels += 1 if pixel==color else 0

    # compute accuracy
    return int((right_pixels/total_pixels)*100)

def contours(original, contours, numbers):
    """
    function findcontours: apply the grid to the image and distribute coloring numbers among the different
                        coloring zones
        INPUT:
            - original: original image where we will lay the grid
            - contours: grid to be applied
            - numbers: array of random numbers to be distributed among the zones
        OUTPUT:
            - [return value]: original image with grid and coloring numbers laid out
    """

    # grid and numbers will be white
    color = (255,255,255)

    for i in range(len(contours)):
        c = contours[i]

        x,y,w,h = cv2.boundingRect(c)
        cX = int(x + w/2)
        cY = int(y + h/2)

        # write the numbers in each zone
        cv2.putText(original, str(numbers[i]), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # draw the contours and return the result
    return cv2.drawContours(original, contours, -1, color, 3)

class Shapes:

    def __init__(self,type,origin,final,colour,thickness):
        self.type = type
        self.coord_origin = origin
        self.coord_final = final
        self.color = colour
        self.thickness = thickness

class Mouse:
    
    def __init__(self):
        self.coords = (None,None)
        self.pressed = False

    def update_mouse(self,event,x,y,flags,param):
        self.coords = (x,y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.pressed = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.pressed = False
                    
def main():
    global draw_color, pencil_thick,shake_limit
    
    # setting up the video capture
    file,usp,ucm,umm = initialization()

    #print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'd'+ Style.RESET_ALL + ' to pause!\n')
    print('To activate/deactivate modes:\n')
    print('Shake prevention - press '+Fore.CYAN+ 'n'+ Style.RESET_ALL + ' \n')
    print('Camera as canvas - press '+Fore.CYAN+ 'l'+ Style.RESET_ALL + ' \n')
    print('Mouse mode - press '+Fore.CYAN+ 'm'+ Style.RESET_ALL + ' \n')
    print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'd'+ Style.RESET_ALL + ' to pause!\n')
    
    limits = limitsRead(file) 

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    camera_window, mask_window, drawing_window, drawing_cache = windowSetup(frame)
  
    cv2.imshow( camera_window,frame)
    cv2.imshow(drawing_window,drawing_cache)
    
    low_limits = (limits['B']['min'], limits['G']['min'], limits['R']['min'])
    high_limits = (limits['B']['max'], limits['G']['max'], limits['R']['max'])
    print

    mouse = Mouse()
    cv2.setMouseCallback(drawing_window, mouse.update_mouse)
    
    draws = []
    draw_mode = False
    color_zones=False

    ## Operação em contínuo ##
    while True:
        ret,frame = capture.read()
        #frame_sized=cv2.resize(frame,(int(frame.shape[0]*0.6),int(frame.shape[1]*0.6)))
        frame_flip = cv2.flip(frame, 1)
        cv2.imshow(camera_window,frame_flip)

        if ucm:  
            drawing_canvas = frame_flip
        else:
            drawing_canvas = drawing_cache
        
        frame_mask = cv2.inRange(frame_flip, low_limits, high_limits)
        
        frame_wMask = cv2.bitwise_and(frame_flip,frame_flip, mask = frame_mask)
        cv2.imshow(mask_window,frame_wMask)
        
        cx,cy,frame_centroid= get_centroid(frame_mask)
        #cv2.imshow(camera_window, frame_test)
        cv2.imshow( mask_window, frame_centroid)

        if not umm:    
            cx,cy,frame_test = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            image_copy=drawing_canvas.copy()
            try:
                cv2.drawMarker(image_copy, (cx,cy) , draw_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
                cv2.imshow(drawing_window,image_copy)
                
            except: (cx,cy)==(None,None)
        else:
            cx = mouse.coords[0]
            cy = mouse.coords[1]
            
            if cx:
                image_copy=drawing_canvas.copy()
                cv2.line(image_copy, (cx-5, cy-5), (cx+5, cy+5), (0, 0, 255), 5)
                cv2.line(image_copy, (cx+5, cy-5), (cx-5, cy+5), (0, 0, 255), 5)
                cv2.imshow(drawing_window,image_copy)
       
        '''
             # if we're in coloring mode
        if color_zones:
            # display the grid and numbers
            frame = contours(drawing_canvas, zones, color_numbers)

            # setting up the window the coloring accuracy
            
            color_window = 'Color map'
            cv2.namedWindow(color_window, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(color_window, (300,350))
            cv2.moveWindow(color_window, 800, 600)
            
            # show the colors to be used
            stats = colorswindow(numbers_to_colors)
            cv2.imshow(drawing_canvas, stats)
        '''

        k = cv2.waitKey(1) & 0xFF
        key = str(chr(k))

        if not key_press(key,drawing_canvas): 
            break

        if key == "p":
            draw_mode = not draw_mode
            (prev_cx,prev_cy) = (None,None)

            if draw_mode:
                print('Back to drawingm...\n')
            else: 
                print('Drawing paused...\n')
            
        elif key == 'c':
            draws = []
            drawing_canvas.fill(255)
            prev_cx,prev_cy = cx,cy
            print('New canvas\n')

        elif key == " ":
            draw_mode= True
            print('\nDesenho iniciado!\n')

        elif key == "m":
            umm= not umm
            print('Mouse mode: '+ str(umm)+'\n')

        elif key == "n":
            usp= not usp
            print('Shake prevention mode: '+ str(usp)+'\n')

        elif key == "l":
            ucm= not ucm
            print('Camera as canvas mode: '+ str(ucm)+'\n')
        '''
        elif key=='t':
            # if we're activating coloring mode
            if not color_zones:

                # clear canvas
                draws = []
                (prev_cx,prev_cy) = (None,None)

                # compute the grid (division into zones) and correlation between the numbers are the 
                # colors they represent
                zones, numbers_to_colors = getgrid(frame_flip)
                num_zones = len(zones) # number of coloring zones

                # create array of random numbers between 1 and 3, with as many numbers as there are
                # coloring zones; these will later be distributed among the zones; the numbers go from 1
                # to 3 because we can only use three colors (red, blue and green)
                color_numbers = []
                for _ in range(num_zones):
                    color_numbers.append(randint(1,3)) # we have three colors

            else:
                accuracy = calc_accuracy(frame_flip, zones, color_numbers, numbers_to_colors)
                stats = colorswindow(numbers_to_colors, accuracy)
                cv2.imshow(drawing_canvas, stats)
            
            # update the mode indicator
            color_zones = not color_zones

            if color_zones:
                print('Teste de pintura\n')
            else: print('Teste de pintura desativado\n')
        '''
        
        if draw_mode :
            if (cx,cy) != (None,None):
                
                if key == "s":
                    draws[-1] = (Shapes("square",(cX,cY),(cx,cy),draw_color,pencil_thick))  
                    print('Square draw\n')
                        
                    
                elif key == "o":
                    draws[-1] = (Shapes("circle",(cX,cY),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Circle draw\n')

                elif key == "e":
                    image_copy=drawing_canvas.copy()
                    
                    draws[-1] = (Shapes("ellipse",(cX,cY),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Ellipse draw\n')

                elif key == 'c':
                    draws = []
                    drawing_canvas.fill(255)
                    prev_cx,prev_cy = cx,cy
                    print('New canvas\n')

                else:
                    try:
                        if usp and (prev_cx,prev_cy) != (None,None):
                            diffX = abs(prev_cx - cx)
                            diffY = abs(prev_cy - cy)
                            if diffX>shake_limit or diffY>shake_limit: # this line performs shake detection
                                draws.append(Shapes("dot",(0,0),(prev_cx,prev_cy),draw_color,pencil_thick))
                            else:
                                draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))
                        elif (prev_cx,prev_cy) != (None,None):
                                draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))
                    except:
                        prev_cx, prev_cy = cx,cy

                if k == 0xFF:
                    cX,cY = cx,cy
                    prev_cx,prev_cy = cx,cy
                    
            repaint(drawing_canvas,draws)
          
            
        cv2.imshow( camera_window,drawing_canvas)

    capture.release()
    



if __name__ == '__main__':
    main()