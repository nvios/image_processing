#!/usr/bin/env python3

import os
import lego_main as lego
from PIL import Image

#==============================================================#
#                  CHANGE THE VARIABLES BELOW                  #
#==============================================================#

largest_dimension = 64
palettes = ['art', 'portrait', 'solid']
factor = 0.5

#==============================================================#
#            DANGER ZONE, DO NOT TRY THIS AT HOME              #
#==============================================================#

size = (largest_dimension, largest_dimension)
raw_files = os.path.dirname(os.path.dirname(__file__)) + '/raw_files'
previews = os.path.dirname(os.path.dirname(__file__)) + '/previews'

def generate_previews():
    for file in os.listdir(raw_files):
        if file.endswith(".jpeg") or file.endswith(".jpg") or file.endswith(".png"):
            in_path = f'{raw_files}/{file}'
            previews_folder_path = os.path.join(previews, os.path.splitext(file)[0])
            
            print(f'Creating the previews for: {file}')
            if not os.path.exists(previews_folder_path):
                os.makedirs(previews_folder_path)
            image = Image.open(in_path)
            for palette in palettes:
                previews_file_path = os.path.join(previews_folder_path, 
                                                  f'Previews_{palette[:2].upper()}_{os.path.splitext(file)[0]}.pdf')
                lego.multi_preview(image, size, previews_file_path, palette, factor)

generate_previews()


