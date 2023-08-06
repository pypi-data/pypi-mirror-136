#Imports
from PIL import Image
from numpy import imag

class FlipImage(object):
    '''
        Flips the image.
    '''

    def __init__(self, flip_type='horizontal'):
        '''
            Arguments:
            flip_type: 'horizontal' or 'vertical' Default: 'horizontal'
        '''
        self.flip_type=flip_type

    def get_name(self):
        return ( 'Flip_type_'+self.flip_type )   
    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        # image.show()

        if(self.flip_type=='horizontal'):
            hori_flippedImage=image.transpose(Image.FLIP_LEFT_RIGHT)
            # hori_flippedImage.show()
            return hori_flippedImage
        else:
            vert_flippedimage=image.transpose(Image.FLIP_TOP_BOTTOM)
            # vert_flippedimage.show()
            return vert_flippedimage

       