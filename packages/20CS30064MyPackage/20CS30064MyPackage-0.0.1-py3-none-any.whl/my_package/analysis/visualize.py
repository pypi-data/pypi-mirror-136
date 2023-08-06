from PIL import Image, ImageDraw, ImageFont
import numpy as np
from itertools import chain
import os

def plot_visualization(image_dict, segmentor, relative_filepath):
  '''
  The function plots the predicted segmentation maps and the bounding boxes on the images and save them.
  Arguments:
    image_dict: Dictionary returned by Dataset
    segmentor: Object of InstanceSegmentationModel class
    relative_filepath: Relative filepath to the output image in the target folder
  '''
  jpg_image = image_dict["image"]

  pred_boxes, pred_masks, pred_class, pred_score = segmentor(np.transpose(jpg_image, (-1, 0, 1))/255)

  if(len(pred_score) > 3):                 # Taking the top 3 segmentations
    pred_boxes = pred_boxes[:3]
    pred_masks = pred_masks[:3]
    pred_class = pred_class[:3]
    pred_score = pred_score[:3]
  
  image_boxes = []
  for k in range(len(pred_score)):
    my_list = []
    my_list = list(chain.from_iterable(pred_boxes[k]))
    for j in range(len(my_list)):
      my_list[j] = int(my_list[j])
    image_boxes.append(my_list)
  
  boxed_image = Image.fromarray(np.uint8(jpg_image)).convert('RGB')     # Converting numpy array to PIL image
  
  k = 0
  for j in image_boxes:                # Iterating the list image_boxes, containg lists of four corners of each segmentation box
    x_min, y_min, x_max, y_max = j
    shape = [(x_min, y_min), (x_max, y_max)]
    drawer = ImageDraw.Draw(boxed_image)
    drawer.rectangle(shape, outline ="red", width=3)      # Drawing the box on the image
    my_font = ImageFont.truetype('arial.ttf', 20)
    drawer.text((x_min,y_min), pred_class[k], font=my_font, fill = (255, 255, 0))
    k = k + 1
  

  img_array = np.array(boxed_image)
  for mask in pred_masks:                       # Applying the segmentation masks on the image
    img_array = img_array + ((np.transpose(mask, (1, 2, 0)))*[0, 0, 0.5] * 300)
  
  masked_image = Image.fromarray(np.uint8(img_array)).convert('RGB')

  dirname = os.path.dirname(__file__)                   # Getting the absolute file path
  filepath = os.path.join(dirname, relative_filepath)
  masked_image.save(filepath)                          # Saving the image
  
  return masked_image