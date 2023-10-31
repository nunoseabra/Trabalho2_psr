#!/usr/bin/env python3
#shebang line to inform the OS that the content is in python

#!/usr/bin/env python3

import json
import argparse
import sys
from colorama import Fore, Style
import cv2
import numpy as np
from math import sqrt
from datetime import datetime
from functions import get_centroid, initialization, key_press, limitsRead, repaint, windowSetup

draw_color = (0,0,255)
pencil_thick = 5
shake_limit=100


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
    path, usp,ucm,umm = initialization()

    #print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'd'+ Style.RESET_ALL + ' to pause!\n')
    print('To activate/deactivate modes:\n')
    print('Shake prevention - press '+Fore.CYAN+ 'n'+ Style.RESET_ALL + ' \n')
    print('Camera as canvas - press '+Fore.CYAN+ 'l'+ Style.RESET_ALL + ' \n')
    print('Mouse mode - press '+Fore.CYAN+ 'm'+ Style.RESET_ALL + ' \n')
    print('Press '+ Fore.CYAN + 'SPACE'+Style.RESET_ALL + ' to start drawing and '+Fore.CYAN+ 'd'+ Style.RESET_ALL + ' to pause!\n')
    
    limits = limitsRead(path) 

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    camera_window, mask_window, drawing_window, drawing_cache = windowSetup(frame)
  
    cv2.imshow( camera_window,frame)
    cv2.imshow(drawing_window,drawing_cache)
    
    low_limits = (limits['B']['min'], limits['G']['min'], limits['R']['min'])
    high_limits = (limits['B']['max'], limits['G']['max'], limits['R']['max'])
    
    mouse = Mouse()
    cv2.setMouseCallback(drawing_window, mouse.update_mouse)
    
    draws = []
    draw_mode = False

    ## Operação em contínuo ##
    while True:
        _,frame = capture.read()
        #frame_sized=cv2.resize(frame,(int(frame.shape[0]*0.6),int(frame.shape[1]*0.6)))
        frame_flip = cv2.flip(frame, 1)
        cv2.imshow( camera_window,frame_flip)

        
        if ucm: 
            drawing_canvas = frame_flip
        else:
            drawing_canvas = drawing_cache
        
        frame_mask = cv2.inRange(frame_flip, low_limits, high_limits)
        
        frame_wMask = cv2.bitwise_and(frame_flip,frame_flip, mask = frame_mask)
        cv2.imshow(mask_window,frame_wMask)
        
        (cx,cy),frame_test,skip= get_centroid(frame_mask)
        #cv2.imshow(camera_window, frame_test)
        cv2.imshow( mask_window, frame_test)

        if not umm:    
            (cx,cy),frame_test,skip = get_centroid(frame_mask)
            cv2.imshow(mask_window, frame_test)
            
        else:
            
            cx = mouse.coords[0]
            cy = mouse.coords[1]
            
            if cx:
                image_copy=drawing_canvas.copy()
                cv2.line(image_copy, (cx-5, cy-5), (cx+5, cy+5), (0, 0, 255), 5)
                cv2.line(image_copy, (cx+5, cy-5), (cx-5, cy+5), (0, 0, 255), 5)
                cv2.imshow(drawing_window,image_copy)


        k = cv2.waitKey(1) & 0xFF

        key = str(chr(k))
        if not key_press(key,drawing_canvas): 
            print('Program interrupted\n')
            break

        if key == "d":
            draw_mode = not draw_mode
            (cx,cy) = (None,None)
            

            print('\n')

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

        if draw_mode :
            if (cx,cy) != (None,None):
                if key == "s":
                    draws[len(draws)-1] = (Shapes("square",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Square draw\n')

                elif key == "o":
                    draws[len(draws)-1] = (Shapes("circle",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Circle draw\n')

                elif key == "e":
                    draws[len(draws)-1] = (Shapes("ellipse",(cox,coy),(cx,cy),draw_color,pencil_thick))
                    prev_cx,prev_cy = cx,cy
                    print('Ellipse draw\n')

                elif key == 'c':
                    draws = []
                    drawing_canvas.fill(255)
                    prev_cx,prev_cy = cx,cy
                    print('New canvas\n')
                else:
                    try:
                        if usp:
                            diffX = abs(prev_cx - cx)
                            diffY = abs(prev_cy - cy)
                            if diffX>shake_limit or diffY>shake_limit: # this line performs shake detection
                                draws.append(Shapes("dot",(0,0),(prev_cx,prev_cy),draw_color,pencil_thick))
                            else:
                                draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))
                        else:
                            
                            draws.append(Shapes("line",(prev_cx,prev_cy),(cx,cy),draw_color,pencil_thick))
                    except:
                        prev_cx, prev_cy = cx,cy

                if k == 0xFF:
                    cox,coy = cx,cy
                    prev_cx,prev_cy = cx,cy
                    print('prev_',prev_cx)
                    print('cx ',cx)
            repaint(drawing_canvas,draws)
            
        cv2.imshow( drawing_window,drawing_canvas)

    capture.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()