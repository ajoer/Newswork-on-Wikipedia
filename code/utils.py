#!/usr/bin/python3
"""
	General modules used across MultiLingWiki.

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


def save_to_json(en_title, language, dictionary, filetype): 
	''' save JSON dump to file '''

	directory_name = "output/%s/%s/" % (filetype, en_title)

	try:
		os.mkdir(directory_name)
		print("Directory %s created!" % directory_name) 
	except FileExistsError:
		print("Directory %s already exists." % directory_name)
	
	file_name = "%s_%s_%s.json" % (en_title, language, filetype)
	with open(directory_name + file_name, 'w') as outfile:
		json.dump(dictionary, outfile)

def save_pois_to_tsv(en_title, language, tsv_output, filetype):

	directory_name = "output/%s/%s/tsv/" % (filetype, en_title)

	try:
		os.mkdir(directory_name)
		print("Directory %s created!" % directory_name) 
	except FileExistsError:
		print("Directory %s already exists." % directory_name)

	file_name = "%s_%s_%s.json" % (en_title, language, filetype)
	file_name = open(directory_name + "%s_%s_%s.json" % (en_title, language, filetype), 'w')

	file_name.write("%s\t%s\n" % (tsv_output[0][0], tsv_output[0][1]))
	for (t,p) in sorted(tsv_output[1:], key=lambda x: x[1], reverse=True):
		file_name.write("%s\t%s\n" % (t, p))
	file_name.close()

def open_data(filetype, topic):

	input_files = glob.glob("output/%s/%s/*.json" % (filetype, topic))

	for file_name in sorted(input_files):
		
		data = read_from_json(file_name)
		language = file_name.split('/')[-1].split('_')[-2]

		print("\nLanguage:\t", language)
		print("Title:\t\t", topic)

		yield data, language

def check_if_exists(filetype, en_title, language):
	
	directory_name = "output/%s/%s/" % (filetype, en_title)
	file_name = directory_name + "%s_%s_%s.json" % (en_title, language, filetype)
	
	return os.path.isfile(file_name)

if __name__ == '__main__':
	open_data()
	read_from_json()
	save_to_json()
	save_pois_to_tsv()
	check_if_exists()
