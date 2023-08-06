from asyncio.windows_events import NULL
import json_lines
from PIL import Image
import os
import numpy as np

# from my_package.data.transforms import FlipImage, RescaleImage, BlurImage, CropImage, RotateImage
# from transforms.blur import BlurImage
# from transforms.crop import CropImage
# from transforms.flip import FlipImage
# from transforms.rescale import RescaleImage
# from transforms.rotate import RotateImage


class Dataset(object):
    '''
        A class for the dataset that will return data items as per the given index
    '''

    def __init__(self, annotation_file, transforms=None):
        '''
            Arguments:
            annotation_file: path to the annotation file
            transforms: list of transforms (class instances)
                        For instance, [<class 'RandomCrop'>, <class 'Rotate'>]
        '''

        self.annotation_file_path = annotation_file
        self.transformsToBeDone = transforms

    def __len__(self):
        '''
            return the number of data points in the dataset
        '''
        i = 0
        with open(self.annotation_file_path, 'rb') as file:
            for item in json_lines.reader(file):
                i = i+1
        return i

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

        i = 0
        SelectedData = NULL

        with open(self.annotation_file_path, 'rb') as file:
            for item in json_lines.reader(file):
                if i == idx:
                    SelectedData = item
                    break
                i = i+1

        CurrentFilepath = os.path.realpath(__file__)
        CurrentFilepath = CurrentFilepath.replace(
            'my_package\data\dataset.py', 'data/')
        Imagespath = CurrentFilepath.replace('\\', '/')

        pathOfRequiredImage = Imagespath + SelectedData['img_fn']
        OriginalImage = Image.open(pathOfRequiredImage)

        pathOfRequiredPng = Imagespath + SelectedData['png_ann_fn']
        pngImage = Image.open(pathOfRequiredPng)

        numpyArrayOfOriginalImage = np.array(OriginalImage)
        numpyArrayOfOriginalImage = numpyArrayOfOriginalImage/255.0

        FinalTransformedImage = OriginalImage

        for transform in self.transformsToBeDone:
            TempObj = transform
            FinalTransformedImage = TempObj(FinalTransformedImage)
        
        # FinalTransformedImage.show()

        numpyArrayOfFinalTransformedImage =np.array(FinalTransformedImage)


        numpyArrayOfPngImage = np.array(pngImage)
        numpyArrayOfPngImage = numpyArrayOfPngImage/255.0


        final_list = []
        for item in SelectedData['bboxes']:
            list = []
            list.append(item['category'])
            item['bbox'][2]=item['bbox'][2]+item['bbox'][0]
            item['bbox'][3]=item['bbox'][3]+item['bbox'][1]
            list = list + item['bbox']
            final_list.append(list)

        MyDictionary = {

            "image":numpyArrayOfOriginalImage,
            "transformedImage": numpyArrayOfFinalTransformedImage,
            "gt_png_ann": numpyArrayOfPngImage,
            "gt_bboxes": final_list

        }

        return MyDictionary