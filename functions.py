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
import numpy as np
from datetime import datetime
import pygame as pygame



# Function to draw shapes in the canva
def draw_shape(event,x,y,canvas,pencil_color,mode):
    # Calling global variables
    

    # The function starts when the button is pressed
    if event == cv2.EVENT_LBUTTONDOWN :
                                # Drawing flag turns true
        start_point = (x,y)
        
    elif event == cv2.EVENT_MOUSEMOVE :          # If the mouse moves while pressed
        
            if mode == 'circle':                # Circle mode
                image_copy =canvas.copy()
                
                radius = int(np.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2))
                cv2.circle(image_copy, start_point, radius, pencil_color, 2)
                cv2.imshow("Drawing1", image_copy)

            elif mode == 'rectangle':           # Rectangle mode
                image_copy =canvas.copy()
                cv2.rectangle(image_copy, start_point, (x, y), pencil_color, 2)
                cv2.imshow("Drawing1", image_copy)
            
            elif mode == 'ellipse':
                image_copy =canvas.copy()
                # Calcule o tamanho da elipse
                a = abs(x - start_point[0])
                b = abs(y - start_point[1])
                # Desenhe a elipse
                cv2.ellipse(image_copy, start_point, (a, b), 0, 0, 360, pencil_color, 2)
                cv2.imshow("Drawing1", image_copy)

    # Button no longer pressed - program ends and defines the radious based on end point
    elif event == cv2.EVENT_LBUTTONUP:
        
        end_point = (x, y)

        if   mode=='circle':                    # Ends circle mode
            radius = int(np.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2))
            cv2.circle(canvas, start_point, radius, pencil_color, 2)
            

        elif mode == 'rectangle':               # Ends rectangle mode
            cv2.rectangle(canvas, start_point, end_point, pencil_color, 2)
        
        elif mode == 'ellipse':
            #image_copy = image.copy()
            a = abs(end_point[0] - start_point[0])
            b = abs(end_point[1] - start_point[1])
            cv2.ellipse(canvas, start_point, (a, b), 0, 0, 360, pencil_color, 2)

def applyMask(image,limits):
     # Image converted to HSV
     # Image converted to HSV
        #hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        print(limits)
        # Detects color based on JSON file limits
        a=cv2.inRange(image, (limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']),
                       (limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']))
        return a
def centroid_position(mask,pencil_color):
        global pencil_coords
     # Finds the contours of the largest object in the mask area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:

                # If contours are found, the largest contour is the one with the biggest area
                largest_contour = max(contours, key=cv2.contourArea)

                # make it green (but still show other objects in white
                biggest_obj = np.zeros(mask.shape, np.uint8)
                cv2.drawContours(biggest_obj, [largest_contour ], -1, 255, cv2.FILLED)
                biggest_obj = cv2.bitwise_and(mask, biggest_obj) # mask-like image with only the biggest object
                all_other = cv2.bitwise_xor(mask, biggest_obj) # all other objects except the biggest one
                
                b = all_other
                g = mask
                r = all_other

                final_image = cv2.merge((b, g, r))
                        
                M = cv2.moments(largest_contour)
                
                # If contour is not zero, calculate centroid
                if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"]) 
                        cY = int(M["m01"] / M["m00"])
                        
                        # Draws centroid in the original image with a red cross
                        cv2.drawMarker(final_image,(cX,cY), pencil_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
        
                return cX,cY,final_image 
        
def new_draw(old_coords,pencil_color,pencil_size,usp,image,draw):
                global pencil_coords
                if not draw:
                    pass
                else:
                    global pencil_coords
                    cv2.line(image, old_coords,pencil_coords,pencil_color, pencil_size)                   

                        # Uses the center of the image to paint canvas
                    if pencil_size % 2 == 0:
                        cv2.circle(image, pencil_coords, pencil_size // 2, pencil_color, -1)
                        cv2.circle(image, pencil_coords, pencil_size // 2, pencil_color, -1)
                    else: 
                        cv2.circle(image, pencil_coords, pencil_size // 2, pencil_color, -1)
                        cv2.circle(image, pencil_coords, pencil_size // 2, pencil_color, -1)

                    if old_coords and usp:         # The program was already running and checks for shake in the centroid
                        # Calculate the distance between the previous and current centroids
                        distance=np.sqrt((pencil_coords[0] - old_coords[0]) ** 2 + (pencil_coords[0] - old_coords[1]) ** 2)
                        
                        # Define a threshold for shake prevention (you can adjust this)
                        shake_threshold = 150

                        if distance > shake_threshold:
                            # If shake is detected, draw a single point
                            cv2.circle(image,pencil_coords, pencil_size, pencil_color, -1)
                        else:
                            # Draw a line between the previous and current centroids
                            cv2.line(image, old_coords,pencil_coords,pencil_color, pencil_size)
                return image
