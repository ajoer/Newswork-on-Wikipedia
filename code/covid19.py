#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Calls the WikiRevParser and extracts information per revision.
	This file does *not* save the entire revisions, but rather specific informations per revision:
	- timestamp
	- size of content
	- editor (name or IP adress)
	- edit type (e.g. content or style edit)

	Output: JSON file where each entry is a revision.
"""

import argparse
import re
import revision_analysis
import utils_io as uio
import utils_visualization as uviz

from collections import Counter, defaultdict, OrderedDict
from WikiRevParser.wikirevparser import wikirevparser

parser = argparse.ArgumentParser(description='''Extracts specific information per revision of a Wikipedia page. To overcome data storage issues, the revision histories are not saved, only the extracted information. Used for COVID19 analysis''')
parser.add_argument("topic", help="e.g. 'covid19'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

def get_language_titles():

	language_titles = {}
	input_file = open("resources/events/%s.txt" % args.topic).readlines()

	for line in sorted(input_file):
		try:
			language, title = line.split('\t')[0], line.split('\t')[1].strip()
		except IndexError:
			language, title = line.split(',')[0], line.split(',')[1].strip()
		if args.language:
			if language != args.language: continue
		language_titles[language] = title

	return language_titles

def get_revisions(language, title):

	parser_instance = wikirevparser.ProcessRevisions(language, title)

	page = parser_instance.wikipedia_page()
	if page == None: return None

	revisions = parser_instance.parse_revisions()
	if revisions == None: return None

	return revisions

def process(revision):

	revision_data = {}
	revision_data["wikipedian"] = revision["user"]
	revision_data["content_size"] = len(revision["content"])

	# TODO: edit_purpose
	# maybe edit purpose should be in relation to the number of new images, links, content size, categories etc. 
	# Meaning it should be in comparison to the previous one.
	# I could also consider just saving the changes to the page rather than the entire page.
	
	return revision_data

def main():

	language_titles = get_language_titles()

	print(language_titles.keys())
	for language in language_titles.keys():
		title = language_titles[language]

		if args.check_os == "y":
			if uio.check_if_exists(args.topic, language): 
				print("%s has already been parsed for %s" %(args.topic, language))
				continue
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		output_dict = OrderedDict()
		revisions = get_revisions(language, title)

		for timestamp in revisions:
			revision_data = process(revisions[timestamp])
			output_dict[timestamp] = revision_data
		uio.save_to_json("covid19/" + args.topic, language, output_dict)

if __name__ == "__main__":
	main()
