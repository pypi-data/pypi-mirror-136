import os
import numpy as np
import json
from PIL import Image


class Dataset(object):
    '''
        A class for the dataset that will return data items as per the given index
    '''

    def __init__(self, annotation_file, transforms = None):
        '''
            Arguments:
            annotation_file: path to the annotation file
            transforms: list of transforms (class instances)
                        For instance, [<class 'RandomCrop'>, <class 'Rotate'>]
        '''

        self.transforms = transforms
        
        with open(annotation_file, 'r') as json_file:    # Accessing the annotations.jsonl file
            self.json_list = list(json_file)
        
        

    def __len__(self):
        '''
            return the number of data points in the dataset
        '''
        return len(self.json_list)
        
        

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

            You need to do the following, 
            1. Extract the correct annotation using the idx provided.
            2. Read the image, png segmentation and convert it into a numpy array (wont be necessary
                with some libraries). The shape of the arrays would be (3, H, W) and (1, H, W), respectively.
            3. Scale the values in the arrays to be with [0, 1].
            4. Perform the desired transformations on the image.
            5. Return the dictionary of the transformed image and annotations as specified.
        '''

        data_dict = {}

        idx_dictionary = json.loads(self.json_list[idx])         # Stores the idx-th dictionary
        
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, '../../data/')

        jpg_image = Image.open(filepath + idx_dictionary["img_fn"])

        for transform_obj in self.transforms:       # Applying all the transforms
            jpg_image = transform_obj(jpg_image)
        
        data_dict["image"] = np.array(jpg_image)     # Storing the jpg file in the dictionary

        png_image = Image.open(filepath + idx_dictionary["png_ann_fn"])
        data_dict["gt_png_ann"]  = np.array(png_image)     # Storing png file in the dictionary
        

        final_list = []
        bboxes_list = idx_dictionary["bboxes"]
        for i in bboxes_list:
            temp_list = []
            temp_list.append(i["category"])
            temp_list += i["bbox"]
            temp_list[3] += temp_list[1]     # (class, x1, y1, w, h) -> (class, x1, y1, x2, y2)
            temp_list[4] += temp_list[2]
            final_list.append(temp_list)
        
        data_dict["gt_bboxes"] = final_list       # Storing the required list in dictionary

        
        return data_dict

'''
def main():
    obj = Dataset(r'C:/Users/anami/OneDrive/Documents/Python_DS_Assignment/data/annotations.jsonl', [BlurImage(5)])
    print(obj[4])


if __name__ == '__main__':
    main()
'''