#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Processes the output from covid19_vs.py.
	The input data has the following structure:
		dictionary where each key is a timestamp and the value a dictionary with the following:
			1) size of content ("words")
			2) wikipedian
			3) new links
			4) deleted links
			5) sections
	Output: Overview of the nationality of the references, whether they are local or global (local here == Danish).  
"""

import argparse
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.graph_objects as go
import string
import re
import requests
import revision_analysis
import time
import utils_io as uio
import utils_visualization as uviz

from collections import Counter, defaultdict, OrderedDict
from tabulate import tabulate
from WikiRevParser.wikirevparser import wikirevparser

parser = argparse.ArgumentParser(description='''Extracts specific information per revision of a Wikipedia page. To overcome data storage issues, the revision histories are not saved, only the extracted information. Used for COVID19 analysis''')
parser.add_argument("event", help="e.g. 'covid19'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

counter = 0

def check_if_location(entity, language):
	global counter
	if counter == 5:
		time.sleep(5)
		counter = 0
	entity = entity.capitalize()
	label='"'+entity+'"'
	sparql = "https://query.wikidata.org/sparql"
	rq_wiki="""  SELECT ?geo WHERE {{  ?country rdfs:label {0}@{1} .  ?country  wdt:P625 ?geo . }}"""
	r = requests.get(sparql, params = {'format': 'json', 'query':rq_wiki.format(label, language)})
	counter += 1
	data = r.json()
	if (pd.json_normalize(data['results']['bindings']).empty is False):
		results_df = pd.json_normalize(data['results']['bindings']).iloc[0][2]
		return results_df
	else:
		pass #print("the entity is not a location on Wikidata")

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

	directory = "data/%s/020720/*.json" % args.event
	for filename in sorted(glob.glob(directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print("\nLanguage:\t", language)

		if args.check_os == "y":
			if os.path.isfile(f"visualizations/{args.event}/content_magnitude/{language}.png"):
				print(f"{language} has already been analyzed, moving on...")
				continue

		input_data = uio.read_from_json(filename)
		timestamps = list(input_data.keys())
		danish = []
		locations = []
		number_of_danish = []
		number_of_locations = []

		for timestamp in timestamps:
			try:
				entities = input_data[timestamp]["new_links"]
				for entity in entities:
					if entity[0] == "_":
						danish.append(entity)
						locations.append(entity)
						print("**", entity)
					elif check_if_location(entity, language) != None:
						locations.append(entity)
						print("*", entity)
					elif check_if_location(entity, "en") != None:
						locations.append(entity)
						print("*", entity)
					elif check_if_location(entity.split()[0], language) != None:
						locations.append(entity)
						print("*", entity)
					elif check_if_location(entity.split("-")[0], language) != None:
						locations.append(entity)
						print("*", entity)
					
			except KeyError:
				pass
			try:
				entities = input_data[timestamp]["deleted_links"]
				for entity in entities:
					if entity in locations:
						locations.remove(entity)
			except KeyError:
					pass
			
			number_of_danish.append(len(danish))
			number_of_locations.append(len(locations))
		
		print(danish)
		print(locations)
		print(number_of_danish)
		print(number_of_locations)
		print(timestamps)

if __name__ == "__main__":
	main()

