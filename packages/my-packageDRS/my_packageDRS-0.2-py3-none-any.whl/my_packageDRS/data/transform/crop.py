from PIL import Image

class CropImage(object):
    '''
        Performs either random cropping or center cropping.
    '''

    def __init__(self,shape,crop_type='center'):
        '''
            Arguments:
            shape: output shape of the crop (h, w)
            crop_type: center crop or random crop. Default: center
        '''

        # Write your code here

        # print(self.shape)

        self.crop_type = crop_type
        self.shape = shape
        print(self.shape)
        print(self.crop_type)

    def __call__(self, image):
        '''
            Arguments:
            image (numpy array or PIL image)
            Returns:
            image (numpy array or PIL image)
        '''

        # Write your code here
        if(self.crop_type=='center'):
            width,height=image.size
            left =(width-self.shape[0])/2
            top = (height-self.shape[1])/2
            right = (width+self.shape[0])/2
            bottom =  (height+self.shape[1])/2
        else:
            left = 0
            top = 0
            right = self.shape[0]
            bottom = self.shape[1]

        im1 = image.crop((left, top, right, bottom))
        return im1






