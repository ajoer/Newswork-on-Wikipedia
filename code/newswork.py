#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: JSON with parsed and tokenized revision histories (from get_revisions.py)
	Output: analysis (numbers and visualizations) for each of the following:
		tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""
import argparse
import glob
import nltk
import numpy as np
import re
import revision_analysis
import string
import scipy
import utils
import utils_io as uio
import utils_visualization as uviz

from collections import defaultdict, Counter
from Levenshtein import distance as levenshtein_distance
from sklearn import preprocessing

parser = argparse.ArgumentParser(description='''Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="n", help="e.g. 'y' (for debugging).")

args = parser.parse_args()

def perform_analyses():

	for language in uio.get_language(args.topic):
		if args.language:
			if language != args.language: continue

		input_data = uio.open_file(args.topic, language)
		directory_name = "visualizations/%s/" % args.topic
		uio.mkdirectory(directory_name)

		ra = revision_analysis.Analyze(input_data, language, args.topic)
		
		# - - - - Perform analyses per element - - - - 
		elements = ["links", "urls", "images", "content", "categories"] # "sections" have a bad format for now: [[],[],[]]
		totals = []
		analysis_data = defaultdict()

		for element in elements:
			if element == "content": 
				added, removed, total = ra.string_development(element, visualize=True)
			else: 
				added, removed, total = ra.list_development(element, visualize=True)

			analysis_data[element] = [added,removed]
			totals.append(total)

		# Sections

		# - - - - Temporal overview all elements - - - - -  
		# Added/Removed over time for all elements
		uviz.plot_article_development(ra.dates, analysis_data.values(), elements, args.topic, language, "article_changes")
		#uviz.plot_article_development(analysis_object.dates, totals, elements, args.topic, language, "total_development")

		# General development of article over time, needs scaling to accomodate the differences in scope
		mm_scaler = preprocessing.MinMaxScaler()
		scaled_totals = [mm_scaler.fit_transform(np.array(x).reshape(-1, 1)) for x in totals]
		try:
			uviz.plot_article_development(ra.dates, scaled_totals, elements, args.topic, language, "article_development")
		except ValueError as err:
			print("there is an error hier", err)

if __name__ == "__main__":
	perform_analyses()
