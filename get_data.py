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

def save_to_json(data, title, lang):

	today = date.today().strftime("%Y%m%d")
	outfile = "output/raw/%s_%s_%s_raw.json" % (title, lang, today)

	with open(outfile, 'w') as outfile:
		json.dump(data, outfile)


def get_geobased_articles(latitude, longitude, results, radius):
	geo = wikipedia.geosearch(latitude=latitude,longitude=longitude, results=100,radius=10000)
	return geo

def GetWikiData():
	
	# There can be just 1 language and 1 title
	if len(args.titles.strip()) == 1:
		title = args.titles
	if len(args.languages.strip()) == 1:
		language = args.language

	# for lang in args.languages.strip().split():
	# 	wikipedia.set_lang(lang)
	# 	page = wikipedia.WikipediaPage(title)
	# 	data = get_page_data(page)
	# 	if args.save == "y":
	# 		save_to_json(data, title, lang)

GetWikiData()

""" Todo: parse text and save to file """