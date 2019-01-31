#!/bin/python
# -*- coding: utf-8 -* 
#import sys

import numpy as np
import regex as re
import random
import time

def compressString(Message):
	LUToctetsdispo = [True] * 256
	dictsymb =[Message[0]]
	LUToctetsdispo[ord(Message[0])] = False
	nbsymboles = 1
	for i in range(1,len(Message)):
		if Message[i] not in dictsymb:
			dictsymb += [Message[i]]
			LUToctetsdispo[ord(Message[i])] = False  #Octet utilisé
			nbsymboles += 1
			
	#print("longueur originale : " + str(np.ceil(np.log2(nbsymboles))*len(Message)))
	dictsymb = []  #Dictionnaire des substitutions
	debut = ord(Message[0])  # Origine trouver un code de substitution. Et pour avoir des caractères imprimables...

	remplacementpossible = True
	while remplacementpossible == True:
		#Recherche des paires
		paires = []
		skipIt = False
		#for in in range(0, len(Message)-1):
		if(Message[len(Message)-2] == '\\'):
			bornePlus = len(Message)-2
		else:
			bornePlus = len(Message)-1
		for i in range(0,bornePlus):
		#-2 until fix of the \n alone
			if(skipIt == True):
				skipIt = False
				continue
			if(Message[i+1]=='\\'):
				temppaire = Message[i]+Message[i+1]+Message[i+2]
				
			elif(Message[i]=='\\'):
				temppaire = Message[i]+Message[i+1]+Message[i+2]
				if(Message[i+2]=='\\'):
					temppaire+=Message[i+3]
				skipIt = True
            
			else:
				temppaire = Message[i]+Message[i+1]
			if not list(filter(lambda x: x[0] == temppaire, paires)): #Si la liste retournée par filter est vide.
				#print (temppaire)
				paires += [[temppaire,len(re.findall(temppaire, Message, overlapped = True))]]

		#Trouve la paire avec le plus de répétitions.
		paires = sorted(paires, key=lambda x: x[1], reverse = True)

		if paires[0][1] > 1:
			#Remplace la paire
			#print(paires)
			#print("La paire ",paires[0][0], " est la plus fréquente avec ",paires[0][1], "répétitions")
			#Cherche un octet non utilisé
			while debut <256 and LUToctetsdispo[debut] == False:
				debut += 1
			if debut < 256:     
            #On substitut
				Message = Message.replace(paires[0][0], chr(debut))
				Message = Message.replace("\\","")
				Message = re.escape(Message)
				#print(Message)
				LUToctetsdispo[debut] = False
				dictsymb += [[paires[0][0], chr(debut)]]
			else:
				remplacementpossible = False 
				# Si on n'a plus d'octet disponible, on ne peut plus faire de remplacement
				print("Il n'y a plus d'octets disponible!") #Bien sûr, ce n'est pas exact car la recherche commence à Message[0]
        
			#print(Message)
			#print(dictsymb)
		else:
			remplacementpossible = False
			#print("taille finale : " + str(np.ceil(np.log2(nbsymboles))*len(Message)))
	#print("-----")
	#print(dictsymb)
	#print(len(Message))
	#print(len(dictsymb)*3)
	#print(np.ceil(np.log2(nbsymboles))*len(Message))
	#print("-----")
	# Le message à envoyer ne comporte pas les \\ utiles pour la regex
	Message = Message.replace("\\","")
	return len(Message) + len(dictsymb)*3
	
	#ancien return
	#return np.ceil(np.log2(nbsymboles))*len(Message)
	#charRange=["AB","CD","KE","ZK","JW"]
#si on ajoute des paires, i doit être incrémenté de 2
charRange="ABCDEFG"	
tailleEspace = len(charRange)
nomFichier = "output_"+charRange+"_.csv"
file = open(nomFichier,"w")
file.write("Taille de base;Taille compressé;Gain de taille;Temps de compression;Coefficient de compression \n")

nbIteration = 20
for i in range(10,1500,25):
	sommeTaille = 0
	sommeTime = 0
	for j in range(0,nbIteration):
		compteur = 0
		msg = ""
		while(compteur < i):
			char = charRange[random.randint(0,tailleEspace-1)]
			msg += char
			compteur += 1
		#print(msg)
		timeStart = time.clock()
		sommeTaille += compressString(msg)
		sommeTime += time.clock()-timeStart
		#print(sommeTaille)
	
	#print(timeEnd-timeStart)
	msgToWrite = (str(i)+";"+str(sommeTaille/nbIteration)+";"+str(i-sommeTaille/nbIteration)+";"+str(sommeTime/nbIteration)+";"+str(1-((sommeTaille/nbIteration)/i))+"\n").replace(".",",")
	#msgToWrite = (str(i)+";"+str(sommeTaille/nbIteration)+";"+str(i-sommeTaille/nbIteration)+"\n").replace(".",",")
	file.write(msgToWrite)
	print("Pour les messages de taille : " + str(i) + " la taille moyenne compressée est : " + str(sommeTaille/nbIteration)+" le gain de taille est de : "+str(i-sommeTaille/nbIteration))
		

file.close()
