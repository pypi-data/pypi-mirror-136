# Imports


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

        # Check if the output_size if of tuple or int
        if(isinstance(output_size, int)):
            self.option = 1
        else:
            self.option = 2

        self.output_size = output_size

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)

            Note: You do not need to resize the bounding boxes. ONLY RESIZE THE IMAGE.
        '''

        # Resize the image
        if self.option == 1:
            ratio = image.size[0] / image.size[1]

            if(image.size[0] > image.size[1]):
                height = self.output_size
                width = height * ratio
            else:
                width = self.output_size
                height = width / ratio

            image = image.resize(int(width), int(height))
        else:
            image = image.resize(self.output_size)

        # Return the image
        return image
