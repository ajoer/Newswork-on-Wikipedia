#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: JSON with parsed and tokenized revision histories (from get_revisions.py)
	Output: analysis (numbers and visualizations) for each of the following:
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
from datetime import datetime

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

# Sara
def get_link_frequencies(data, timestamps):

	links_history = defaultdict()

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

	uio.save_to_json("%s/entities" % args.topic, language, links_history)
		
	return links_history
		
class Analyze:

	def __init__(self, data, language, topic, daily=True):
		self.data = data
		self.language = language
		self.topic = topic
		self.timestamps = sorted(list(self.data.keys()))
		self.dates = self.timestamps
		#self.daily_data, self.timestamps, self.dates = self._one_edit_per_timestamp(daily)
		
	def _timestamp2date(self, timestamp, daily=True):
		''' Convert timestamps to US datetime format. '''
		year = timestamp[:4]
		month = timestamp[5:7]

		if daily:
			day = timestamp[8:10]
			date = "%s-%s-%s" % (year, month, day)
		else:
			date = timestamp
			#date = "%s-%s" % (year, month)
		return date

	def _one_edit_per_timestamp(self, daily=True):
		''' Filter so revision history has one entry per month or day, i.e. page on YYYY/MM or YYYY/MM/DD.'''

		self.timestamps = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in sorted(list(self.data.keys()))]
			
		self.dates = set([self._timestamp2date(ts, daily) for ts in self.timestamps])

		for n in range(1,len(self.dates)):
			if self.dates[n] == self.dates[n-1]:
				del self.data[self.timestamps[n-1]]

		self.timestamps = sorted(list(self.data.keys()))
		self.dates = [self._timestamp2date(timestamp) for timestamp in self.timestamps]

		return self.data, self.timestamps, self.dates

	def _one_edit_per_timespan(self, daily=True):
		''' Filter so revision history has one entry per month or day, i.e. page on YYYY/MM or YYYY/MM/DD.'''

		self.timestamps = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in sorted(list(self.data.keys()))]
		per_day = _last_edits_per_day(self.timestamps) 	
		#self.dates = set([ts.date() for ts in self.timestamps])

		for n in range(1,len(self.dates)):
			if self.dates[n] == self.dates[n-1]:
				del self.data[self.timestamps[n-1]]

		self.timestamps = sorted(list(self.data.keys()))
		self.dates = [self._timestamp2date(timestamp) for timestamp in self.timestamps]

		return self.data, self.timestamps, self.dates

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
				# added_elements[self.dates[n]] = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				# removed_elements[self.dates[n]] = []

				added_counts.append(1)
				removed_counts.append(0)
			else:
				curr = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				prev = [x.lower() for x in self.data[self.timestamps[n-1]][element_type]]

				added, removed = diff_lists(curr, prev)
				added_elements[self.timestamps[n]] = added
				removed_elements[self.timestamps[n]] = removed
				# added_elements[self.dates[n]] = added
				# removed_elements[self.dates[n]] = removed

				if len(added) == 0: added_counts.append(0)
				else: added_counts.append(len(added)) #/curr_total)
				if len(removed) == 0: removed_counts.append(0)
				else: removed_counts.append(-len(removed)) #/curr_total)

		if remove_vandalism:
			added_elements, removed_elements = self._remove_vandalism(added_elements, removed_elements)

		if visualize:
			y = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in self.timestamps]
			uviz.plot_barchart(y, added_counts, removed_counts, self.topic, self.language, element_type)

		return added_counts, removed_counts, total_counts

	def string_development(self, element_type, visualize=False):

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
			uviz.plot_barchart(self.dates, added, removed, self.topic, self.language, element_type)

		return added, removed, totals

"""
#!/usr/bin/python3
"""
#	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
#	Input: JSON with parsed and tokenized revision histories (from get_revisions.py)
#	Output: analysis (numbers and visualizations) for each of the following:
#		tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""

import argparse
import datetime
import nltk
import re
import string
import utils
import utils_io as uio
import utils_visualization as uviz

from collections import defaultdict, Counter

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

# Sara
def get_link_frequencies(data, timestamps):

	links_history = defaultdict()

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

	uio.save_to_json("%s/entities" % args.topic, language, links_history)
		
	return links_history
		
class Analyze:

	def __init__(self, data, language, topic, daily=True):
		self.data = data
		self.language = language
		self.topic = topic
		self.daily_data, self.timestamps, self.dates = self._one_per_timestamp(daily)
		
	def _timestamp2date(self, timestamp, daily=True):
		''' Convert timestamps to US datetime format. '''
		year = timestamp[:4]
		month = timestamp[5:7]

		if daily:
			day = timestamp[8:10]
			date = "%s-%s-%s" % (year, month, day)
		else:
			date = timestamp
			#date = "%s-%s" % (year, month)
		return date

	def _one_per_timestamp(self, daily=True):
		''' Filter so revision history has one entry per month or day, i.e. page on YYYY/MM or YYYY/MM/DD.'''

		self.timestamps = sorted(list(self.data.keys()))
		self.dates = [self._timestamp2date(ts, daily) for ts in self.timestamps]

		for n in range(1,len(self.dates)):
			if self.dates[n] == self.dates[n-1]:
				del self.data[self.timestamps[n-1]]

		self.timestamps = sorted(list(self.data.keys()))
		self.dates = [self._timestamp2date(timestamp) for timestamp in self.timestamps]

		return self.data, self.timestamps, self.dates

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
				# added_elements[self.dates[n]] = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				# removed_elements[self.dates[n]] = []

				added_counts.append(1)
				removed_counts.append(0)
			else:
				curr = [x.lower() for x in self.data[self.timestamps[n]][element_type]]
				prev = [x.lower() for x in self.data[self.timestamps[n-1]][element_type]]

				added, removed = diff_lists(curr, prev)
				added_elements[self.timestamps[n]] = added
				removed_elements[self.timestamps[n]] = removed
				# added_elements[self.dates[n]] = added
				# removed_elements[self.dates[n]] = removed

				if len(added) == 0: added_counts.append(0)
				else: added_counts.append(len(added)/curr_total)
				if len(removed) == 0: removed_counts.append(0)
				else: removed_counts.append(-len(removed)/curr_total)

		if remove_vandalism:
			# todo: remove counts from added/removed_counts if vandalism
			added_elements, removed_elements = self._remove_vandalism(added_elements, removed_elements)

		if visualize:
			uviz.plot_barchart(self.timestamps, added_counts, removed_counts, self.topic, self.language, element_type)

		return added_counts, removed_counts, total_counts

	def counter_development(self, element_type, remove_vandalism=False, visualize=False):
		''' Analyze and plot the development of links or urls over time. '''
		# Veel van de diffs in lists zijn kleine verschillen in spelling of specificatie, e.g. "anna", "anna (phd)"
		removed_counts = []
		added_counts = []
		total_counts = []
			
		for n in range(len(self.timestamps)):
			curr_total = sum(self.data[self.timestamps[n]][element_type].values())
			total_counts.append(curr_total)
			if n == 0: 
				added_counts.append(1)
				removed_counts.append(0)
			else:
				curr = self.data[self.timestamps[n]][element_type]
				prev = self.data[self.timestamps[n-1]][element_type]

				added, removed = diff_counters(curr, prev)
				if added == 0: added_counts.append(0)
				else: added_counts.append(added/curr_total)
				if removed == 0: removed_counts.append(0)
				else: removed_counts.append(removed/curr_total)

		if visualize:
			uviz.plot_barchart(self.dates, added_counts, removed_counts, self.topic, self.language, element_type)

		return added_counts, removed_counts, total_counts

	def string_development(self, element_type, visualize=False):

		added = []
		removed = []
		totals = []

		for n in range(len(self.timestamps)):
			curr_total = len(self.data[self.timestamps[n]][element_type].split())
			
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
					removed.append(diff/curr_total)
				elif diff > 0:
					added.append(diff/curr_total)
					removed.append(0)

		if visualize:
			uviz.plot_barchart(self.dates, added, removed, self.topic, self.language, element_type)

		return added, removed, totals
"""
