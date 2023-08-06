# Imports
from PIL import Image
import numpy as np


class FlipImage(object):
    '''
        Flips the image.
    '''

    def __init__(self, flip_type='horizontal'):
        '''
            Arguments:
            flip_type: 'horizontal' or 'vertical' Default: 'horizontal'
        '''

        self.flip_type = flip_type

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''

        # Flip the image
        if self.flip_type == 'horizontal':
            image = np.fliplr(image)
        elif self.flip_type == 'vertical':
            image = np.flipud(image)
        else:
            raise ValueError('Invalid flip type')

        # Return the image
        return image
