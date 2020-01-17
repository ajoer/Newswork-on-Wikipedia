#!/usr/bin/python3
"""
	Gets data from Wikipedia given language(s) and topic 
	Uses the Wikipedia API.
"""

import argparse
import general
import json
import os
import preprocess
import re

import dataclasses

from urllib.request import urlopen
from Wikipedia.wikipedia import wikipedia
from Wikipedia.wikipedia import exceptions

from collections import defaultdict
from datetime import datetime
from enum import Enum

parser = argparse.ArgumentParser(description='''Extracts and preprocesses Wikipedia pages for a given title, e.g. "refugee crisis" in a given language, e.g. "nl". 
						Input is a tab separated file with two columns, language and the article's title in that language, e.g. "nl\tEuropese vluchtelingencrisis".
						Output is a dictionary with (partly preprocessed) content for the language-topic pair. 
						This dictionary also has a field "revisions" with a dictionary of the entitre revision history.''')
parser.add_argument("topic", help="name of txt file with tab separated language, title pairs, e.g. 'refugee_crisis'.")
parser.add_argument("--save", default="y", help="save to location, str, 'y' or 'n'.")

args = parser.parse_args()

class FileType(Enum):
	RAW = "raw"
	PROCESSED = "processed"

def get_wiki_data(language, title):
	''' Get wikipedia data for a title in a given language, e.g. Europese_vluchtelingencrisis in NL, and save to json. '''
	
	wikipedia.set_lang(language)

	# add underscore in multiword titles: "refugee crisis" --> "refugee_crisis"
	if len(title.split()) > 1:
		title = '_'.join(title.split())
		print("Edited title:\t", title)	
	
	try:
		page = wikipedia.WikipediaPage(title)
		data = defaultdict()

		today = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
		data['_TODAY_'] = today
		data['_TITLE_'] = title

		data["categories"] = page.categories
		data["content"] = page.content
		data["links"] = page.links
		data["images"] = page.images
		data["references"] = page.references
		data["revision_id"] = page.revision_id
		data["sections"] = page.sections

		data["revisions"] = page.revisions
		print("there are %d revisions for %s" % ( len(data["revisions"]), title))
		
		if page.coordinates is not None:
			data["coordinates"] = (float(page.coordinates[0]), float(page.coordinates[1]))

		return data

	except exceptions.PageError:
		print("There is no '%s' page in the '%s' language version of Wikipedia, try another one" % (title, language))
		return None

def main():

	topic = args.topic
	input_data = open("data/topics/%s.txt" % topic).readlines()

	for line in sorted(input_data):
		language, title = line.split('\t')[0], line.split('\t')[1].strip()
		
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		data = get_wiki_data(language, title)

		if data != None:	

			if args.save == "y":
				general.save_to_json(topic, language, data, FileType.RAW.value)

			# Preprocess:
			data['categories'] = preprocess.preprocess_categories(data['categories'])
			data['content'] = preprocess.preprocess_content(data['content'])
			data['images'] = preprocess.preprocess_images(data['images'])
			data['references'] = preprocess.preprocess_references(data['references'])

			if args.save == "y":
				general.save_to_json(topic, language, data, FileType.PROCESSED.value)

		print(50*"*")	

if __name__ == "__main__":
	main()