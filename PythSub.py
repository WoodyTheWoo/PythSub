# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup 	# Import parser BeautifulSoup
import urllib					# Import lib ouverture url
import codecs					# Import char coding
import os						# Import OS methods
import time						# Import gestion temps
import re						# Import regex expressions
import ConfigParser				# Import gestion id series

# ~~~~~ CONSTANTES ~~~~~
SHOW_LIST = "showList.txt"							# Nom fichier contenant les id addic7ed
SERIES_DIR = "D:\Documents\Downloads\SeriesTest"	# Dir où sont copiées les séries une fois traitées
DOWNLOAD_DIR = "D:\Documents\Downloads"				# Dir à crawler pour trouver les épisodes


# ~~~~~ DEBUG FONCTIONS ~~~~~
DEBUG = 1											# Active / Desactive debug

def debug_print_info(function_name, message_info):
	if(DEBUG):
		print "[DEBUG] [" + function_name + "] - " + message_info


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

	file.write("[ShowsId]\n")
	
	for s in showId :
		# print(s.get("href").split('/')[2], " = ", s.text)			# --- Debug
		file.write(s.text.replace("(", "").replace(")", "") + " = " + s.get("href").split('/')[2] + "\n")

def get_date_idList():
	age = time.time() - os.path.getmtime(SHOW_LIST)		# age = epoch actuel - epoch creation du fichier (secondes)
	
	# --- Debug 
	debug_print_info(get_date_idList.__name__, str(age))
	
	return age

def get_file_extension(file_name):
	t_name_splitted = file_name.split('.') 				# Split nom fichier à chaque '.'
	tab_len = len(t_name_splitted)						# Calcul nb éléments (extension étant à n -1)
	
	# --- Debug 
	debug_print_info(get_file_extension.__name__, "." + t_name_splitted[tab_len - 1])
	
	return  "." + t_name_splitted[tab_len - 1]			# Retourne .ext
	
def get_serie_name(file_name):
	t_name_splitted = re.split('\.S[0-9]', file_name)		# Split nom fichier avant '.S[0-9]'
	t_name_splitted = t_name_splitted[0].replace(".", " ")	# Remplace les '.' du nom par un espace
	
	# --- Debug
	debug_print_info(get_serie_name.__name__, t_name_splitted)
	
	return t_name_splitted									# Retourne le nom

def get_serie_id(serie_name):
	idList = ConfigParser.RawConfigParser()					# Creation d'un fichier ConfigParser
	idList.read(SHOW_LIST)									# Pointage vers le fichier adéquat
	
	serie_id = idList.get("ShowsId", serie_name)			# Recherche de l'id de la série
	
	# --- Debug
	debug_print_info(get_serie_id.__name__, serie_id)
	
	return serie_id											# Retourne l'id de la série
	
	
# ~~~~~ MAIN ~~~~~
# Ouverture ou création du fichier contenant les id addic7ed des séries
try:
	with open(SHOW_LIST): pass				# Tentative d'ouverture du  fichier (verif de son existence)
	
	if(get_date_idList() >= 864000):		# Plus vieux que 10 jours ?
		print("showList.txt is older than 10 days, getting it again")
		create_show_idList()

except IOError:								# Le fichier n'exite pas, creation
	print("showList.txt not found, creating it")
	create_show_idList()
# Vérification et création du fichier terminé

# Recherche dans le dossier DL des series necessitant des subs (fichier ne possédant pas de .srt associé)
for i in os.listdir(DOWNLOAD_DIR):				# Crawl le répertoire et sort les fichiers + rep
	if(re.match(r'.*\.(mp4|mkv|avi)$', i)):		# Match every .mp4 / .mkv / .avi files
		get_file_extension(i)
		get_serie_id(get_serie_name(i))
