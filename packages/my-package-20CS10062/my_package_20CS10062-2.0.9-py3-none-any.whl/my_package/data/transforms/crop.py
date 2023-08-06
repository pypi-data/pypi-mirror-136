from email.base64mime import header_length
from PIL import Image
from random import randrange


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
        self.ShapeOfTheImage=shape
        self.type=crop_type

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        if (self.type=='center'):
            width,height = image.size
            requiredHeight,requiredWidth=self.ShapeOfTheImage
            left=(width-requiredWidth)/2
            right=(width+requiredWidth)/2
            top=(height-requiredHeight)/2
            bottom=(height+requiredHeight)/2
            croppedImage = image.crop((left, top, right, bottom))
            return croppedImage
        else :
            image_Size=image.size
            new_height,new_width=self.ShapeOfTheImage
            left_max=image_Size[0]-new_width
            top_max=image_Size[1]-new_height
            random_left=randrange(0, left_max//2 + 1) * 2
            random_top=randrange(0, top_max//2 + 1) * 2
            croppedImage=image.crop(random_left,random_top,random_left+new_width,random_top+new_height)
            return croppedImage
        
        

        

 