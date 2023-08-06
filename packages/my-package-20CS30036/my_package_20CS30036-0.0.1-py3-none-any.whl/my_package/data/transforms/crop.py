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

        # Get the height and width of the image
        width, height = image.size

        # Check if the crop type is random or center
        if self.crop_type == 'center':
            left = width / 2 - self.width / 2
            right = left + self.width
            top = height / 2 - self.height / 2
            bottom = top + self.height
        elif self.crop_type == 'random':
            left = random.uniform(0, width - self.width)
            right = left + self.width
            top = random.uniform(0, height - self.height)
            bottom = top + self.height
        else:
            raise ValueError('Invalid crop type')

        # Crop the image
        image = image.crop((left, top, right, bottom))

        # Return the image
        return image
