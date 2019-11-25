#!/usr/bin/python3
"""
	General modules used across MultiLingWiki.

"""

import json
import os

def read_from_json(filename):
	''' read from json file if the file exists '''

	try:
		return json.load(open(filename))
	except FileNotFoundError:
		print("There is no file called: %s" % filename)
		return None

def save_to_json(en_title, language, data, status): 
	''' save JSON dump to file '''
	
	# Create target directory for English term (e.g. refugee_crisis)
	directory_name = "output/%s/%s" % (status, en_title)

	try:
		os.mkdir(directory_name)
		print("Directory %s created!" % directory_name) 
	except FileExistsError:
		print("Directory %s already exists." % directory_name)
	
	file_name = "/%s_%s_%s.json" % (en_title, language, status)
	with open(directory_name + file_name, 'w') as outfile:
		json.dump(data, outfile)


def get_geobased_articles(latitude, longitude, results, radius):

	''' you can geosearch in several languages. Currently only with a specified long and lat, but later also with box ''' 
	geo = wikipedia.geosearch(latitude=latitude,longitude=longitude, results=results,radius=radius)
	return geo

if __name__ == '__main__':
	read_from_json()
	save_to_json()
