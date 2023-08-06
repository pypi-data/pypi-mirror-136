from PIL import Image
import numpy
from random import randrange


class CropImage(object):
    '''
        Performs either random cropping or center cropping.
    '''

    def __init__(self, shape, crop_type='center'):
        '''
            Arguments:
            shape: output shape of the crop (h, w)
            crop_type: center crop or random crop. Default: center
        '''

        self.shape = shape
        self.crop_type = crop_type

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        if (self.crop_type == 'center'):
            width, height = image.size   # Get dimensions
            new_height, new_width = self.shape
            left = (width - new_width)//2
            top = (height - new_height)//2
            right = (width + new_width)//2
            bottom = (height + new_height)//2

            img = image.crop((left, top, right, bottom))  # Centre cropping
            return img

        else:              # Random cropping
            x, y = image.size
            h, w = self.shape

            x1 = randrange(0, x - w)
            y1 = randrange(0, y - h)

            img = image.crop((x1, y1, x1 + w, y1 + h))
            return img

        

 