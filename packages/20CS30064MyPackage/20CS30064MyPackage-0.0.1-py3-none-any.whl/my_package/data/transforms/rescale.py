from PIL import Image
import numpy


class RescaleImage(object):
    '''
        Rescales the image to a given size.
    '''

    def __init__(self, output_size):
        '''
            Arguments:
            output_size (tuple or int): Desired output size. If tuple, output is
            matched to output_size. If int, smaller of image edges is matched
            to output_size keeping aspect ratio the same.
        '''

        self.output_size = output_size

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)

            Note: You do not need to resize the bounding boxes. ONLY RESIZE THE IMAGE.
        '''

        if(type(self.output_size) == int):
            w, h = image.size
            width = None
            height = None
            if (w < h):
                width = self.output_size
                height = self.output_size * h // w
            else:
                height = self.output_size
                width = self.output_size * w // h
            
            resized_img = image.resize((width, height))
            return resized_img
        else:
            resized_img = image.resize(self.output_size)
            return resized_img