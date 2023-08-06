# Imports

from PIL import Image, ImageFilter


class BlurImage(object):
    '''
        Applies Gaussian Blur on the image.
    '''

    def __init__(self, radius):
        self.radius = radius
        '''
            Arguments:
            radius (int): radius to blur
        '''

        # Write your code here
        #print("in constructot")
        self.radius = radius

    def __call__(self, im):
        '''
            Arguments:
            image (numpy array or PIL Image)
            Returns:
            image (numpy array or PIL Image)
        '''

        # Write your code here

        im = im.filter(ImageFilter.GaussianBlur(self.radius))
        print("in call")
        # im.save(r'C:\Users\HP\Pictures\Camera Roll\prabhu3.jpg')
        return im

