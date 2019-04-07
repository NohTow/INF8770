import numpy as np
from PIL import Image
from anytree import Node, RenderTree, PreOrderIter, AsciiStyle
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
    return block.flatten()[ZIGZAGFLAT].astype('float')

def inverse_zigzag_single(array):
	return array[ZIGZAGFLATINVERSE].reshape([8,8])

def encodeHuffman(block):
    #Convert array to string
    temp = np.asarray(block).flatten().astype('str')
    Message = ''.join(temp)
    #Liste qui sera modifié jusqu'à ce qu'elle contienne seulement la racine de l'arbre
    ArbreSymb =[[Message[0], Message.count(Message[0]), Node(Message[0])]] 
    #dictionnaire obtenu à partir de l'arbre.
    dictionnaire = [[Message[0], '']]
    nbsymboles = 1

    #Recherche des feuilles de l'arbre
    for i in range(1,len(Message)):
        if not list(filter(lambda x: x[0] == Message[i], ArbreSymb)):
            ArbreSymb += [[Message[i], Message.count(Message[i]),Node(Message[i])]]
            dictionnaire += [[Message[i], '']]
            nbsymboles += 1

    longueurOriginale = np.ceil(np.log2(nbsymboles))*len(Message) 

    ArbreSymb = sorted(ArbreSymb, key=lambda x: x[1])

    while len(ArbreSymb) > 1:
        #Fusion des noeuds de poids plus faibles
        symbfusionnes = ArbreSymb[0][0] + ArbreSymb[1][0] 
        #Création d'un nouveau noeud
        noeud = Node(symbfusionnes)
        temp = [symbfusionnes, ArbreSymb[0][1] + ArbreSymb[1][1], noeud]
        #Ajustement de l'arbre pour connecter le nouveau avec ses parents 
        ArbreSymb[0][2].parent = noeud
        ArbreSymb[1][2].parent = noeud
        #Enlève les noeuds fusionnés de la liste de noeud à fusionner.
        del ArbreSymb[0:2]
        #Ajout du nouveau noeud à la liste et tri.
        ArbreSymb += [temp]
        #Pour affichage de l'arbre ou des sous-branches
        ArbreSymb = sorted(ArbreSymb, key=lambda x: x[1])  

    ArbreCodes = Node('')
    noeud = ArbreCodes
    #print([node.name for node in PreOrderIter(ArbreSymb[0][2])])
    parcoursprefix = [node for node in PreOrderIter(ArbreSymb[0][2])]
    parcoursprefix = parcoursprefix[1:len(parcoursprefix)] #ignore la racine

    Prevdepth = 0 #pour suivre les mouvements en profondeur dans l'arbre
    for node in parcoursprefix:  #Liste des noeuds 
        if Prevdepth < node.depth: #On va plus profond dans l'arbre, on met un 0
            temp = Node(noeud.name + '0')
            noeud.children = [temp]
            if node.children: #On avance le "pointeur" noeud si le noeud ajouté a des enfants.
                noeud = temp
        elif Prevdepth == node.depth: #Même profondeur, autre feuille, on met un 1
            temp = Node(noeud.name + '1')
            noeud.children = [noeud.children[0], temp]  #Ajoute le deuxième enfant
            if node.children: #On avance le "pointeur" noeud si le noeud ajouté a des enfants.
                noeud = temp
        else:
            for i in range(Prevdepth-node.depth): #On prend une autre branche, donc on met un 1
                noeud = noeud.parent #On remontre dans l'arbre pour prendre la prochaine branche non explorée.
            temp = Node(noeud.name + '1')
            noeud.children = [noeud.children[0], temp]
            if node.children:
                noeud = temp

        Prevdepth = node.depth

    ArbreSymbList = [node for node in PreOrderIter(ArbreSymb[0][2])]
    ArbreCodeList = [node for node in PreOrderIter(ArbreCodes)]

    for i in range(len(ArbreSymbList)):
        if ArbreSymbList[i].is_leaf: #Génère des codes pour les feuilles seulement
            temp = list(filter(lambda x: x[0] == ArbreSymbList[i].name, dictionnaire))
            if temp:
                indice = dictionnaire.index(temp[0])
                dictionnaire[indice][1] = ArbreCodeList[i].name

    MessageCode = []
    longueur = 0 
    for i in range(len(Message)):
        substitution = list(filter(lambda x: x[0] == Message[i], dictionnaire))
        MessageCode += [substitution[0][1]]
        longueur += len(substitution[0][1])
    return(MessageCode, dictionnaire)


def encodeRLE(block):
    temp = np.asarray(block).flatten().astype('str')
    Message = ''.join(temp)
    count = 2
    prev = ''
    lst = []
    for character in Message:
        if character != prev:
            if prev:
                entry = (prev,count)
                lst.append(entry)
            count = 1
            prev = character
        else:
            count += 1
    else:
        try:
            entry = (character,count)
            lst.append(entry)
            
        except Exception as e:
            print("Exception encountered {e}".format(e=e))
        
    return lst

def decodeRLE(blockList):
    MessageOriginal = ""
    for character, count in blockList:
        MessageOriginal += character * count
    return MessageOriginal

def decodeHuffman(Message, dictionnaire):
    res = ""
    while Message:
        for k in dictionnaire:
            if Message.startswith(k[1]):
                res+=k[0]
                Message = Message[len(k[1]):]
      
    Message = res 
    resultat = []
    while Message:
        temp = Message.split(".",1)[0] + "."
        Message = Message[len(temp):]
        temp += Message[ 0 : 1]
        Message = Message[1:]
        resultat.append(int((temp.split(".")[0])))
    
    
      
    return np.asarray(resultat)
# Diviser le message decode de sorte a separer les elements et les mettres dans un tableau
    
