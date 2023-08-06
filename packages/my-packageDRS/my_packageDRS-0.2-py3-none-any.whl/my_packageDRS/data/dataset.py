# Imports
import json_lines
import numpy
import model
from model import InstanceSegmentationModel
from PIL import Image
from numpy import asarray
import analysis
from analysis import visualize
#from visualize import plot_visualization
from data import transform
from data.transform.blur import BlurImage
from data.transform.crop import CropImage
from data.transform.flip import FlipImage
from data.transform.rescaleimage import RescaleImage
from data.transform.rotate import RotateImage


class Dataset(object):
    '''
        A class for the dataset that will return data items as per the given index
    '''

    def __init__(self, annotation_file, transforms=None, List=[]):
        '''
            Arguments:
            annotation_file: path to the annotation file
            transforms: list of transforms (class instances)
                        For instance, [<class 'RandomCrop'>, <class 'Rotate'>]
        '''
        self.annotation_file = annotation_file
        self.transforms = transforms

        self.List = List
        path = self.annotation_file
        with open(path) as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                self.List.append(item)

    def __len__(self):
        '''
            return the number of data points in the dataset
        '''
        return len(self.List)

    def __getitem__(self, idx):
        '''
            return the dataset element for the index: "idx"
            Arguments:
                idx: index of the data element.
            Returns: A dictionary with:
                image: image (in the form of a numpy array) (shape: (3, H, W))
                gt_png_ann: the segmentation annotation image (in the form of a numpy array) (shape: (1, H, W))
                gt_bboxes: N X 5 array where N is the number of bounding boxes, each
                            consisting of [class, x1, y1, x2, y2]
                            x1 and x2 lie between 0 and width of the image,
                            y1 and y2 lie between 0 and height of the image.
            You need to do the following,
            1. Extract the correct annotation using the idx provided.done
            2. Read the image, png segmentation and convert it into a numpy array (wont be necessary
                with some libraries). The shape of the arrays would be (3, H, W) and (1, H, W), respectively.done
            3. Scale the values in the arrays to be with [0, 1].done
            4. Perform the desired transformations on the image.done
            5. Return the dictionary of the transformed image and annotations as specified.done


        '''

        imgdict = dict()
        inidict = dict()
        for item in self.List:
            if (int)(item['img_id']) == idx:
                inidict = item

        imname = inidict['img_fn']
        imname = imname[5:]

        print(imname)
        imgdict['imgname'] = imname

        img = Image.open('C:/Users/HP/PycharmProjects/pythonProject/' + imname)

        for str in self.transforms:
            img = str(img)

        image_numpy = numpy.array(img, dtype=float) / 255
        image_numpy = image_numpy.transpose(2, 0, 1)
        imgdict['image'] = image_numpy

        obhj = InstanceSegmentationModel()
        arra = obhj(image_numpy)

        pred_boxes = arra[0]
        pred_masks = arra[1]
        pred_class = arra[2]
        pred_score = arra[3]
        imgdict['gt_png_ann'] = visualize.plot_visualization(pred_boxes, pred_masks, pred_class, pred_score, image_numpy)

        L = []
        for i in range(len(pred_score)):
            li = []
            li.append(pred_class[i])
            li.append(pred_boxes[i][0][0])
            li.append(pred_boxes[i][0][1])
            li.append(pred_boxes[i][1][0])
            li.append(pred_boxes[i][1][1])
            L.append(li)

        imgdict['gt_bboxes'] = L

        return imgdict
