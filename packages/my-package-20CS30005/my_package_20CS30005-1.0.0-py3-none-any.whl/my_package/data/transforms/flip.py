# Imports
from PIL import Image


class FlipImage(object):
    '''
        Flips the image.
    '''

    def __init__(self, flip_type='horizontal'):
        '''
            Arguments:
            flip_type: 'horizontal' or 'vertical' Default: 'horizontal'
        '''

        # Write your code here

        self.flip_type = flip_type

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''

        # Write your code here

        if self.flip_type == 'horizontal':
            newImage = image.transpose(method=Image.FLIP_LEFT_RIGHT)
        else:
            newImage = image.transpose(method=Image.FLIP_TOP_BOTTOM)

        return newImage
