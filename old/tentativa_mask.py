import cv2
import numpy as np
import json

with open('limits.json', 'r') as file:
        limits=json.load(file)

def applyMask(frame,limits):
    # Image converted to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.inRange(hsv, (limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']),
                       (limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']))
def main():
    capture = cv2.VideoCapture(0)
    ret, frame = cap.read()
    pencil_color = (0, 0, 255)
    while True:
        mask = applyMask(frame,limits)
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
                        pencil_coords = (cX,cY)
                        # Draws centroid in the original image with a red cross
                        cv2.drawMarker(final_image,pencil_coords, pencil_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)
        key=cv2.waitKey(1)
        if key == ord('q'):
            # Quits program when "q" is pressed
            print ( Fore.RED + 'Program interrupted\n'+ Style.RESET_ALL)
            cv2.destroyAllWindows()
            break

#--------- MAIN CODE  ---------#

if __name__ == '__main__':
    main()
        