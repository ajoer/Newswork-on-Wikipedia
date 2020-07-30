#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Reads the scraped data (from covid19_data.py) and extracts information (preprocess).
		1) editor types over time
		2) content size over time
		3) edit type over time
		4) editor type/edit type over time 
	Output: dictionary
"""

import argparse
import glob
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go
import string
import re
import revision_analysis
import utils_io as uio
import utils_visualization as uviz

from collections import Counter, defaultdict, OrderedDict
from tabulate import tabulate
from WikiRevParser.wikirevparser import wikirevparser

parser = argparse.ArgumentParser(description='''Extracts specific information per revision of a Wikipedia page. To overcome data storage issues, the revision histories are not saved, only the extracted information. Used for COVID19 analysis''')
parser.add_argument("event", help="e.g. 'covid19'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="n")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

directory = "data/%s/*.json" % args.event

def get_wikipedian_type(wikipedian):
	""" determine whether a wikipedian is registered, anonymous or bot """
	IP = re.search(r"([0-9]+[:.]+)+", wikipedian)
	if IP != None: wikipedian_type = "anonymous"
	elif wikipedian.lower().endswith("bot"): 
		wikipedian_type = "bot"
	else: wikipedian_type = "registered"
	return wikipedian_type

def process_data(input_data):
	""" Get the values for each key in input data. Output is a dictionary with all y in Y in a list. """

	processed_data = {
		"content_sizes": [input_data[timestamp]["words"] for timestamp in input_data],
		"edit_types": [input_data[timestamp]["edit_type"] for timestamp in input_data],
		"wikipedians": [input_data[timestamp]["wikipedian"] for timestamp in input_data],
		"wikipedian_types": []
	}
	for wikipedian in processed_data["wikipedians"]:
		processed_data["wikipedian_types"].append(get_wikipedian_type(wikipedian))

	return processed_data

def normalize_counter(input_counter):
	total = sum(input_counter.values())
	for i in input_counter:
		input_counter[i] = round(input_counter[i] / total, 2)
	return input_counter

def get_wikipedian_edits_dist(data):
	""" get edit type per wikipedia type and vice versa """
	edit_wikipedian = {
		"anonymous": Counter(),
		"registered": Counter(),
		"bot": Counter()
	}
	wikipediantype_edit = {
		"content": Counter(),
		"editorial": Counter()
	}

	for e, w in zip(data["edit_types"], data["wikipedian_types"]):
		edit_wikipedian[w][e] += 1
		wikipediantype_edit[e][w] += 1

	for key in edit_wikipedian:
		edit_wikipedian[key] = normalize_counter(edit_wikipedian[key])
		if args.visualize == "y":
			fig = go.Figure(data=[go.Pie(labels=list(edit_wikipedian[key].keys()), values=list(edit_wikipedian[key].values()))])
			fig.update(layout_title_text=key)
			fig.show()

	for key in wikipediantype_edit:
		wikipediantype_edit[key] = normalize_counter(wikipediantype_edit[key])
		if args.visualize == "y":
			fig = go.Figure(data=[go.Pie(labels=list(wikipediantype_edit[key].keys()), values=list(wikipediantype_edit[key].values()))])
			fig.update(layout_title_text=key)
			fig.show()

	return edit_wikipedian, wikipediantype_edit


def get_diachronic_wikipedians(data):
	""" edit types per wikipedia type over time """
	
	totals = {
		"content": 0,
		"editorial": 0,
		"anon_content": 0,
		"anon_editorial": 0,
		"reg_content": 0,
		"reg_editorial": 0,
		"bot_content": 0,
		"bot_editorial": 0
	}
	wikipedian_edit_diachronic = {
		"anon_content": [],
		"anon_editorial": [],
		"reg_content": [],
		"reg_editorial": [],
		"bot_content": [],
		"bot_editorial": []
	}
	for e, w in zip(data["edit_types"], data["wikipedian_types"]):

		if e == "content":
			if w == "anonymous": 
				totals["anon_content"] += 1
			elif w == "registered":
				totals["reg_content"] += 1
			elif w == "bot":
				totals["bot_content"] += 1
			totals["content"] += 1

		elif e == "editorial":
			if w == "anonymous": 
				totals["anon_editorial"] += 1
			elif w == "registered":
				totals["reg_editorial"] += 1
			elif w == "bot":
				totals["bot_editorial"] += 1
			totals["editorial"] += 1

		if totals["content"] == 0:
			wikipedian_edit_diachronic["anon_content"].append(0)
			wikipedian_edit_diachronic["reg_content"].append(0)
			wikipedian_edit_diachronic["bot_content"].append(0)
		else:
			wikipedian_edit_diachronic["anon_content"].append(totals["anon_content"]/totals["content"])
			wikipedian_edit_diachronic["reg_content"].append(totals["reg_content"]/totals["content"])
			wikipedian_edit_diachronic["bot_content"].append(totals["bot_content"]/totals["content"])
		
		if totals["editorial"] == 0:
			wikipedian_edit_diachronic["anon_editorial"].append(0)
			wikipedian_edit_diachronic["reg_editorial"].append(0)
			wikipedian_edit_diachronic["bot_editorial"].append(0)
		else:
			wikipedian_edit_diachronic["anon_editorial"].append(totals["anon_editorial"]/totals["editorial"])
			wikipedian_edit_diachronic["reg_editorial"].append(totals["reg_editorial"]/totals["editorial"])
			wikipedian_edit_diachronic["bot_editorial"].append(totals["bot_editorial"]/totals["editorial"])

	return wikipedian_edit_diachronic


def get_content_development(data, timestamps):
	""" content development and deletion/additions per wikipedian type. Makes data for table and plot"""
	content_information = {
		"content_sizes": [],
		"addition_magnitude": Counter(),
		"addition_count": Counter(),
		"deletion_magnitude": Counter(),
		"deletion_count": Counter(),
		"registered_add": [],
		"anonymous_add": [],
		"bot_add": [],
		"registered_del": [],
		"anonymous_del": [],
		"bot_del": []
	}
	total_non_magnitude_change = 0

	for n, s in enumerate(data["content_sizes"]):
		#print(s, "\tat timestamp:\t", timestamps[n], "(", n, ")")
		content_information["content_sizes"].append(s)

		wikipedian = data["wikipedian_types"][n]
		other_wikipedians = [t for t in ["registered", "anonymous", "bot"] if t != wikipedian]
		
		# this is for making a table
		if n == 0: 
			content_information["addition_magnitude"][wikipedian] += s
			content_information["addition_count"][wikipedian] += 1
			content_information[f"{wikipedian}_add"].append(s)
			content_information[f"{wikipedian}_del"].append(0)

			for wikipedian_type in other_wikipedians:
				content_information[f"{wikipedian_type}_add"].append(0)
				content_information[f"{wikipedian_type}_del"].append(0)
			continue

		previous_size = data["content_sizes"][n-1]

		if s < previous_size:
			content_information["deletion_magnitude"][wikipedian] += previous_size - s
			content_information["deletion_count"][wikipedian] += 1
			content_information[f"{wikipedian}_del"].append(data["content_sizes"][n-1] - s)
			#if wikipedian == "registered":
			print("deletion:\t", timestamps[n], previous_size, s, s - previous_size)
		else:
			content_information[f"{wikipedian}_del"].append(0)

		if s > previous_size:
			content_information["addition_magnitude"][wikipedian] += s - previous_size
			content_information["addition_count"][wikipedian] += 1
			content_information[f"{wikipedian}_add"].append(s - data["content_sizes"][n-1])
			#if wikipedian == "anonymous":
			#	print("addition:\t", timestamps[n], previous_size, s, s - previous_size)
		else:
			content_information[f"{wikipedian}_add"].append(0)
		
		for wikipedian_type in other_wikipedians:
			content_information[f"{wikipedian_type}_add"].append(0)
			content_information[f"{wikipedian_type}_del"].append(0)

	return content_information

def add_to_table(language, content_information, evaluation="deletion"):
	""" format data for tabulate for deletion/addition """

	language_list = [language]
	total_count = 0
	for user_type in ["registered", "anonymous", "bot"]: #list(content_information[f"{evaluation}_count"].keys()):
		for element in ["count", "magnitude"]:
			
			if user_type in list(content_information[f"{evaluation}_count"].keys()):
				counter = content_information[f"{evaluation}_{element}"]
				value = counter[user_type]

				total = sum(counter.values())
				if total == 0: percentage = ""
				else: percentage = round((value/total) * 100,1)

				if element == "count": total_count += value
				#if value == 0 or value == 0.0: value = ""
				if percentage == 0 or percentage == 0.0: percentage = ""

				language_list.append(percentage)

			else:
				language_list.append("")

	language_list.append(total_count)
	if total_count < 100: return None
	elif len(language_list) == 1: return None
	elif language_list[2] == 100.0: return None
	return language_list

def get_wikipedian_information(data):
	""" Wikipedian distributions """
	wikipedian_edit = {}
	edit_wikipedian = {
		"editorial": Counter(),
		"content": Counter()
	}
	for e, w in zip(data["edit_types"], data["wikipedians"]):
		if w not in wikipedian_edit:
			wikipedian_edit[w] = Counter()
		wikipedian_edit[w][e] += 1

	for e, w in zip(data["edit_types"], data["wikipedians"]):
		edit_wikipedian[e][w] += 1

	print("\n********** Top 10 editorial contributors ********** \t", edit_wikipedian["editorial"].most_common(10))
	print()
	print("\n********** Top 10 content contributors ********** \t", edit_wikipedian["content"].most_common(10))
	print()

def get_continents(languages):
	continent_data = open(f"resources/events/covid19.tsv").readlines()
	LV2continent = {}
	continents = []
	colors = []

	continent2color = {
		"Universal": "aliceblue",
		"Europe": "darkslateblue",
		"Asia": "hotpink",
		"North America": "seagreen",
		"South America": "rebeccapurple",
		"Africa": "cadetblue",
		"Caribbean": "lime"
	}

	for line in continent_data:
		language, title, continent = line.split("\t")
		LV2continent[language.strip()] = continent.strip()

	for language in languages:
		if language not in list(LV2continent.keys()):
			print("{language} is not in the list of continents")
			continue
		continent = LV2continent[language]
		continents.append(continent)
		colors.append(continent2color[continent])

	return colors, continents

def main():

	header1 = ["Language", "Registered", "", "Anonymous", "", "Bot", "", "total count"]
	header2 = ["", "CP", "MP", "CP", "MP", "CP", "MP", ""]
	deletion_table = [header2]
	addition_table = [header2]
	creation_time = dict()

	too_small_languages = set()

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
		data = process_data(input_data)
		creation_time[language] = (timestamps[0], data["wikipedian_types"][0])
		
		if len(timestamps) < 100: 
			too_small_languages.add((language, len(timestamps)))
			continue
		
		# """ WIKIPEDIANS """
		get_wikipedian_information(data)

		# # distributions of wikipedian/edits and edits/wikipedian
		edit_wikipedian, wikipedian_edit = get_wikipedian_edits_dist(data)

		# # over time
		wikipedian_edit_diachronic = get_diachronic_wikipedians(data)
		uviz.plot_wikipedian_edittypes(wikipedian_edit_diachronic, timestamps, args.event, language)

		""" CONTENT """
		content_information = get_content_development(data, timestamps)
		uviz.plot_content_magnitude(content_information["content_sizes"], timestamps, args.event, language)
		uviz.plot_additions_deletions_per_wikipediantype(content_information, timestamps, args.event, language)
		
		# Deletion
		language_list = add_to_table(language, content_information)
		if language_list != None:
			deletion_table.append(language_list)

		# Addition
		language_list = add_to_table(language, content_information, evaluation="addition")
		if language_list != None:
			addition_table.append(language_list)
	
	#DELETION and ADDITION tables
	print("\n********** Deletions **********")
	print(tabulate(deletion_table, headers=header1, tablefmt="latex"))
	print("\n********** Additions **********")
	print(tabulate(addition_table, headers=header1, tablefmt="latex"))

	print("\n\n")
	sorted_creation_times ={k: v for k, v in sorted(creation_time.items(), key=lambda item: item[1])} 
	languages = list(sorted_creation_times.keys())
	creation_times = [t.split("T")[0] for (t, w) in sorted_creation_times.values()]
	first_creator = Counter([w for (t, w) in sorted_creation_times.values()])
	print("First creators:\t", first_creator)
	print([el[0] for el in creation_time.items() if el[1][1] == "anonymous"])
	print()

	colors, continents = get_continents(languages)
	uviz.plot_creation_time(creation_times, languages, colors, continents)

	print("%s languages have < 100 edits:" % len(too_small_languages), too_small_languages)

if __name__ == "__main__":
	main()