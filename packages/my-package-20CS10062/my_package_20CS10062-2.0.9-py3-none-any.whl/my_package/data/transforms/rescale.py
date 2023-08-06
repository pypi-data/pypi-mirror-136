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
        self.outputSize = output_size

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)

            Note: You do not need to resize the bounding boxes. ONLY RESIZE THE IMAGE.
        '''
        if isinstance(self.outputSize, int):
            width,height=image.size
            aspectRatio=width//height
            new_height=0
            new_width=0
            if width>height:
                new_height=self.outputSize
                new_width=aspectRatio*new_height
            else:
                new_width=self.outputSize
                new_height=new_width//aspectRatio
            
            rescaled_image = image.resize(new_width,new_height)
            return rescaled_image

        elif isinstance(self.outputSize, tuple):
            rescaled_image = image.resize(self.outputSize)
            return rescaled_image
        else:
            print("Wrong type of output size is given")