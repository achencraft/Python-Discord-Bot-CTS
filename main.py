import sys, os, shutil, re
import PIL.Image as Image
from dotenv import dotenv_values
from pathlib import Path


#Programme de génération automatique des schémas de ligne CTS pour chestcommands
#Usage : main.py <fichier_couleurs_html>
#
#Nécéssite un répertoire "in" avec le modèle de base
#Sortie : un repertoire nommé avec le code_couleur contenant les fichiers


def generer_images(color):


    os.makedirs(config['OUTPUT_DIRECTORY']+"/textures",exist_ok=True)

    #ouvrir repertoire d'entree
    list = os.listdir(config['INPUT_DIRECTORY'])

    os.makedirs(config['OUTPUT_DIRECTORY']+"/textures/"+color.lower(),exist_ok=True)
    for file in list:

        #Copier les fichiers dans le repertoire de sortie        
        shutil.copyfile(config['INPUT_DIRECTORY']+"/"+file, config['OUTPUT_DIRECTORY']+"/textures/"+color.lower()+"/"+file)

        #Modifier la couleur des fichiers de sortie
        change_color(config['OUTPUT_DIRECTORY']+"/textures/"+color.lower()+"/"+file,color)



def change_color(nom,color):
    
    im = Image.open(nom)
    largeur,hauteur=im.size
    pix = im.load() # pix est notre tableau de pixels

    modele_color = config['MODELE_COLOR_CODE']
    (r,v,b) = (int(modele_color[0:2],16),int(modele_color[2:4],16),int(modele_color[4:6],16))
    (r1,v1,b1) = (int(color[0:2],16),int(color[2:4],16),int(color[4:6],16))

    print("création - "+nom)
    for y in range(hauteur):
        for x in range(largeur):
            if pix[x,y] == (r,v,b) :
                pix[x,y] = (r1,v1,b1)
    # sauvegarde
    im.save(nom)


def generer_fichiers(color):


    os.makedirs(config['OUTPUT_DIRECTORY']+"/models",exist_ok=True)


    list = os.listdir(config['OUTPUT_DIRECTORY']+"/textures/"+color.lower())

    os.makedirs(config['OUTPUT_DIRECTORY']+"/models/"+color.lower(),exist_ok=True)
    for file in list:

        filename = file.replace(".png",".json")
        print("création - "+config['OUTPUT_DIRECTORY']+"/models/"+color.lower()+"/"+filename)

        f = open(config['OUTPUT_DIRECTORY']+"/models/"+color.lower()+"/"+filename, "w")

        data = '''{
    "parent": "item/generated",
    "textures": {
        "layer0": "item/cts/'''+color.lower()+'''/'''+file.split('.')[0]+'''"
    }
}'''

        f.write(data)
        f.close()


def generer_fichier_principal(color,start_damage):

    valeur_damage_base = float(config['DAMAGE_BASE'])

    list = os.listdir(config['INPUT_DIRECTORY'])

    f = open(config['OUTPUT_DIRECTORY']+"/out.json", "a")
    print("création - "+config['OUTPUT_DIRECTORY']+"/"+color.lower()+".json")

    for file in list:

        #damage = valeur_damage_base*start_damage
        damage = start_damage/1561

        data = '''{
"predicate": {
    "damaged": 0,
    "damage": '''+str(damage)+'''
},
"model": "item/cts/menu/'''+color+'''/'''+file.split('.')[0]+'''"
},
'''
        f.write(data)
        start_damage = start_damage + 1.
    f.close()

if __name__ == '__main__':

    pattern = re.compile(r"[a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]", re.IGNORECASE)
    config = dotenv_values(".env")

    args = sys.argv[1:]
    print(args)

    if not Path(args[0]).is_file():
        print("Le fichier n'est pas valide : "+args[0])
        exit()


    file = open(args[0], 'r')
    Lines = file.readlines()

    for line in Lines:
        (color,start_damage) = line.lower().split(',')

        if not pattern.match(color):
            print("Le code couleur n'est pas au bon format : "+color)
            exit()

        if not start_damage[:-1].isdigit():
            print("Le damage n'est pas un entier : "+start_damage[:-1])
            exit()


        generer_images(color)
        generer_fichiers(color)
        generer_fichier_principal(color,float(start_damage))
