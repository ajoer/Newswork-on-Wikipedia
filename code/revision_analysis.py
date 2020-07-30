#!/usr/bin/python3
"""
	Quantitatively analyze the revision histories of Wikipedia language versions. 
	I have used it to analyse the development of content size, content, references, captions, images etc. over time.
	
	Input: JSON with parsed and tokenized revision histories (from get_revisions.py)
	Output: analysis (numbers and/or visualizations) for each of the following:
		tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""

import argparse
import nltk
import re
import string
import utils
import utils_io as uio
import utils_visualization as uviz

from collections import defaultdict, Counter
from datetime import datetime, date

def diff_counters(curr, prev):

	added = 0
	removed = 0
	for ck, cv in curr.items():
		if ck in prev.keys():

			if cv == prev[ck]: continue

			diff = cv - prev[ck]

			if diff > 0: added += diff
			elif diff < 0: removed += diff

		else:
			added += cv

	for pk, pv in prev.items():
		if pk not in curr.keys(): removed -= pv

	return added, removed

def diff_lists(curr, prev):
	''' Get the difference between two lists in data. Returns two lists, one with additions over time, and one with removals over time.'''
	if curr == prev: return [], []

	added = [x for x in curr if x not in prev]
	removed = [x for x in prev if x not in curr] 

	# allow slight differences, e.g. "Ma'an" == "Maan"
	if len(added) == 0 or len(removed) == 0: return added, removed
	added, removed = utils.allow_levenshtein_distance(added, removed)
	
	if len(added) == 0: return added, removed
	removed, added = utils.allow_levenshtein_distance(removed, added)

	return added, removed
		
class Analyze:

	def __init__(self, data, language, topic, daily=True):
		self.data = data
		self.language = language
		self.topic = topic
		self.timestamps = sorted(list(self.data.keys()))
		self.dates = self.timestamps

	def _remove_vandalism(self, added_elements, removed_elements):

		timepoints = list(removed_elements.keys())
		for n in range(len(timepoints)-1):
			if removed_elements[timepoints[n]] == added_elements[timepoints[n+1]] and len(removed_elements[timepoints[n]]) != 0:
				removed_elements[timepoints[n]] = []
				added_elements[timepoints[n+1]] = []
		return added_elements, removed_elements

	def get_users(self):
		users = Counter()
		for t in self.timestamps:
			users[self.data[t]["user"]] += 1
		return users

	def list_development(self, element_type, remove_vandalism=False, visualize=False):
		''' Analyze and plot the development of links or urls over time. '''
		# Veel van de diffs in lists zijn kleine verschillen in spelling of specificatie, e.g. "anna", "anna (phd)"
		
		# elements are for actual links, urls etc
		removed_elements = dict()
		added_elements = dict()

		# counts are for visualizations
		added_counts = []
		removed_counts = []
		total_counts = []
			
		for n in range(len(self.timestamps)):
			curr_total = len(self.data[self.timestamps[n]][element_type])
			total_counts.append(curr_total)

			if curr_total == 0:
				added_counts.append(0)
				removed_counts.append(0)
				continue

			if n == 0: 
				added_elements[self.timestamps[n]] = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				removed_elements[self.timestamps[n]] = []

				added_counts.append(1)
				removed_counts.append(0)
			else:
				curr = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				prev = [x.lower() for x in self.data[self.timestamps[n-1]][element_type]]

				added, removed = diff_lists(curr, prev)
				added_elements[self.timestamps[n]] = added
				removed_elements[self.timestamps[n]] = removed

				if len(added) == 0: added_counts.append(0)
				else: added_counts.append(len(added))
				if len(removed) == 0: removed_counts.append(0)
				else: removed_counts.append(-len(removed))

		if remove_vandalism:
			added_elements, removed_elements = self._remove_vandalism(added_elements, removed_elements)

		if visualize:
			y = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in self.timestamps]
			uviz.plot_changes(y, added_counts, removed_counts, total_counts, self.topic, self.language, element_type)

		return added_counts, removed_counts, total_counts

	def string_development(self, element_type, visualize=False):

		# todo: remove vandalism. If x_t == x_t+2, remove x_t and x_t1
		added = []
		removed = []
		totals = []

		for n in range(len(self.timestamps)):
			curr_total = len(self.data[self.timestamps[n]][element_type].split())
			totals.append(curr_total)

			if curr_total == 0:
				added.append(0)
				removed.append(0)
				continue

			if n == 0: 
				added.append(1)
				removed.append(0)

			else:
				curr = [x.lower() for x in self.data[self.timestamps[n]][element_type].split()]
				prev = [x.lower() for x in self.data[self.timestamps[n-1]][element_type].split()]

				# TODO: do Levensteihn or something more complicated on sentences, 
				# to detect whether there is both additions and removals. And what they are.
				diff = len(curr) - len(prev)
				if diff == 0:
					added.append(0)
					removed.append(0)
				elif diff < 0:
					added.append(0)
					removed.append(diff) #/curr_total)
				elif diff > 0:
					added.append(diff) #/curr_total)
					removed.append(0)

		if visualize:
			y = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in self.timestamps]
			uviz.plot_changes(y, added, removed, totals, self.topic, self.language, element_type)

		return added, removed, totals
