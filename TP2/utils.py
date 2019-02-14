import numpy as np
from PIL import Image
#https://github.com/ghallak/jpeg-python
#https://stackoverflow.com/questions/7762948/how-to-convert-an-rgb-image-to-numpy-array

#load an image and return it in numpy array format
def load_image(filename):
	img = Image.open(filename)
	return img
	

#save a numpy array into an image named outfilename
def save_image(datarray, outfilename):
	outimg = Image.fromarray(np.uint8(datarray),"RGB")
	#outimg = Image.fromarray(datarray,"RGB")
	outimg.save(outfilename)

def convert_to_array(img):
	img.load()
	datarray = np.asarray(img,dtype="int32")
	return datarray

def load_quantization_table(component):
    # Quantization Table for: Photoshop - (Save For Web 080)
    # (http://www.impulseadventure.com/photo/jpeg-quantization.html)
    if component == 'lum':
        q = np.array([[2, 2, 2, 2, 3, 4, 5, 6],
                      [2, 2, 2, 2, 3, 4, 5, 6],
                      [2, 2, 2, 2, 4, 5, 7, 9],
                      [2, 2, 2, 4, 5, 7, 9, 12],
                      [3, 3, 4, 5, 8, 10, 12, 12],
                      [4, 4, 5, 7, 10, 12, 12, 12],
                      [5, 5, 7, 9, 12, 12, 12, 12],
                      [6, 6, 9, 12, 12, 12, 12, 12]])
    elif component == 'chrom':
        q = np.array([[3, 3, 5, 9, 13, 15, 15, 15],
                      [3, 4, 6, 11, 14, 12, 12, 12],
                      [5, 6, 9, 14, 12, 12, 12, 12],
                      [9, 11, 14, 12, 12, 12, 12, 12],
                      [13, 14, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12]])
    else:
        raise ValueError((
            "component should be either 'lum' or 'chrom', "
            "but '{comp}' was found").format(comp=component))

    return q

	
def quantize(block, component):
    q = load_quantization_table(component)
    return (block / q).round().astype(np.int32)
	
def dequantize(block, component):
    q = load_quantization_table(component)
    return block * q
	
#https://github.com/lot9s/lfv-compression/blob/master/scripts/our_mpeg/zigzag.py
ZIGZAGINVERSE = np.array([[0,  1,  5,  6,  14, 15, 27, 28],
                   [2,  4,  7,  13, 16, 26, 29, 42],
                   [3,  8,  12, 17, 25, 30, 41, 43],
                   [9,  11, 18, 24, 31, 40, 44,53],
                   [10, 19, 23, 32, 39, 45, 52,54],
                   [20, 22, 33, 38, 46, 51, 55,60],
                   [21, 34, 37, 47, 50, 56, 59,61],
                   [35, 36, 48, 49, 57, 58, 62,63]])
ZIGZAGFLATINVERSE = ZIGZAGINVERSE.flatten()
ZIGZAGFLAT = np.argsort(ZIGZAGFLATINVERSE)
def zigzag_single(block):
	return block.flatten()[ZIGZAGFLAT]

def inverse_zigzag_single(array):
	return array[ZIGZAGFLATINVERSE].reshape([8,8])