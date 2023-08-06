#Imports
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
        self.degrees=degrees
    def get_name(self):
        return ('Rotate_degrees_'+str(self.degrees))
    def __call__(self, sample):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        # sample.show()
        rotated=sample.rotate(self.degrees)
        # rotated.show()
        return rotated