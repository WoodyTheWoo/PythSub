# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup 	# Import parser BeautifulSoup
import codecs					# Import char coding
import os						# Import OS methods
import time						# Import gestion temps
import re						# Import regex expressions
import ConfigParser				# Import gestion id series
import requests					# Import lib gestion HTTP

# ~~~~~ CONSTANTES ~~~~~
# Nom fichier de config contenant les id addic7ed
# Dir où sont copiées les séries une fois traitées
# Dir à crawler pour trouver les épisodes
# ON / OFF
SHOW_LIST = "showList.txt"
SERIES_DIR = "D:\Documents\Downloads\SeriesTest"
DOWNLOAD_DIR = "D:\Documents\Downloads\Bitch"
ON = 1
OFF = 0

# ~~~~~ FONCTIONS DEBUG ~~~~~
# Active / Desactive debug
DEBUG = ON											

# Affiche le nom de la fonction + le message d'info si DEBUG = ON
def debug_print_info(function_name, message_info):
	if(DEBUG):
		print "[DEBUG] [" + function_name + "] - " + message_info


# ~~~~~ FONCTIONS ~~~~~

# CREATE SHOW ID LIST
# Crée le fichier de config contenant les id des séries venant d'addic7ed
# in : none
# out : none
def create_show_idList():
	# Ouverture fichier liste des séries encodage UTF-8
	idList_File = codecs.open(SHOW_LIST, 'wb', 'utf-8')

	# Mise en cache de la page contenant les id des séries
	urlAddic7edShows = requests.get("http://www.addic7ed.com/shows.php")
	addic7edShows = urlAddic7edShows.content
	urlAddic7edShows.close() 			# Fermeture site ouvert

	soup = BeautifulSoup(addic7edShows) # Parsing avec BS venant du site en cache
	showId = soup.select("tr h3 a") 	# Recherche de tout les liens <a href="/show/xxxxx">

	idList_File.write("[ShowsId]\n") 	# Tag [ShowId] pour ConfigParser
	
	for s in showId :
		# print(s.get("href").split('/')[2], " = ", s.text)				# --- Debug
		idList_File.write(	s.text.replace("(", "").replace(")", "").replace("'", "") 	# Suppression des '()' et '''dans les noms de séries
							+ " = " + s.get("href").split('/')[2] 		# = id série
							+ "\n")										# Retour chariot
		
	idList_File.close()					# Fermeture du fichier

# GET DATE FROM SHOW ID FILE
# Récupère l'age du fichier showId
# in : none
# out : age en secondes
def get_date_idList():
	age = time.time() - os.path.getmtime(SHOW_LIST)		# age = epoch actuel - epoch creation du fichier (secondes)
	
	# --- Debug 
	debug_print_info(get_date_idList.__name__, str(age))
	
	return age

# GET FILE EXTENSION
# Récupère l'extension du fichier en param
# in : nom du fichier (xxxx.ext)
# out : extension du fichier en '.ext"
def get_file_extension(file_name):
	t_name_splitted = file_name.split('.') 				# Split nom fichier à chaque '.'
	tab_len = len(t_name_splitted)						# Calcul nb éléments (extension étant à n -1)
	
	# --- Debug 
	debug_print_info(get_file_extension.__name__, "." + t_name_splitted[tab_len - 1])
	
	return  "." + t_name_splitted[tab_len - 1]			# Retourne .ext

# GET SUBTITLE FILENAME
# Récupère le nom du futur fichier de sous titre '.srt'
# Remplace simplement l'extension de la vidéo par '.srt'
# in : nom du fichier vidéo (xxxx.mkv|avi|mp4)
# out : nom du fichier de sous titre
def get_sub_filename(video_file):
	sub_filename = re.sub('mkv|avi|mp4', 'srt', video_file)			# Remplace '.mkv|.mp4|.avi' par '.srt'
	
	# --- Debug 
	debug_print_info(get_sub_filename.__name__, sub_filename)
	
	return  sub_filename											# Retourne le nom du fichier de sous titre

# GET SERIE NAME
# Récupère le nom de la série à partir du nom fichier
# Coupe avant '.S[0-9]' et remplace les '.' par ' '
# in : nom du fichier (xxxx.ext)
# out : nom de la série
def get_serie_name(file_name):
	t_name_splitted = re.split('\.[S|s][0-9]{2}', file_name)		# Split nom fichier avant '.S[0-9]'
	serie_name = t_name_splitted[0].replace(".", " ")		 		# Remplace les '.' du nom par un espace
	
	# --- Debug
	debug_print_info(get_serie_name.__name__, serie_name)
	
	return serie_name												# Retourne le nom de la série

# GET SERIE SEASON
# Récupère la saison de la série à partir du nom fichier
# Sélectionne la séquence '.S[0-9]'
# in : nom du fichier (xxxx.ext)
# out : numéro de saison (format string)
def get_serie_season(file_name):
	t_name_splitted = re.findall('\.[S|s][0-9]{2}', file_name)		# Trouve la séquence '.S[0-9]'
	serie_season = re.sub('\.|S|s', '', t_name_splitted[0])			# Supprime les '.' et les 'S|s'
	
	# --- Debug
	debug_print_info(get_serie_season.__name__, serie_season)
	
	return serie_season												# Retourne le numero de saison

# GET SERIE EPISODE
# Récupère le numéro de l'épisode à partir du nom de fichier
# Sélectionne la séquence 'E[0-9]'
# in : nom du fichier (xxxx.ext)
# out : numéro de l'épisode sans '0' (format string)
def get_serie_episode(file_name):
	t_name_splitted = re.findall('[E|e][0-9]{2}', file_name)		# Trouve la séquence 'E[0-9]'
	serie_episode = re.sub('E|e|^0', '', t_name_splitted[0])		# Supprime les 'E|e' et le '0' devant le numéro de l'épisode
	
	# --- Debug
	debug_print_info(get_serie_episode.__name__, serie_episode)
	
	return serie_episode											# Retourne le numero de l'épisode

# GET SERIE ID
# Récupère l'id de la série à partir du nom de fichier
# Parse le fichier de config
# in : nom du fichier (xxxx.ext)
# out : id de la série (format string)
def get_serie_id(file_name):
	serie_name = get_serie_name(file_name)					# Recupère le nom de la série à partir du nom de fichier
	
	idList = ConfigParser.RawConfigParser()					# Creation d'un fichier ConfigParser
	idList.read(SHOW_LIST)									# Pointage vers le fichier adéquat
	
	serie_id = idList.get("ShowsId", serie_name)			# Recherche de l'id de la série dans le tag [ShowsId]
	
	# --- Debug
	debug_print_info(get_serie_id.__name__, serie_id)
	
	return serie_id											# Retourne l'id de la série
	
	
# ~~~~~ MAIN ~~~~~
# Ouverture ou création du fichier contenant les id addic7ed des séries si non exixtant
# Ou si fichier plus vieux que 10 jours
try:
	with open(SHOW_LIST): pass				# Tentative d'ouverture du  fichier (verif de son existence)
	
	if(get_date_idList() >= 864000):		# Ou plus vieux que 10 jours ?
		print("showList.txt is older than 10 days, creating it again")
		create_show_idList()

except IOError:								# Le fichier n'exite pas, creation
	print("showList.txt not found, creating it")
	create_show_idList()
	
# ~~~~~~~~
# Vérification et création du fichier lsite des id terminé
# ~~~~~~~~

# Recherche dans le dossier DL des series necessitant des subs
# Fichiers vidéos .mkv | .mp4 | .avi
for i in os.listdir(DOWNLOAD_DIR):				# Crawl le répertoire et sort les fichiers + rep
	
	# Si c'est un fichier vidéo
	if(re.match('.*\.(mp4|mkv|avi)$', i)):
		
		# Variables reprenant les infos sur le fichier
		serie_id = get_serie_id(i)
		season = get_serie_season(i)
		episode = get_serie_episode(i)
		sub_name = DOWNLOAD_DIR + "\\" + get_sub_filename(i)
		
		# Puis télécharge les sous titres associés
		# ~~~~~~~~
		# Ouverture de l'url contenant la série + saison
		urlAddic7edSeriePage = requests.get("http://www.addic7ed.com/show/" 
											+ serie_id + "&season=" 
											+ season)
		addic7edSeriePage= urlAddic7edSeriePage.content								# Mise en cache de la page															
		urlAddic7edSeriePage.close() 												# Fermeture du site
		
		soup = BeautifulSoup(addic7edSeriePage) 									# Parsing avec BS à partir du site en cache
		
		for row in soup('tr', {'class': 'epeven completed'}):						# Selection du tableau comprenant les sub
			cells = row('td')														# Définition des cellules
			
			if(episode == cells[1].text):											# Séléction de l'épisode
				if("French" == cells[3].text):										# Sélection du Français
					
					if(cells[5].text.strip() != 'Completed'):						# Fichier non complet
						print "Subtitle not finished yet : " + cells[5].text		# Affiche le statut de completion actuel
						
					elif(cells[5].text.strip() == 'Completed'):						# Fichier complet
						# Mise en cache du sous titre 
						sub_download = requests.get("http://www.addic7ed.com" 
													+ cells[9].a['href'], 			# Ouverture du fichier de sous titre
													headers={'Referer': "http://www.addic7ed.com" 
													+ cells[9].a['href']})			# Avec le header correspondant à un fichier .srt (politique addic7ed)
						sub_file = open(sub_name, 'wb')								# Ouverture du fichier '.srt' sur le PC
						sub_file.write(sub_download.content)						# Ecriture du sub dans le fichier '.srt'
						sub_file.close()											# Fermeture du fichier
