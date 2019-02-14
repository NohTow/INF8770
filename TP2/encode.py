import numpy as np
from PIL import Image

#https://github.com/ghallak/jpeg-python
#https://stackoverflow.com/questions/7762948/how-to-convert-an-rgb-image-to-numpy-array

#load an image and return it in numpy array format
def load_image(filename):
	img = Image.open(filename)
	img.load()
	datarray = np.asarray(img,dtype="int32")
	#datarray = np.asarray(img,dtype="int8")
	return datarray

#save a numpy array into an image named outfilename
def save_image(datarray, outfilename):
	outimg = Image.fromarray(np.uint8(datarray),"RGB")
	#outimg = Image.fromarray(datarray,"RGB")
	outimg.save(outfilename)

