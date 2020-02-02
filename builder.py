#!/usr/bin/env python3

import os
import pandas as pd
import lego_main as lego
from PIL import Image

#==============================================================#
#                  CHANGE THE VARIABLES BELOW                  #
#==============================================================#

largest_dimension = 64
file_name = 'test.jpg' # The name must contain an extension (e.g. .jpg or .png)
palette_mode = 'bw'

#=======================   PRE-PROCESS   ======================#

effect = 1 # Optional (between 0 and 11), if selected, please also select a factor
factor = 0.8 # Only works when 'effect' is selected, the preview default is 0.5
color = 0
brightness = 0
contrast = 0
sharpness = 0

#=====================   REPLACE COLORS   =====================#

colors_to_replace = {'H':'L'}

#==========================   MAIN   ==========================#

pre_process_ = 0
bulk_pre_process_ = 0
color_replace_ = 0
finalize_ = 1

#==============================================================#
#            DANGER ZONE, DO NOT TRY THIS AT HOME              #
#==============================================================#

size = (largest_dimension, largest_dimension)
raw_files = os.path.dirname(os.path.dirname(__file__)) + '/raw_files'
previews = os.path.dirname(os.path.dirname(__file__)) + '/previews'
processed_files = os.path.dirname(os.path.dirname(__file__)) + '/processed_files'
instructions = os.path.dirname(os.path.dirname(__file__)) + '/instructions'

def pre_process():       
    image = Image.open(f'{raw_files}/{file_name}')
    print(f'Processing file: {file_name}')
    lego.pre_process(image, size=size, out_path=f'{processed_files}/{os.path.splitext(file_name)[0]}.png', 
        effect=effect, palette_mode=palette_mode, factor=factor, color=color, brightness=brightness,
        contrast=contrast, sharpness=sharpness)
    
def bulk_pre_process():
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processing_pipeline.csv')
        pipeline = pd.read_csv(path, index_col=0)
        pipeline.fillna(value=0, inplace=True)
        pipeline.iloc[:, 2:] = pipeline.iloc[:, 2:].astype(int)
        for file_name in pipeline.index:
            print(f'Processing file: {file_name}')
            image = Image.open(f'{raw_files}/{file_name}')
            max_size = pipeline.loc[file_name, 'max_size']
            size = (max_size, max_size)
            lego.pre_process(image, size=size, out_path=f'{processed_files}/{os.path.splitext(file_name)[0]}.png', 
                 effect=pipeline.loc[file_name, 'effect'], palette_mode=pipeline.loc[file_name, 'palette_mode'], 
                 factor=pipeline.loc[file_name, 'factor'], color=pipeline.loc[file_name, 'color'], 
                 brightness=pipeline.loc[file_name, 'brightness'],contrast=pipeline.loc[file_name, 'contrast'], 
                 sharpness=pipeline.loc[file_name, 'sharpness'])
    
def finalize():        
    for file in os.listdir(processed_files):
        instructions_folder_path = os.path.join(instructions, os.path.splitext(file)[0])
        instructions_file_path = f'{instructions_folder_path}/Instructions_{os.path.splitext(file)[0]}.png'
        brick_count_path = f'{instructions_folder_path}/Brick_count_{os.path.splitext(file)[0]}'
        brick_image_path = os.path.join(os.path.dirname(__file__), 'lego', 'assets', 'bricks', '1x1.png')
        lego_effect_preview = f'{instructions_folder_path}/Result_preview_{os.path.splitext(file)[0]}.png'
        if file.endswith(".png"):
            if not os.path.exists(instructions_folder_path):
                os.makedirs(instructions_folder_path)
            image = Image.open(f'{processed_files}/{file}')
            # Add the png with the instructions to the folder
            lego.instructions(image, palette_mode=palette_mode, out_path=instructions_file_path)
            # Add the preview of the final result to the folder
            brick_image = Image.open(brick_image_path)
            print(f'Creating the final preview for {os.path.splitext(file)[0]}.png')
            lego.make_lego_image(image, brick_image).save(lego_effect_preview)
            # Add the brick count to the folder
            lego.color_count_printer(image, palette_mode, brick_count_path)
            
def color_replace():
    path = f'{processed_files}/{os.path.splitext(file_name)[0]}.png'
    image = Image.open(path)
    print(f'Replacing colors in: {file_name}')
    lego.manual_color_replace(image, colors_to_replace, palette_mode, path)
    
def main():
    if pre_process_ == 1:
        pre_process()
    if bulk_pre_process_ == 1:
        bulk_pre_process()
    if color_replace_ == 1:
        color_replace()
    if finalize_ == 1:
        finalize()
main()
