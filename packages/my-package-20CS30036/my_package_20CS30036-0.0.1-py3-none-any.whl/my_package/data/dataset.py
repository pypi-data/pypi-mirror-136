# Imports
from PIL import Image
import numpy as np
import json


# A class for the dataset that will return data items as per the given index
class Dataset(object):
    def __init__(self, annotation_file, transforms=None):
        '''
            Initialize the dataset with the given annotation file.
            Arguments:
                annotation_file: Path to annotation file
                transforms: List of transformation classes
        '''

        self.transforms = transforms
        with open(annotation_file, 'r') as f:
            self.annotation_list = list(f)

    def __len__(self):
        '''
            Return the length of the dataset.
            Returns: The length of the dataset.
        '''

        return len(self.annotation_list)

    def __getitem__(self, idx):
        '''
            return the dataset element for the index: "idx"
            Arguments:
                idx: index of the data element.

            Returns: A dictionary with:
                image: image (in the form of a numpy array) (shape: (3, H, W))
                gt_png_ann: the segmentation annotation image (in the form of a numpy array) (shape: (1, H, W))
                gt_bboxes: N X 5 array where N is the number of bounding boxes, each 
                            consisting of [class, x1, y1, x2, y2]
                            x1 and x2 lie between 0 and width of the image,
                            y1 and y2 lie between 0 and height of the image.
        '''

        # Get the annotation for the given index
        annotation = json.loads(self.annotation_list[idx])

        # Get the image as a numpy array
        image = Image.open('data/' + annotation['img_fn'])

        # Perform the desired transformations on the image
        if self.transforms:
            for transform in self.transforms:
                image = transform(image)

        # Get the numpy array of the image
        image = np.array(image).transpose((2, 0, 1))

        # Get the segmentation annotation as a numpy array
        mask = Image.open('data/' + annotation['png_ann_fn'])
        mask = np.array(mask)

        # Scale the values in the arrays to be with [0, 1]
        image = image / 255
        mask = mask / 255

        # Get the bounding boxes
        bboxes = []
        for bbox in annotation['bboxes']:
            temp_list = []
            temp_list.append(bbox['category'])
            temp_list = temp_list + bbox['bbox']
            bboxes.append(temp_list)

        # Return the image, mask and the bounding boxes
        return {'image': image, 'mask': mask, 'gt_bboxes': bboxes}
