#Imports
from PIL import Image
import json
import numpy as np
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
        self.annotation_file=annotation_file
        self.transforms=transforms
        

    def __len__(self):
        '''
            return the number of data points in the dataset
        '''
        with open(self.annotation_file, 'r') as infile:
            data = infile.read()
            new_data = data.replace('}\n{', '},{')
            self.json_obj = json.loads(f'[{new_data}]')
        self.length=len(self.json_obj)
        return self.length

    def __getitem__(self, idx):
        '''
            return the dataset element for the index: "idx"
            Arguments:
                idx: index of the data element.

            Returns: A dictionary with:
                image: image (in the form of a numpy array) (shape: (3, H, W))  <--//H,W,3
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
        
        
        #gt_boxes
        li=self.json_obj[idx]["bboxes"]
        matrix=[]
        for ite in li :
            temp=[]
            temp.append(ite["category"])
            for i in ite["bbox"]:
                temp.append(i)
            matrix.append(temp)
        dict={}
        dict['gt_bboxes']=matrix

        image=Image.open('data/'+self.json_obj[idx]['img_fn'])
        png=Image.open('data/'+self.json_obj[idx]['png_ann_fn'])

        for transform in self.transforms:
            image=transform.__call__(image)
            # transform.__call__(png)
        
        np_img=np.array(image,dtype=np.float32)/255
        np_png=np.array(png,dtype=np.float32)/255
        np_img=np.rollaxis(np_img,2,0)
        np_png=np.rollaxis(np_png.reshape(*np_png.shape,1),2,0)

        dict['image']=np_img
        dict['gt_png_ann']=np_png
        
        return dict

        