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

def determine_edit_type(values, previous_values):
	""" Determine whether an edit is editorial (0) or content (1). 
	This is dependent on whether there are substantial additions in content volume. 
	
	It is only a content contribution if:
		1) both text and links/urls are added (not text in isolation)
		2) images are added. 
	Editorial counts:
		- words only
		- categories
		- any deletions
	"""

	changes = {key: values[key] - previous_values.get(key, 0) for key in values}

	if changes["images"] > 0:
		return "content"

	elif changes["words"] > 0 and changes["links"]+changes["urls"] > 0:
		return "content"
	
	else:
		return "editorial"

def get_values(revision):
	""" Get the values to determine edit type (editorial or content). """

	values = {
		"words": len([w for w in revision["content"].split() if w not in string.punctuation]),
		"images": len(revision["images"]),
		"links": len(revision["links"]),
		"urls": len(revision["urls"]),
		#"sections": len(revision["sections"]),
		"categories": len(revision["categories"])
	}
	
	return values

def main():
	""" 
		Get revision histories and use the size changes of the different elements to determine edit type.
		Output dictionary where each key is a timestamp and the value a dictionary with the following:
			1) size of content
			2) wikipedian
			3) edit type
	"""

	language_titles = get_language_titles()
	for language in language_titles.keys():
		title = language_titles[language]

		if args.check_os == "y":
			if os.path.isfile("data/%s/%s.json" % (args.event, language)):
				print("%s has already been processed, moving on..." % language)
				continue
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		revisions = get_revisions(language, title)
		if revisions is None: continue
		timestamps = list(revisions.keys())
		timestamps.reverse()

		output_dict = OrderedDict()
		previous_values = {
			"words": 0,
			"images": 0,
			"links": 0,
			"urls": 0,
			"categories": 0
		}

		for n,timestamp in enumerate(timestamps):
			values = get_values(revisions[timestamp])

			timestamp_output = {}
			timestamp_output["wikipedian"] = revisions[timestamp]["user"]
			timestamp_output["words"] = values["words"]
			timestamp_output["edit_type"] = determine_edit_type(values, previous_values)
			previous_values = values

			output_dict[timestamp] = timestamp_output

		uio.save_to_json("%s/" % args.event, language, output_dict)

if __name__ == "__main__":
	main()
