#!/usr/bin/python3
"""
	General utils for Wikipedia edit history parsing, e.g. save and read form JSON.

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


def save_to_json(event, language, dictionary): 
	''' save JSON dump to file '''

	directory_name = "../newswork/data/%s/" % event

	try:
		os.mkdir(directory_name)
		print("Directory %s created!" % directory_name) 
	except FileExistsError:
		print("Directory %s already exists." % directory_name)
	
	file_name = "%s.json" % language
	with open(directory_name + file_name, 'w') as outfile:
		json.dump(dictionary, outfile, sort_keys=True, indent=4)

def save_pois_to_tsv(event, language, tsv_output):

	directory_name = "newswork/data/%s/tsv/" % event

	try:
		os.mkdir(directory_name)
		print("Directory %s created!" % directory_name) 
	except FileExistsError:
		print("Directory %s already exists." % directory_name)

	file_name = "%s.json" % language
	file_name = open(directory_name + file_name, 'w')

	file_name.write("%s\t%s\n" % (tsv_output[0][0], tsv_output[0][1]))
	for (t,p) in sorted(tsv_output[1:], key=lambda x: x[1], reverse=True):
		file_name.write("%s\t%s\n" % (t, p))
	file_name.close()

def open_data(event):

	input_files = glob.glob("data/%s/*.json" % event)

	for file_name in sorted(input_files):
		
		data = read_from_json(file_name)
		language = file_name.split('/')[-1].split('.')[0]

		print("\nLanguage:\t", language)
		print("Event:\t\t", event)

		yield data, language

def check_if_exists(event, language):
	
	directory_name = "newswork/data/%s/" % event
	file_name = directory_name + "%s.json" % language
	
	return os.path.isfile(file_name)

if __name__ == '__main__':
	open_data()
	read_from_json()
	save_to_json()
	save_pois_to_tsv()
	check_if_exists()
