#Imports
import os
from PIL import Image, ImageDraw, ImageFont
from isort import file
import numpy as np
from matplotlib.pyplot import draw, fill
from torch import imag

def plot_visualization(dict,index): 

  # The function should plot the predicted segmentation maps and the bounding boxes on the images and save them.
  # Tip: keep the dimensions of the output image less than 800 to avoid RAM crashes.

  path = os.path.realpath(__file__)
  path = path.replace('my_package\\analysis\\visualize.py', 'Outputs\\Bounding Boxes\\')
  path = path.replace('\\', '/')

  image = dict['image']
  image = image*255
  image=Image.fromarray(np.uint8(image)).convert('RGB')

  for j in dict['bboxes']: # for one bbox
      x_min, y_min, x_max, y_max = j['bbox']
      shape = [(x_min, y_min), (x_max, y_max)]
      drawer = ImageDraw.Draw(image)
      drawer.rectangle(shape, outline ="red", width=1) # draws rectangle on the image
      my_font = ImageFont.truetype('arial.ttf', 20) # for bigger font
      drawer.text((x_min,y_min), j['category'], font=my_font, fill = (255, 255, 0))

  image.save(path+str(index)+".jpg") 
  return image


    


