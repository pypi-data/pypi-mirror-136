#Imports
from turtle import shape
from PIL import Image

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
        self.newheight , self.newwidth=shape
        self.crop_type=crop_type
    def get_name(self):
        return ('crop_type_'+self.crop_type)
    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)

            Returns:
            image (numpy array or PIL image)
        '''
        image.show()
        if(self.crop_type=='center'):
            width,height=image.size
            left=(width-self.newwidth)/2
            top=(height-self.newheight)/2
            right=(width+self.newwidth)/2
            bottom=(height+self.newheight)/2

            cropped=image.crop((left,top,right,bottom))
            # cropped.show()
            return cropped

        else :
            top=self.newheight
            right=self.newwidth
            cropped=image.crop(1,top,right,2)
        
            # cropped.show()
            return cropped
            

        

 