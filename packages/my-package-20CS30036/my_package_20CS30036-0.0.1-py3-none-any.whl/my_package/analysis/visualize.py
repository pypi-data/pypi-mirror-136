# Imports
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def plot_visualization(image_dict, image, filename, saver):
    '''
        Function to plot the segmentation maps on the image and save them

            Arguments:
            image_dict: Dictionary containing the segmentation annotations
            image: Image to be segmented
        '''

    # Create the image to draw on
    image = Image.fromarray((image * 255).astype(np.uint8)).convert('RGB')
    draw = ImageDraw.Draw(image)

    # Set the font
    font = ImageFont.truetype("arial.ttf", 15)

    # Iterate over the annotations
    for annotation in image_dict['bboxes']:
        # Draw the bounding box
        draw.rectangle(annotation['bbox'], outline='red')

        # Draw the category
        draw.text((annotation['bbox'][0], annotation['bbox'][1]), annotation['category'], font=font, fill='red')

    # Save the image
    if saver == 1:
        image.save('outputs/' + filename + '.png')

    return image
