#!/usr/bin/env python3
from colorama import Fore, Style
import cv2
import json
import argparse
import numpy as np
from datetime import datetime


# Inicializa a captura de vídeo da câmera
cap = cv2.VideoCapture(0)

# Variáveis globais
drawing = False  # Indica se o usuário está desenhando
mode = 'circle'  # Inicialmente, o modo é definido para círculo
start_point = (0, 0)
end_point = (0, 0) 
image = np.zeros((512, 512, 3), dtype=np.uint8) #por agora ta assim 



def draw_shape(event,x,y,flags, param):
    global mode,drawing,start_point,end_point,image

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            if mode == 'circle':
                image_copy =image.copy()
                radius = int(np.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2))
                cv2.circle(image_copy, start_point, radius, pencil_color, 2)
                cv2.imshow("F3", image_copy)

            elif mode == 'square':
                image_copy =image.copy()
                cv2.rectangle(image_copy, start_point, (x, y), pencil_color, 2)
                cv2.imshow("F3", image_copy)

##################################
            
            elif mode == 'ellipse':
                image_copy =image.copy()
                # Calcule o tamanho da elipse
                a = abs(x - start_point[0])
                b = abs(y - start_point[1])
                # Desenhe a elipse
                cv2.ellipse(image_copy, start_point, (a, b), 0, 0, 360, pencil_color, 2)
                cv2.imshow("F3", image_copy)

###################################

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        if mode == 'circle':
            radius = int(np.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2))
            cv2.circle(image, start_point, radius, pencil_color, 2)
        elif mode == 'square':
            cv2.rectangle(image, start_point, end_point, pencil_color, 2)

###################################

        elif mode == 'ellipse':
            #image_copy = image.copy()
            a = abs(end_point[0] - start_point[0])
            b = abs(end_point[1] - start_point[1])
            cv2.ellipse(image, start_point, (a, b), 0, 0, 360, pencil_color, 2)
         
####################################

def main():
    parser = argparse.ArgumentParser(description='Definition of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = parser.parse_args()
    print('\n ' + 'Drawing ready ....'+ '\n')
    # Carregua os limites de cor a partir do arquivo JSON
    with open(args.json, 'r') as file:
        limits=json.load(file)

    global mode, pencil_color
    

    # Define as variáveis iniciais para a cor e tamanho do lápis
    pencil_color = (0, 0, 255)  # Vermelho inicialmente
    pencil_size = 2 
    mode = 'circle'

     # Define a tela em branco
    screen = np.full((480, 640, 3),255, dtype=np.uint8) 
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converta a imagem para o espaço de cores HSV (recomendado para detecção de cor)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Aplique a detecção de cor com base nos limites lidos do arquivo JSON
        mask = cv2.inRange(hsv, (limits['limits']['B']['min'], limits['limits']['G']['min'], limits['limits']['R']['min']),
                       (limits['limits']['B']['max'], limits['limits']['G']['max'], limits['limits']['R']['max']))

       

        # Encontre os contornos do objeto de maior área na máscara
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)

            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # Desenhe o centróide com uma cruz vermelha na imagem original
                cv2.drawMarker(frame, (cX, cY), pencil_color, markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)

                # Use o centróide para desenhar na tela
                if pencil_size % 2 == 0:
                    cv2.circle(frame, (cX, cY), pencil_size // 2, pencil_color, -1)
                    cv2.circle(screen, (cX, cY), pencil_size // 2, pencil_color, -1)
                else: 
                    cv2.circle(frame, (cX, cY), pencil_size // 2, pencil_color, -1)
                    cv2.circle(screen, (cX, cY), pencil_size // 2, pencil_color, -1)

         # Mostrar a imagem original
        #frame_sized=cv2.resize(frame,(600,400))
        
        
        cv2.setMouseCallback("F3", draw_shape)
       
        # Mostrar a imagem original
        
        cv2.imshow('Original Image', cv2.flip(frame,1))

        # Mostrar a tela em branco
        cv2.imshow('F3', image)
        #cv2.imshow('Drawing',screen)

        key = cv2.waitKey(1)
        if key == ord('r'):
             pencil_color = (0, 0, 255)  # Vermelho
             print('Selected color to ' + Fore.RED + 'red\n' + Style.RESET_ALL)

        elif key == ord('g'):
            pencil_color = (0, 255, 0)  # Verde
            print('Selected color to ' + Fore.GREEN + 'green\n' + Style.RESET_ALL)

        elif key == ord('b'):
            pencil_color = (255, 0, 0)  # Azul
            print('Selected color to '+ Fore.BLUE +  'blue\n' + Style.RESET_ALL)

        elif key == ord('+'):
            pencil_size += 2
            print('Pencil size increased to: '+ Fore.YELLOW + str(pencil_size)+ '\n' + Style.RESET_ALL)

        elif key == ord('-'):
            pencil_size = max(1, pencil_size - 2)
            print('Pencil size decreased to: '+ Fore.YELLOW + str(pencil_size)+ '\n' + Style.RESET_ALL)

        elif key == ord('o'):
             mode = 'circle'
             print('circle mode\n')

        elif key == ord('e'):
             mode = 'ellipse'
             print('ellipse mode\n')

        elif key == ord('s'):
             mode = 'square'
             print('square mode\n')
        
        elif key == ord('c'):
            screen = np.full((480, 640, 3),255, dtype=np.uint8)
            print( Fore.YELLOW + 'New canvas\n'+ Style.RESET_ALL)

        elif key == ord('w'):
        # Gere um nome de arquivo com base na data e hora atual
            current_time = datetime.now().strftime("%a_%b_%d_%H:%M:%S_%Y")
            filename = f'drawing_{current_time}.png'
            cv2.imwrite(filename, screen)
            print(Fore.YELLOW + 'Saved canvas\n'+ Style.RESET_ALL)

        elif key == ord('q'):
            print ( Fore.RED + 'Program interrupted\n'+ Style.RESET_ALL)
            break

if __name__ == '__main__':
    main()
