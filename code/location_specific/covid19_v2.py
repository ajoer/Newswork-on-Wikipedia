#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Calls the WikiRevParser and extracts information per revision.
	This file does *not* save the entire revisions, but rather specific informations per revision:
	Output dictionary where each key is a timestamp and the value a dictionary with the following:
		1) size of content ("words")
		2) wikipedian
		3) new links
		4) deleted links
		5) sections
"""

import argparse
import os
import re
import revision_analysis
import string
import time
import utils_io as uio
import utils_visualization as uviz

from collections import Counter, defaultdict, OrderedDict
from WikiRevParser.wikirevparser import wikirevparser

parser = argparse.ArgumentParser(description='''Extracts specific information per revision of a Wikipedia page. To overcome data storage issues, the revision histories are not saved, only the extracted information. Used for COVID19 analysis''')
parser.add_argument("event", help="e.g. 'covid19'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

def get_language_titles():
	""" Extract language and title from input file. """

	language_titles = {}
	input_file = open("resources/events/%s.tsv" % args.event).readlines()

	for line in sorted(input_file):
		try:
			language, title = line.split('\t')[0], line.split('\t')[1].strip()
		except IndexError:
			language, title = line.split(',')[0], line.split(',')[1].strip()
		if args.language:
			if language != args.language: continue
		if language == "lang": continue
		if language.startswith("%"): continue # languages with % in front of them can't be scraped.
		language_titles[language] = title

	return language_titles

def get_revisions(language, title):
	""" Extract and parse Wikipedia revision history for given language and title. """

	time.sleep(3)
	parser_instance = wikirevparser.ProcessRevisions(language, title)

	page = parser_instance.wikipedia_page()
	if page == None: return None

	revisions = parser_instance.parse_revisions()
	if revisions == None: return None

	return revisions

def main():
	""" 
		Get revision histories and use the size changes of the different elements to determine edit type.
		Output dictionary where each key is a timestamp and the value a dictionary with the following:
			1) size of content ("words")
			2) wikipedian
			3) new links
			4) deleted links
			5) sections
	"""

	language_titles = get_language_titles()
	for language in language_titles.keys():
		title = language_titles[language]

		if args.check_os == "y":
			if os.path.isfile("data/%s/100720/%s.json" % (args.event, language)):
				print("%s has already been processed, moving on..." % language)
				continue
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		revisions = get_revisions(language, title)
		if revisions is None: continue
		timestamps = list(revisions.keys())
		timestamps.reverse()

		previous_links = []
		previous_sections = []
		output_dict = OrderedDict()

		for n,timestamp in enumerate(timestamps):

			timestamp_output = {}
			timestamp_output["wikipedian"] = revisions[timestamp]["user"]
			timestamp_output["words"] = len([w for w in revisions[timestamp]["content"].split() if w not in string.punctuation])
			timestamp_output["sections"] = []
			timestamp_output["new_links"] = []
			timestamp_output["deleted_links"] = []
			timestamp_output["citations"] = []
			
			# add new links to memory
			for link in revisions[timestamp]["links"]:
				if link not in previous_links:
					timestamp_output["new_links"].append(link)

			# add deleted links to memory
			for link in previous_links:
				if link not in revisions[timestamp]["links"]:
					timestamp_output["deleted_links"].append(link)

			previous_links = revisions[timestamp]["links"]

			if revisions[timestamp]["sections"]	!= previous_sections:
				timestamp_output["sections"] = revisions[timestamp]["sections"]
				previous_sections = revisions[timestamp]["sections"]

			del_keys = []
			for key in timestamp_output:
				if timestamp_output[key] == []:
					del_keys.append(key)
			for key in del_keys:
				del timestamp_output[key]

			timestamp_output["citations"] = revisions[timestamp]["urls"]

			output_dict[timestamp] = timestamp_output

		uio.save_to_json("%s/100720/" % args.event, language, output_dict)

if __name__ == "__main__":
	main()
