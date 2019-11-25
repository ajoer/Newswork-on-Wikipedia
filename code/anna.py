#!/usr/bin/python3
"""
	Gets data from Wikipedia given language(s) and topic 
	Uses the Wikipedia API.
"""

import argparse
import general
import get_data
import json
import os
import preprocess
import re

from urllib.request import urlopen
from Wikipedia.wikipedia import wikipedia
from Wikipedia.wikipedia import exceptions

from collections import defaultdict
from datetime import date
from enum import Enum

parser = argparse.ArgumentParser(description='Extract Wikipedia pages for a given title in a given language.')
parser.add_argument("topic", help="name of txt file with tab separated language, title pairs, e.g. 'refugee_crisis'.")
parser.add_argument("--save", default="y", help="save to location, str, 'y' or 'n'.")

args = parser.parse_args()

class FileType(Enum):
	RAW = "raw"
	PROCESSED = "processed"

def scrape_Wiki():

	input_data = open("data/topics/" + args.topic + ".txt").readlines()

	for line in input_data:
		language, title = line.split('\t')[0], line.split('\t')[1].strip()

		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		data = get_data.get_wiki_data(language, title)

		if data != None:	

			if args.save == "y":
				general.save_to_json(args.topic, language, data, FileType.RAW.value)

			# preprocess a few of the data types
			data['categories'] = preprocess.preprocess_categories(data['categories'])
			data['content'] = preprocess.preprocess_content(data['content'])
			data['images'] = preprocess.preprocess_images(data['images'])
			data['references'] = preprocess.preprocess_references(data['references'])
			data['revision_references'] = preprocess.get_references_from_revisions(data['revisions'])

			if args.save == "y":
				general.save_to_json(args.topic, language, data, FileType.PROCESSED.value)

		print(50*"*")	

if __name__ == "__main__":
	scrape_Wiki()