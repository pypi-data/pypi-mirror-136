#Imports
from PIL import Image,ImageFilter

class BlurImage(object):
    '''
        Applies Gaussian Blur on the image.
    '''
    
    def __init__(self, radius):
        '''
            Arguments:
            radius (int): radius to blur
        '''
        self.radius=radius
    
    def get_name(self):
        return ('Blur_radius_'+str(self.radius))
    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL Image)

            Returns:
            image (numpy array or PIL Image)
        '''
        # image.show()
        gaussImage=image.filter(ImageFilter.GaussianBlur(self.radius))
        # gaussImage.show()
        return gaussImage

