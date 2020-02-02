from __future__ import unicode_literals

from PIL import Image, ImageEnhance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from matplotlib.ticker import AutoMinorLocator
import sys
import os
from lego import palettes


def apply_color_overlay(image, color):
    '''Small function to apply an effect over an entire image'''
    overlay_red, overlay_green, overlay_blue = color
    channels = image.split()

    r = channels[0].point(lambda color: overlay_effect(color, overlay_red))
    g = channels[1].point(lambda color: overlay_effect(color, overlay_green))
    b = channels[2].point(lambda color: overlay_effect(color, overlay_blue))

    channels[0].paste(r)
    channels[1].paste(g)
    channels[2].paste(b)

    return Image.merge(image.mode, channels)

def overlay_effect(color, overlay):
    '''Actual overlay effect function'''
    if color < 33:
        return overlay - 100
    elif color > 233:
        return overlay + 100
    else:
        return overlay - 133 + color

def make_lego_image(thumbnail_image, brick_image):
    '''Create a lego version of an image from an image'''
    base_width, base_height = thumbnail_image.size
    brick_width, brick_height = brick_image.size

    rgb_image = thumbnail_image.convert('RGB')

    lego_image = Image.new("RGB", (base_width * brick_width,
                                   base_height * brick_height), "white")

    for brick_x in range(base_width):
        for brick_y in range(base_height):
            color = rgb_image.getpixel((brick_x, brick_y))
            lego_image.paste(apply_color_overlay(brick_image, color),
                             (brick_x * brick_width, brick_y * brick_height))
    return lego_image


def get_new_filename(file_path, ext_override=None):
    '''Returns the save destination file path'''
    folder, basename = os.path.split(file_path)
    base, extension = os.path.splitext(basename)
    if ext_override:
        extension = ext_override
    new_filename = os.path.join(folder, "{0}_lego{1}".format(base, extension))
    return new_filename


def get_new_size(base_image, brick_image, size=None):
    '''Returns a new size the first image should be so that the second one fits neatly in the longest axis'''
    new_size = base_image.size
    if size:
        scale_x, scale_y = size, size
    else:
        scale_x, scale_y = brick_image.size

    if new_size[0] > scale_x or new_size[1] > scale_y:
        if new_size[0] < new_size[1]:
            scale = new_size[1] / scale_y
        else:
            scale = new_size[0] / scale_x

        new_size = (int(round(new_size[0] / scale)) or 1,
                    int(round(new_size[1] / scale)) or 1)

    return new_size

def get_lego_palette(palette_mode):
    '''Gets the palette for the specified lego palette mode'''
    legos = palettes.legos()
    palette = legos[palette_mode]
    return palettes.extend_palette(palette)

def quantize_to_palette(image, palette, dither):
    """Convert an RGB or L mode image to use a given P image's palette."""
    # use palette from reference image
    '''if palette.mode != "P":
        raise ValueError("bad mode for palette image")
    if image.mode != "RGB" and image.mode != "L":
        raise ValueError("only RGB or L mode images can be quantized to a palette")'''
    im = image.im.convert("P", 1 if dither else 0, palette.im)
    # the 0 above means turn OFF dithering
    # Later versions of Pillow (4.x) rename _makeself to _new
    try:
        return image._new(im)
    except AttributeError:
        return image._makeself(im)

def apply_thumbnail_effects(image, palette, dither=False):
    '''Apply effects on the reduced image before Legofying'''
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette)
    return quantize_to_palette(image, palette_image, dither)
    
def palette_thumbnail(image, size, palette_mode='all', dither=False):
    ''' Reduce the image to thumbnail and converts the colors to the selected palette. 

    image: path to the original image
    size: tuple containing the X and Y size
    palette_mode: 
    - grayscale (5 shades of gray)
    - solid
    '''
    image.thumbnail(size)
    palette = get_lego_palette(palette_mode)
    converted_image = apply_thumbnail_effects(image, palette, dither)
    return converted_image

def legofy_image(base_image, brick_image, output_path, size, palette_mode, dither):
    '''Legofy an image'''
    new_size = get_new_size(base_image, brick_image, size)
    base_image.thumbnail(new_size, Image.ANTIALIAS)
    if palette_mode:
        palette = get_lego_palette(palette_mode)
        base_image = apply_thumbnail_effects(base_image, palette, dither)
    make_lego_image(base_image, brick_image).save(output_path)

def main(image_path, output_path=None, size=None,
         palette_mode=None, dither=False):
    '''Legofy image or gif with brick_path mask'''
    image_path = os.path.realpath(image_path)
    if not os.path.isfile(image_path):
        print('Image file "{0}" was not found.'.format(image_path))
        sys.exit(1)

    brick_path = os.path.join(os.path.dirname(__file__), "assets",
                              "bricks", "1x1.png")

    if not os.path.isfile(brick_path):
        print('Brick asset "{0}" was not found.'.format(brick_path))
        sys.exit(1)

    base_image = Image.open(image_path)
    brick_image = Image.open(brick_path)

    if palette_mode:
        print ("LEGO Palette {0} selected...".format(palette_mode.title()))
    elif dither:
        palette_mode = 'all'

    if output_path is None:
        output_path = get_new_filename(image_path, '.png')
    print("Static image detected, will now legofy to {0}".format(output_path))
    legofy_image(base_image, brick_image, output_path, size, palette_mode, dither)

    base_image.close()
    brick_image.close()
    print("Finished!")
    
    
# =================  PRE PROCESSING AND PREVIEW  ================= #
      

def default_effect(image, effect, size, palette_mode, factor): 
    if 0 <= effect <= 9:
        effects = default_preview(image, factor)
        return palette_thumbnail(effects[effect], size, palette_mode, dither=False)
    else:
        raise Exception('The effect number must be within 0 and 9.')

def custom_effect(image, color=0, brightness=0, contrast=0, sharpness=0):
    ''' Apply custom enhancements to the input image. '''
    if color + brightness + contrast + sharpness == 0:
        raise Exception('Please pass at least one effect as the argument of "custom_effect".')
    else: 
        image = [ImageEnhance.Color(image).enhance(color + 1), image][color == 0]
        image = [ImageEnhance.Brightness(image).enhance(brightness + 1), image][brightness == 0]
        image = [ImageEnhance.Contrast(image).enhance(contrast + 1), image][contrast == 0]
        image = [ImageEnhance.Sharpness(image).enhance(sharpness + 1), image][sharpness == 0]
        return image

def pre_process(image, size=None, effect=0, out_path=None, palette_mode='solid', factor=0.5, color=0, brightness=0, contrast=0, sharpness=0):
  ''' Generate a preview of the final result and tweak the image parameters. '''
  if size:
    size_x, size_y = size
  else:
    size_x, size_y = image.size

  if color != 0 or brightness != 0 or contrast != 0 or sharpness != 0:
    image = custom_effect(image, color, brightness, contrast, sharpness)
    image = palette_thumbnail(image, size=(size_x, size_y), palette_mode=palette_mode, dither=False)
    quadrants_x, quadrants_y, unit = count_quadrants(image)
    image = image.crop((0, 0, quadrants_x * unit, quadrants_y * unit))
    if out_path:
        image.save(out_path)
    return image
  else:
    image = default_effect(image, effect, size, palette_mode, factor) 
    quadrants_x, quadrants_y, unit = count_quadrants(image)
    image = image.crop((0, 0, quadrants_x * unit, quadrants_y * unit))
    if out_path:
        image.save(out_path)
    return image

def multi_preview(image, size=None, out_path=None, palette_mode='all', factor=0.5):
  ''' Generate standard combinations of enhancement parameters. '''  
  if size:
    size_x, size_y = size
  else:
    size_x, size_y = image.size
    
  previews = default_preview(image, factor)
  fig, axs = plt.subplots(5,2, figsize=(10, 20), dpi=40)
  plt.subplots_adjust(wspace=0.1, hspace=0)
  plt.suptitle(f'Palette: {palette_mode.upper()}', va='bottom') 
  titles = {
            0:  'Original image (effect=0)', 
            1:  'Very high contrast(effect=1)',
            2:  'Low brightness, high contrast (effect=2)',
            3:  'High brightness, high contrast (effect=3)',
            4:  'Low saturation, high contrast (effect=4)',
            5:  'High saturation, high contrast (effect=5)',
            6:  'Low saturation (effect=6)', 
            7:  'High saturation (effect=7)', 
            8:  'High brightness (effect=8)', 
            9:  'High contrast (effect=9)'
            }

  n = 0
  for row in axs:
    for ax in row:
      previews[n] = palette_thumbnail(previews[n], size=(size_x, size_y), palette_mode=palette_mode, dither=False) #========================================================#
      ax.axis('off')
      ax.imshow(previews[n])
      ax.set_title(titles[n])
      n += 1

  plt.tight_layout(rect=[0, 0.05, 1, 0.98])  
  if out_path:
      plt.savefig(out_path, bbox_inches='tight')
  plt.close()

def default_preview(image, factor):
  ''' Generate default previews of the image applying different effects '''
  original_image = image
  color_less = ImageEnhance.Color(image).enhance(1 - factor * 0.5)
  color_more = ImageEnhance.Color(image).enhance(1 + factor)
  brightness_more = ImageEnhance.Brightness(image).enhance(1 + factor)
  contrast_more = ImageEnhance.Contrast(image).enhance(1 + factor)
  contrast_more_x2 = ImageEnhance.Contrast(image).enhance(1 + factor*2)
  color_contrast_more = ImageEnhance.Color(contrast_more).enhance(1 + factor)
  color_contrast_less = ImageEnhance.Color(contrast_more).enhance(1 - factor * 0.5)
  brightness_contrast_more = ImageEnhance.Brightness(contrast_more).enhance(1 + factor)
  brightness_contrast_less = ImageEnhance.Brightness(contrast_more).enhance(1 - factor*0.2)

  return [original_image, 
          contrast_more_x2,
          brightness_contrast_less,
          brightness_contrast_more,
          color_contrast_less,
          color_contrast_more,
          color_less, 
          color_more, 
          brightness_more, 
          contrast_more]   
 

# ============  CHECK AND REPLACE RARE COLORS  ============= #  


def auto_color_replace(image, palette_mode, out_path):
    ''' Count the pixels for each color in the pallette and replace rare colors. '''
    colors = palettes.LEGOS[palette_mode]
    substitutes = palettes.substitutes
    color_count = image.histogram()
    colors_to_replace = []
    
    for i in range(len(colors)):
        if 0 < color_count[i] < 3:
            color = list(colors.keys())[i]
            colors_to_replace.append(color)
  
    data = np.array(image)
    for ny, y in enumerate(data):
        for nx, x in enumerate(data[ny]):
            index_letter = list(colors.keys())[x]
            if index_letter in colors_to_replace:
                x = list(colors.keys()).index(substitutes[index_letter])
                image.putpixel((nx, ny), x)
    if 1 in color_count:
        print('The replace operation was skipped.') 
    else:           
        image.save(out_path)
        
def manual_color_replace(image, colors_to_replace, palette_mode, out_path):
    ''' The 'colors_to_replace' parameter takes a dictionary of '{old : new}' values as input. '''
    colors = palettes.LEGOS[palette_mode]    
    data = np.array(image)
    for ny, y in enumerate(data):
        for nx, x in enumerate(data[ny]):
            index_letter = list(colors.keys())[x]
            if index_letter in colors_to_replace.keys():
                x = list(colors.keys()).index(colors_to_replace[index_letter])
                image.putpixel((nx, ny), x)

    image.save(out_path)     

# =================  INSTRUCTIONS PRINTER  ================= #


def count_quadrants(image):
  size_x, size_y = image.size
  if size_x > 500 or size_y > 500:
    raise Exception('The selected image exceeds the 500px limit set for this function. Please resize the image.') 
  elif size_x < 32 or size_y < 32:
    raise Exception('The selected image is smaller than 32px. Please resize the image.') 
  else:
    if size_x % 50 == 0:
      unit = 50
      quadrants = (size_x//50, size_y//50, unit)
    else:
      unit = 32
      quadrants = (size_x//32, size_y//32, unit)
    if quadrants[0]*quadrants[1] == 0:
         raise Exception('One of the dimensions is lower than the chosen quadrant size. Please resize the image.') 
    return quadrants  

def instructions_by_quadrant(image, out_path, range_x, range_y, unit, quadrant_n, palette_mode):
  print(f'Creating the instructions for quadrant {quadrant_n} ({unit}x{unit} format) of {os.path.basename(out_path)[13:]}')
  plt.figure(figsize=(20, 20))
  for y in range(range_y[0], range_y[1]):
    for x in range(range_x[0], range_x[1]):
      color_label = list(palettes.LEGOS[palette_mode].keys())[image.getpixel((x, y))]
      txt = plt.text(x % unit, y % unit, color_label, ha="center", va="center", color='k', fontsize=12)
      txt.set_path_effects([effects.withStroke(linewidth=3, foreground='w')])
  ax = plt.gca()
  plt.yticks(np.arange(0, unit), labels=[i for i in range(1, unit + 1)])
  plt.xticks(np.arange(0, unit), labels=[i for i in range(1, unit + 1)])
  ax.xaxis.set_minor_locator(AutoMinorLocator(2))
  ax.yaxis.set_minor_locator(AutoMinorLocator(2))
  ax.grid(color='w', lw=3, which='minor')
  plt.imshow(image.crop(box=(range_x[0], range_y[0], range_x[1], range_y[1])))
  plt.savefig(os.path.join(os.path.dirname(out_path), f'{quadrant_n}_{os.path.basename(out_path)}' ), dpi=150, transparent=True, bbox_inches='tight')
  plt.close()

def instructions(image, palette_mode, out_path):
  '''When an image is passed to the function, a set of assembly instructions is printed.
  Only pictures with a resolution between 32px and 500px are accepted.'''
  quadrants_x, quadrants_y, unit = count_quadrants(image)
  quadrant_n = 1
  for quadrant_y in range(quadrants_y):
    for quadrant_x in range(quadrants_x):
      instructions_by_quadrant(image, out_path, (quadrant_x * unit, quadrant_x * unit + unit), (quadrant_y * unit, quadrant_y * unit + unit), unit, quadrant_n, palette_mode)
      quadrant_n += 1

def color_count_printer(image, palette_mode, out_path):
    ''' Count the bricks needed for each color in the pallette and print the required brick quantities. '''
    print('Creating brick quantity requirements and adding them to the log')
    instructions = open(out_path, 'w')
    colors = palettes.LEGOS[palette_mode]
    color_count = image.histogram()
    log_file  = pd.read_csv('brick_quantity_log.csv', index_col=0)    

    instructions.write('Here is what you need:\n\n')
    for i in range(len(colors)):
        if color_count[i] > 0:
            color = list(colors.keys())[i]
            old_log_value = log_file.loc[color, 'quantity']
            log_file.loc[color, 'quantity'] = old_log_value + color_count[i]
            instructions.write (f'Color {color}: {color_count[i]} bricks\n')
    log_file.to_csv('brick_quantity_log.csv')
    instructions.close()
    
# =================  APPLY LEGO EFFECT  ================= #    
    
def legofy(thumbnail_image, brick_image, destination):
    destination = os.path.join(destination, 'lego_' + os.path.basename(thumbnail_image))
    print(destination)
    image = Image.open(thumbnail_image)
    brick = Image.open(brick_image)
    final_image = make_lego_image(image, brick)
    final_image.save(destination)
        
    