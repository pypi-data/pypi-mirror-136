from PIL import Image


class FlipImage(object):
    '''
        Flips the image.
    '''

    def __init__(self, flip_type='horizontal'):
        '''
            Arguments:
            flip_type: 'horizontal' or 'vertical' Default: 'horizontal'
        '''
        self.flipType = flip_type
        # Write your code here

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image-)

            Returns:
            image (numpy array or PIL image)
        '''
        if self.flipType == 'horizontal':
            flippedImage = image.transpose(Image.FLIP_LEFT_RIGHT)
            return flippedImage
        else:
            flippedImage = image.transpose(Image.FLIP_TOP_BOTTOM)
            return flippedImage
