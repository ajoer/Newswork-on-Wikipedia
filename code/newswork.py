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

from collections import Counter, defaultdict, OrderedDict
from datetime import datetime
from Levenshtein import distance as levenshtein_distance
from sklearn import preprocessing

parser = argparse.ArgumentParser(description='''Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")
parser.add_argument("--users", default="n")
parser.add_argument("--temporal", default="n")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="n", help="e.g. 'y' (for debugging).")

args = parser.parse_args()

elements = ["links", "urls", "content"] # "images", "categories"]
languages = [l for l in uio.get_language(args.topic)] #["sv", "da", "de", "sv", "es", "fr", "nb", "nl", "en"] # 
#half = round(len(languages))
#languages = languages[:half]
comparative_languages = ["en", "it", "zh"]
all_languages_totals = OrderedDict()
all_languages_dates = dict()

def perform_analyses(visualize=False):

	for language in languages:
		if args.language:
			if language != args.language: continue

		input_data = uio.open_file(args.topic, language)
		if input_data == None: 
			languages.remove(language)
			continue
		directory_name = "visualizations/%s/" % args.topic
		uio.mkdirectory(directory_name)

		ra = revision_analysis.Analyze(input_data, language, args.topic, daily=True)
		if language not in all_languages_dates.keys():
			language_timestamps = ra.timestamps
			all_languages_dates[language] = language_timestamps

		# - - - - Perform analyses per element - - - - 

		# todo: "sections" have a bad format for now: [[],[],[]]
		totals_temporal = []
		analysis_data = defaultdict()

		if args.visualize == "y":
			visualize = True

		for element in elements:
			if element == "content": 
				added, removed, totals = ra.string_development(element, visualize=visualize)
			else: 
				added, removed, totals = ra.list_development(element, remove_vandalism=True, visualize=visualize)
			analysis_data[element] = [added,removed]
			totals_temporal.append(totals)

		all_languages_totals[language] = totals_temporal

		# Users
		if args.users == "y":
			users = ra.get_users()
			total_edits = sum(users.values())
			total_users = len(users)
			median_users = len([k for (k,v) in users.items() if v ==1])
			print("users\t\t", total_users)
			print("max contributions", users.most_common(1)[0][1])
			print("average:\t", round(total_edits/total_users,2))
			print("median:\t\t", sorted(users.values())[round(len(users)/2)], "value, and %s percent" %round(median_users/total_users, 2))

		# - - - - Temporal overview all elements - - - - -  

		if args.temporal == "y":
			# Added/Removed over time for all elements
			y = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in language_timestamps]
			uviz.plot_article_development(y, analysis_data.values(), elements, args.topic, language, "article_changes")

			# General development of article over time, needs scaling to accomodate the differences in scope
			mm_scaler = preprocessing.MinMaxScaler()
			scaled_totals = [mm_scaler.fit_transform(np.array(x).reshape(-1, 1)) for x in totals_temporal]
			try:
				uviz.plot_article_development(y, scaled_totals, elements, args.topic, language, "article_development")
			except ValueError as err:
				print("Couldn't plot article development because:\t", err)
	
def comparative():
	##### Make timestamps datetime expressions in wikirecparser, so math comp is possible, e.g. <>=
	# that will make it possible to plot more languages in one and change labels to Jan 2010.
	for n, element in enumerate(elements):
		print("n",n)
		plotting_data = []
		for language in comparative_languages: 
			print("language", language)
			if args.language:
				if language != args.language: continue
				language = args.language

			lang_data = all_languages_totals[language][n]
			plotting_data.append(lang_data)

		uviz.plot_element_across_languages(all_languages_dates, plotting_data, element, languages, args.topic, "comp_%s" % element)

		
if __name__ == "__main__":
	perform_analyses()
	comparative()
