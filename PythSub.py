from bs4 import BeautifulSoup 	# Import parser BeautifulSoup
import urllib					# Import lib ouverture url
import codecs
import os
import time
import re

# ~~~~~ CONSTANTES ~~~~~
SHOW_LIST = "showList.txt"
SERIES_DIR = "D:\Documents\Downloads\SeriesTest"
DOWNLOAD_DIR = "D:\Documents\Downloads"


# ~~~~~ FONCTIONS ~~~~~
def create_show_idList():
	# Ouverture fichier liste des séries encodage UTF-8
	file = codecs.open (SHOW_LIST, 'w', 'utf-8')

	# Mise en place du parser avec URL
	urlAddic7edShows = urllib.urlopen("http://www.addic7ed.com/shows.php")
	addic7edShows = urlAddic7edShows.read()
	urlAddic7edShows.close() # Fermeture site ouvert

	soup = BeautifulSoup(addic7edShows) # Parsing avec BS

	showId = soup.select("tr h3 a") # Recherche de tout les liens <a href="/show/xxxxx">

	for s in showId :
		# print(s.get("href").split('/')[2], " = ", s.text)		# --- Debug
		file.write(s.get("href").split('/')[2] + " = " + s.text + "\n")

def get_date_idList():
	age = time.time() - os.path.getmtime(SHOW_LIST)	# age = epoch actuel - epoch creation du fichier (secondes)
	return age

# ~~~~~ MAIN ~~~~~
try:
   with open(SHOW_LIST): pass			# Tentative d'ouverture du  fichier (verif de son existence)
   if(get_date_idList() >= 864000):		# Plus vieux que 10 jours ?
   	print("showList.txt is older than 10 days, getting it again")
   	create_show_idList()
except IOError:
   print("showList.txt not found, creating it")
   create_show_idList()

# Vérification et création du fichier terminé
# Recherche dans le dossier DL des series necessitant des subs

for i in os.listdir(DOWNLOAD_DIR):
	if(re.match('.*\.txt$', i)):		# Match every .txt files
	 print i

