#!/usr/bin/python3
"""
	Gets data from Wikipedia given language(s) and topic 
	Uses the Wikipedia API.
"""

import argparse
import json
from Wikipedia.wikipedia import wikipedia

from urllib.request import urlopen
import re

from collections import defaultdict
from datetime import date

parser = argparse.ArgumentParser(description='Extract Wikipedia pages for a given title in a given language.')
parser.add_argument("--titles", default="brexit", help="title of a Wikipedia page, str, e.g. 'Brexit'.")
parser.add_argument("--languages", default="da", help="two letter language code, str, e.g. 'en'.")
parser.add_argument("--save", default="n", help="save to location, str, 'y' or 'n'.")

args = parser.parse_args()

def get_page_data(page,types="all"):

	''' This pulls the information from the page that the user requests '''
	data = defaultdict()

	if types == "all":
		types = ["categories", "content", "coordinates", "links", "images", "references", "revisions", "revision_id", "sections"]

	if "categories" in types:
		data["categories"] = page.categories
	if "content" in types:
		data["content"] = page.content
	if "coordinates" in types:
		data["coordinates"] = page.coordinates
	if "links" in types:
		data["links"] = page.links
	if "images" in types:
		data["images"] = page.images
	if "references" in types:
		data["references"] = page.references
	if "revision_id" in types:
		data["revision_id"] = page.revision_id
	if "sections" in types:
		data["sections"] = page.sections

	# returns the previous 500 edits (max)
	if 'revisions' in types:
		data['revisions'] = page.revisions

	return data

def save_to_json(data, title, language, save_type):

	''' this saves the raw data as a json file '''
	today = date.today().strftime("19%m%d")
	outfile = "./output/%s/%s_%s_%s_%s.json" % (save_type, title, language, today, save_type)

	with open(outfile, 'w') as outfile:
		json.dump(data, outfile)


def get_geobased_articles(latitude, longitude, results, radius):

	''' you can geosearch in several languages. Currently only with a specified long and lat, but later also with box ''' 
	geo = wikipedia.geosearch(latitude=latitude,longitude=longitude, results=results,radius=radius)
	return geo

def GetWikiData():
	
	titles = args.titles.split(',')
	languages = args.languages.split(',')

	for language in languages:
		wikipedia.set_lang(language)
		for title in titles:
			print("Language:\t", language)
			print("Title:\t\t", title)
			try:
				page = wikipedia.WikipediaPage(title)
			except:
				print("There is no '%s' page in the '%s' language version of Wikipedia, try another one" % (title, language))
				continue
			data = get_page_data(page)
			print(data["links"])

			if args.save == "y":
		 		save_to_json(data, title, language, "raw")

if __name__ == "__main__":
	GetWikiData()
	save_to_json()