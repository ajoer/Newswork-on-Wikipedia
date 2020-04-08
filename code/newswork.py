#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: JSON with parsed and tokenized revision histories (from get_revisions.py)
	Output: analysis (numbers and visualizations) for each of the following:
		tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""
import argparse
import numpy as np
import revision_analysis
import utils_io as uio
import utils_visualization as uviz

from collections import Counter, defaultdict, OrderedDict
from datetime import datetime
from Levenshtein import distance as levenshtein_distance
from operator import itemgetter
from sklearn import preprocessing
from tabulate import tabulate

parser = argparse.ArgumentParser(description='''Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")
parser.add_argument("--users", default="y")
parser.add_argument("--temporal", default="y")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="y", help="e.g. 'y' (for debugging).")

args = parser.parse_args()

elements = ["content", "links", "urls"] #, "images", "categories"]
languages = [l for l in uio.get_language(args.topic)] 

all_languages_totals = OrderedDict()
all_languages_dates = dict()
total_edits_all_languages = []

user_info = []
headers = ["Language", "# of editors", "# of edits", "Average # of edits/editor", "# of one-time editors", "length of article"]

def get_edits_per_date(timestamps):
	edits_per_date = Counter()
	dates = [datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d-%Y") for timestamp in sorted(timestamps)]
	
	for dt in dates:
		edits_per_date[dt] += 1

	y = [datetime.strptime(dt, "%m-%d-%Y") for dt in edits_per_date.keys()]

	return y, list(edits_per_date.values())

def print_user_info(list_of_lists, headers):

	table = sorted(list_of_lists, key=itemgetter(1))
	print(tabulate(table, headers, tablefmt="latex"))

def perform_analyses(visualize=False):

	edit_frequencies = []
	edit_dates = []
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
		l_dates, l_edits = get_edits_per_date(ra.timestamps)
		edit_frequencies.append(l_edits)
		edit_dates.append(l_dates)
	
		# # - - - - Perform analyses per element - - - - 

		# todo: "sections" have a bad format for now: [[],[],[]]
		totals_temporal = []
		added_temporal = []
		removed_temporal = []
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
			added_temporal.append(added)
			removed_temporal.append(removed)

		all_languages_totals[language] = totals_temporal
		users = ra.get_users()
		total_edits = sum(users.values())
		total_users = len(users)
		average = round(total_edits/total_users,0)
		singletime_editors = round((len([k for (k,v) in users.items() if v == 1])/total_users)*100,1)

		user_info.append([language, total_users, total_edits, average, singletime_editors, totals[-1]])
		
		#- - - - Temporal overview all elements - - - - -  

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
				pass
				print("Couldn't plot article development because:\t", err)
	#print_user_info(user_info, headers)
	#uviz.plot_element_across_languages(edit_dates, edit_frequencies, "edit frequency", languages, args.topic)
	
def comparative():
	for n, element in enumerate(elements):
		plotting_data = []
		for language in comparative_languages: 
			if args.language:
				if language != args.language: continue
				language = args.language

			lang_data = all_languages_totals[language][n]
			plotting_data.append(lang_data)
		uviz.plot_element_across_languages(all_languages_dates, plotting_data, element, languages, args.topic)

if __name__ == "__main__":
	perform_analyses()
	comparative()
