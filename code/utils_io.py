#!/usr/bin/python3
"""
	General IO utils for Wikipedia edit history parsing, e.g. save and read form JSON.

"""
import glob
import json
import os

def read_from_json(filename):
	''' read from json file if the file exists '''

	try:
		return json.load(open(filename))
	except FileNotFoundError:
		print("There is no file called: %s" % filename)
		return None

def mkdirectory(directory_name):
	try:
		os.mkdir(directory_name)
		print("Created a new directory:\t", directory_name)
	except FileExistsError:
		pass

def save_to_json(event, language, dictionary): 
	''' save JSON dump to file '''

	directory_name = "data/%s/" % event
	mkdirectory(directory_name)
	
	file_name = "%s.json" % language
	with open(directory_name + file_name, 'w') as outfile:
		json.dump(dictionary, outfile, sort_keys=True, indent=4)

def save_pois_to_tsv(event, language, tsv_output):

	directory_name = "data/%s/tsv/" % event

	try:
		os.mkdir(directory_name)
	except FileExistsError:
		pass

	file_name = "%s.json" % language
	file_name = open(directory_name + file_name, 'w')

	file_name.write("%s\t%s\n" % (tsv_output[0][0], tsv_output[0][1]))
	for (t,p) in sorted(tsv_output[1:], key=lambda x: x[1], reverse=True):
		file_name.write("%s\t%s\n" % (t, p))
	file_name.close()

def get_language(event):

	input_files = glob.glob("data/%s/*.json" % event)
	for file_name in sorted(input_files):
		language = file_name.split('/')[-1].split('.')[0]

		yield language

def open_file(event, language):

	print("\nLanguage:\t", language)
	print("Event:\t\t", event)

	file_name = "data/%s/%s.json" % (event, language)
	data = read_from_json(file_name)
	return data

def check_if_exists(event, language):
	
	directory_name = "data/covid19/%s/" % event
	file_name = directory_name + "%s.json" % language
	
	return os.path.isfile(file_name)

if __name__ == '__main__':
	open_data()
	read_from_json()
	save_to_json()
	save_pois_to_tsv()
	check_if_exists()