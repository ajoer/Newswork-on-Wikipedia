#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: txt file with tab separated language, title pairs, e.g. 'refugee_crisis'
	Ouput: yield revision history dictionary with clean data. 
	Output fields: tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""

import argparse
import matplotlib.pyplot as plt
import nltk
import re
import string
import utils
import WikiRevisionParser

from collections import defaultdict, Counter
from Levenshtein import distance as levenshtein_distance

parser = argparse.ArgumentParser(description='''Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="n", help="e.g. 'y' (for debugging).")

args = parser.parse_args()

def timestamp2date(timestamp):
	''' Convert timestamps to US datetime format. '''
	year = timestamp[:4]
	month = timestamp[5:7]
	day = timestamp[8:10]
	date = "%s-%s-%s" % (year, month, day)
	return date

def get_daily_data(data):
	''' Remove all revisions that are not the last of the day. '''

	timestamps = sorted(list(data.keys()))
	dates = [timestamp2date(ts) for ts in timestamps]

	for n in range(1,len(dates)):
		if dates[n] == dates[n-1]:
			del data[timestamps[n-1]]

	timestamps = sorted(list(data.keys()))
	dates = [timestamp2date(ts) for ts in timestamps]

	return data, timestamps, dates

def allow_levenshtein_distance(list1, list2, common_list):
	''' Allow Levenshtein distance between "unique" elements, e.g. "Ma'an" and "Maan". '''
	for x in list1:
		for y in list2:

			distance = levenshtein_distance(x, y)
			if distance > len(x)/3: continue
			
			list1.remove(x)
			common_list.add(x)

	return list1, common_list

def diff_lists(data, timestamps, n, key):

	curr = [x.lower() for x in data[timestamps[n]][key]]
	prev = [x.lower() for x in data[timestamps[n-1]][key]]
	if curr == prev: return [], []

	common_elements = set(prev).intersection(set(curr))
	added_elements = [x for x in curr if x not in prev]
	removed_elements = [x for x in prev if x not in curr] 

	added_elements, common_elements = allow_levenshtein_distance(added_elements, removed_elements, common_elements)
	removed_elements, common_elements = allow_levenshtein_distance(removed_elements, added_elements, common_elements)

	return added_elements, removed_elements

def diff_counters(data, timestamps, n, key):

	curr = Counter(data[timestamps[n]][key])
	prev = Counter(data[timestamps[n-1]][key])
	curr_values = sum(curr.values())
	prev_values = sum(prev.values())
	total = curr_values + prev_values

	if total == 0: return None

	curr_keys = set(curr.keys())
	prev_keys = set(prev.keys())
	diffs = dict()

	common_keys = list(curr_keys & prev_keys)
	unique_keys = curr_keys ^ prev_keys
	
	for key in common_keys:
		diff = curr[key] - prev[key]
		if diff == 0: continue
		diffs[key] = diff

	for key in unique_keys:
		if key in curr_keys:
			diffs[key] = curr[key]
		else:
			diffs[key] = -prev[key]
	try:
		assert sum(diffs.values()) == curr_values-prev_values
	except AssertionError as error:
		print("The number of diffs found do not match the total difference between this timestamp and the previous")
	
	if len(diffs) != 0: 
		return diffs

def get_RAWgraph_area_data(all_keys, input_dict):
	print("date\tkey\tvalue")

	for date in input_dict:
		for key in all_keys:
			if key in input_dict[date]:
				print(date, "\t", key, "\t", input_dict[date][key])
			else:
				print(date, "\t", key, "\t", 0)

def get_RAWgraph_barchart_data(input_dict, change_type):
	print("date\tkey\tvalue")

	for date in input_dict:
		print(date, "\t", change_type, "\t", input_dict[date])
	
def plot_barchart(added, removed):

	dates = list(added.keys())
	added_values = list(added.values())
	removed_values = list(removed.values())

	fig, ax = plt.subplots()
	ax.bar(dates, added_values)
	ax.bar(dates, removed_values)
	plt.show()

def get_link_frequencies(data, timestamps):

	links_history = defaultdict() #lambda: dict(list))

	for t in timestamps:
		links_counter = Counter(data[t]["links"])
		total_count_links = sum(links_counter.values())
		
		links_data = dict()
		length_of_content = len(data[t]["content"])

		for link in links_counter:

			link_data = dict()
			frequency = links_counter[link]
			link_data["frequency"] = frequency
			link_data["relative_frequency_entities"] = 100 * (frequency/total_count_links)
			link_data["relative_frequency_content"] = 100 * (frequency/length_of_content)
			links_data[link] = link_data

		links_history[t] = links_data
	return links_history

def analyse_links(data, timestamps, dates):
	num_removed_links = dict()
	num_added_links = dict()
		
	for n in range(1,len(timestamps)):
		if n == 0: continue

		added_links, removed_links = diff_lists(data, timestamps, n, "links")
		num_added_links[dates[n]] = len(added_links)
		num_removed_links[dates[n]] = len(removed_links)

		if args.visualize == "y": plot_barchart(num_added_links, num_removed_links)

def analyse_tlds(data, timestamps, dates):

	tlds_change_points = dict()
	all_tlds = set()

	tlds_diffs = diff_counters(data, timestamps, n, "tlds_origin")
	if tlds_diffs: 

		all_tlds = all_tlds|data[timestamps[n]]["tlds_origin"].keys()
		tlds_change_points[dates[n]] = data[timestamps[n]]["tlds_origin"]

	get_RAWgraph_area_data(all_tlds, tlds_change_points)	

def main():

	for data, language in utils.open_data(args.topic):

		if args.language:
			if language != args.language: continue
		
		daily_data, timestamps, dates = get_daily_data(data)

		#links_info = get_link_frequencies(daily_data, timestamps)
		
		#utils.save_to_json("%s/entities" % args.topic, language, links_info)
		#analyse_links(data, timestamps, dates)
		#analyse_tlds(data, timestamps, dates)

if __name__ == "__main__":
	main()
