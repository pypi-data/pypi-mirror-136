# Imports
from PIL import Image


class RotateImage(object):
    '''
        Rotates the image about the centre of the image.
    '''

    def __init__(self, degrees):
        '''
            Arguments:
            degrees: rotation degree.
        '''

        # Write your code here
        self.requiredRotation = degrees

    def __call__(self, sample):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        rotatedImage = sample.rotate(self.requiredRotation, expand=True)
        return rotatedImage
