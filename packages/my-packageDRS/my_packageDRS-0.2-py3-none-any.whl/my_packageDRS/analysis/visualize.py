#Imports
import numpy
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import ImageFont
from numpy import asarray, shape
from PIL import Image
from PIL import ImageDraw
from model import *





#import model
def plot_visualization(pred_boxes,pred_masks,pred_class,pred_score,image_numpy): # Write the required arguments

   # The function should plot the predicted segmentation maps and the bounding boxes on the images and save them.
   # Tip: keep the dimensions of the output image less than 800 to avoid RAM crashes.







   image_numpy = image_numpy.transpose(2, 0, 1)
   image_numpy = image_numpy.transpose(2, 0, 1)
   print(image_numpy.shape)

   mul = [(0.5, 0, 0), (0, 0, 0.5), (0, 0.5, 0)]
   i=0
   for pmask in pred_masks:
      pmask=pmask.transpose(2,0,1)
      pmask=pmask.transpose(2,0,1)
      print(pmask.shape)
      image_numpy = image_numpy+ pmask*mul[i]
      i+=1
      if i>=3:
         break


   im = Image.fromarray((image_numpy * 255.0).astype(numpy.uint8))

   color=["red","blue","green"]

   i=0
   while i<3 and i<len(pred_score):
      print(pred_boxes[i])
      print(pred_score[i])
      img=ImageDraw.Draw(im)
      img.rectangle(pred_boxes[i],outline=color[i])
      img.text((pred_boxes[i][0]),pred_class[i],fill=color[i],align="center")
      i += 1

   image_numpy = numpy.array(im, dtype=float)

   return image_numpy



