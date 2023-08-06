# Imports
import random


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

        # Write your code here

        self.height = shape[0]
        self.width = shape[1]
        self.crop_type = crop_type

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''

        # Write your code here

        width, height = image.size

        if self.crop_type == 'random':
            left = random.uniform(0, width-self.width)
            right = left + self.width
            top = random.uniform(0, height-self.height)
            bottom = top + self.height

        else:
            left = width/2 - self.width/2
            right = left + self.width
            top = height/2 - self.height/2
            bottom = top + self.height

        newImage = image.crop((left, top, right, bottom))
        
        return newImage
