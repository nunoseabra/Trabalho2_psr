#!/usr/bin/env python3
#shebang line to inform the OS that the content is in python

#!/usr/bin/env python3

import json
import argparse
import sys
import cv2
import numpy as np
from math import sqrt
from datetime import datetime

draw_color = (0,0,255)
pencil_thick = 5

def initialization():
    # Input Arguments
    parser = argparse.ArgumentParser(description='Ar Paint ')
    parser.add_argument('-j','--json',type = str, required= False , help='Full path to json file', default='limits.json')
    parser.add_argument('-usp','--use_shake_prevention', action='store_true', help='Use shake prevention mode')
    parser.add_argument('-ucc','--use_cam_canvas', action='store_true', help='Use camera as canvas')
    args = vars(parser.parse_args())

    file_path = 'limits.json' if not args['json'] else args['json'] # Path for the json file
    usp = args['use_shake_prevention'] # Shake prevention mode
    #ucc = args['use_cam_canvas'] # Use live feed from the cam to be used as the canvas
    return file_path , usp#, ucc

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
        
    return (cX,cY), image_result 

def key_press(key_input,canvas):
    global draw_color, pencil_thick
        # quit program
    if key_input=='q':
        return False
        # change color to Red
    elif key_input=='r':
        draw_color = (0,0,255)
        # change color to Green
    elif key_input=='g':
        draw_color = (0,255,0)
        # change color to Blue
    elif key_input=='b':
        draw_color = (255,0,0)
        # decrease pencil size
    elif key_input=='-':
        if pencil_thick > 0:
            pencil_thick -= 5
        # increase pencil size
    elif key_input=='+':
        if pencil_thick < 50:
            pencil_thick += 5
        # save canvas 
    elif key_input=='w':
        date = datetime.now()
        formatted_date = date.strftime("%a_%b_%d_%H:%M:%S")
        name_canvas = 'drawing_' + formatted_date + '.png'
        name_canvas_colored = 'drawing_' + formatted_date + '_colored.jpg'
        cv2.imwrite(name_canvas, canvas)
        cv2.imwrite(name_canvas_colored, canvas)
        
    return True

class Figure:

    def __init__(self,type,origin,final,colour,thickness):
        self.type = type
        self.coord_origin = origin
        self.coord_final = final
        self.color = colour
        self.thickness = thickness

def re_paint(frame, figures):
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
               
def main():
    global draw_color, pencil_thick
    # setting up the video capture
    path, usp = initialization()
    limits = limitsRead(path) 

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()

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
    cv2.moveWindow(drawing_window, 1000, 300)


    cv2.imshow( camera_window,frame)

    drawing_cache = np.zeros((window_height,window_width,4))*255
    #draws.fill(255)

    cv2.imshow(drawing_window,drawing_cache)
    
    limits_low = (limits['B']['min'], limits['G']['min'], limits['R']['min'])
    limits_high = (limits['B']['max'], limits['G']['max'], limits['R']['max'])
    
    draws = []
    draw_mode = False

    ## Operação em contínuo ##
    while True:
        _,frame = capture.read()
        frame_flip = cv2.flip(frame, 1)
        #draws.fill(255)
        
        if (0): 
            drawing_canvas = frame_flip

        else:
            drawing_canvas = drawing_cache
        
        frame_mask = cv2.inRange(frame_flip, limits_low, limits_high)

        frame_wMask = cv2.bitwise_and(frame_flip,frame_flip, mask = frame_mask)
        cv2.imshow(camera_window,frame_wMask)
        
        (cx,cy),frame_test= get_centroid(frame_mask)
        cv2.imshow( mask_window, frame_test)

        k = cv2.waitKey(1) & 0xFF

        key_chr = str(chr(k))
        if not key_press(key_chr,drawing_canvas): break

        if key_chr == "d":
            draw_mode = True

        if draw_mode :
            if (cx,cy) != (None,None):
                if key_chr == "s":
                    draws[len(draws)-1] = (Figure("square",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                elif key_chr == "o":
                    draws[len(draws)-1] = (Figure("circle",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                elif key_chr == "e":
                    draws[len(draws)-1] = (Figure("ellipse",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                elif key_chr == 'c':
                    draws = []
                    prev_cx,prev_cy = cx,cy
                else:
                    try:
                        draws.append(Figure("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))
                    except:
                        prev_cx,prev_cy = cx,cy
                if k == 0xFF:
                    cox,coy = cx,cy
                    prev_cx,prev_cy = cx,cy
    
            re_paint(drawing_canvas,draws)
            

        cv2.imshow( drawing_window,drawing_canvas)

    capture.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()