import numpy as np
from PIL import Image
from utils import * 
import argparse
from scipy import fftpack
import sys
#https://github.com/ghallak/jpeg-python
#https://stackoverflow.com/questions/7762948/how-to-convert-an-rgb-image-to-numpy-array

def main():
	fichier = open("data.txt", "w")
	#Partie 0 : ouverture de l'image
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help="path to the input image")
	parser.add_argument("output", help="path to the output image")
	#for optional input
	#parser.add_argument("-i", help="path to the input image",default="input.jpg")
	#parser.add_argument("-o", help="path to the output image",default="output.jpg")
	args = parser.parse_args()
	input_file = args.input
	output_file = args.output
	image = load_image(input_file)
	#Partie 1 : conversion RGB/Y'CbCr
	#YCbCr = image.convert('YCbCr')
	array = convert_to_array(image)
	lgOrignal = sys.getsizeof(array)
	
	#Partie 2/3 : Découpage en bloc de pixel + DCT
	#On récupère la dimension de l'image et on vérifie que ce sont des multiples de 8 
	rows, cols = array.shape[0], array.shape[1]
	if rows % 8 == cols % 8 == 0:
		blocks_count = rows // 8 * cols // 8 
		#le nombre de bloc est égal à la largeur divisée par 8 multiplié par la hauteur divisé par 8
	else:
		raise ValueError(("La hauteur et la largeur de l'image doivent être des multiples de 8"))
		
	DictionnaireFull = []
	MessageRLEFinal=[]
	imageDecompres = ""
	#On parcourt chaque block, et chaque canal de chaque bloc
	for i in range(0, rows, 8):
		for j in range(0, cols, 8):
			for k in range(3):
				block = array[i:i+8, j:j+8, k]
				
				#on effectue la dct sur le bloc, voir https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.fftpack.dct.html
				array[i:i+8, j:j+8, k] = fftpack.dct(fftpack.dct(block.T, axis=0, norm='ortho').T,axis = 1, norm='ortho')
				#on quantifie chaque bloc
				array[i:i+8, j:j+8, k] = quantize(array[i:i+8, j:j+8, k],'lum' if k == 0 else 'chrom')
				Message, Dictionnaire = encodeHuffman(zigzag_single(array[i:i+8, j:j+8, k]))
				DictionnaireFull.append(Dictionnaire)
				MessageRLEFinal.append(encodeRLE(Message))
	
	#La taille de l'image compressée est égale au code RLE + le dictionnaire
	lgFinal = sys.getsizeof(MessageRLEFinal)
	lgFinal = lgFinal + sys.getsizeof(DictionnaireFull)
	
	print("Le taux de compression est de "+str(1-(lgFinal/lgOrignal)))
	
	#Partie 6 bis : Décodage RLE / Huffman
	
	decodedRLE = []
	decodedHuffman = []
	for i in range(0, len(MessageRLEFinal),1):
		decodedRLE.append(decodeRLE(MessageRLEFinal[i]))
		#print(decodeHuffman(decodedRLE[0], DictionnaireFull[0]))
		decodedHuffman.append(decodeHuffman(decodedRLE[i], DictionnaireFull[i]))
	imageDecompres = np.zeros((rows,cols,3))
	
	z = 0
	#Partie 2/3/4 bis : Retour en Y'CbCr, déquantification et IDCT
	for i in range(0, rows, 8):
		for j in range(0, cols, 8):
			for k in range(3): 
				imageDecompres[i:i+8, j:j+8,k] = inverse_zigzag_single(decodedHuffman[z])
				
				#on déquantifie
				imageDecompres[i:i+8, j:j+8, k] = dequantize(imageDecompres[i:i+8, j:j+8, k],'lum' if k == 0 else 'chrom')
				
				#on effectue la dct inverse sur chaque bloc
				imageDecompres[i:i+8, j:j+8, k] = fftpack.idct(fftpack.idct(imageDecompres[i:i+8, j:j+8, k].T,axis=0, norm='ortho').T,axis=1,norm='ortho')
				z=z+1
		
	#Partie 1 bis : conversion Y'CbCr/RGB
	image = Image.fromarray(np.uint8(imageDecompres))
	#image = image.convert("RGB")
	save_image(image, output_file)
	
	return 1

	
	

if __name__ == "__main__":
    main()
