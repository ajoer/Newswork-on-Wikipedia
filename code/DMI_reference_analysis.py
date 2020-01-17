#!/usr/bin/python3
"""
	Process reference data from Wikipedia, from JSON files
"""

import argparse
import glob
import general
import process_revision
import visualize

from collections import Counter, OrderedDict
from enum import Enum

parser = argparse.ArgumentParser(description='Process JSON file containing Wikipedia dumps.')
parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()

language_domain = {
	"da": "dk",
	"en": "uk",
	"nl": "be",
	"nn": "no",
	"sv": "se"
}

news_sources = []
for news_file in glob.glob("data/news_sources/*.txt"):
	for news_source in open(news_file).read().strip().split():
		news_sources.append(news_source)

def get_domain(reference):
	domain = reference.split('/')[0]
	if domain.startswith("www"):
		domain = domain[4:]

	tld = domain.split('.')[-1]
	return domain, tld

def check_local(tld, reference, language):
	if tld == language or "/"+language+"/" in reference:
		return True

	elif language in language_domain.keys():
		if tld == language_domain[language]:
			return True

	elif language == "en":
		if tld in ["org", "com", "net"]:
			return True

def get_local_news(local, news):
	local_news = Counter() # counter of links that are in the news and local counters simultaneously

	local_keys = {x for x in local.keys()}
	news_keys = {x for x in news.keys()}

	for key in local_keys.intersection(news_keys):
		local_news[key] = local[key]
		del local[key]
		del news[key]

	# what is left in news is now foreign
	return local, news, local_news

def reference_origin(language, references):
	''' Assign type to each reference, either local, news, '''

	num_of_domains = 0 # counter of domains, e.g. google.com

	local = 0 # counter of links that have a national/language tld or have the language specified in the url
	foreign = 0 # counter of links that are neither news nor local
	origin_counter = Counter()

	for reference in references:

		if reference is not None:

			domain, tld = get_domain(reference)
			num_of_domains += 1

			origin_counter[tld] += 1

			# local
			local_true = check_local(tld, reference, language)
			if local_true: local += 1
			else: foreign += 1

	for tld in origin_counter:
		origin_counter[tld] = origin_counter[tld]/num_of_domains

	return num_of_domains, local, foreign, origin_counter

def get_references(revisions):
	''' Get references from the content of a revision. Output is a dictionary of references per timestamp. '''
	revision_references = dict()

	for rev in revisions:
		try:

			timestamp = rev["timestamp"]
			references = process_revision.process_revision(rev, elements="revision_references")
			
			if references is not None:
				revision_references[timestamp] = references

		except KeyError:
			pass

	return revision_references

def main():

	for data, language in general.open_data("processed", args.topic):

		revisions = data['revisions']
		print("num of revisions", len(revisions))
		references = get_references(revisions)

		local = []
		foreign = []
		timestamps = []
		origins = []
		dates = []

		for timestamp in references:
			
			d, l, f, origin_counter = reference_origin(language, references[timestamp])

			num_of_domains = d
			if d != 0:
				timestamps.append(timestamp)
				local.append(l/d)
				foreign.append(f/d)
				origins.append(origin_counter)

		timestamps.reverse()
		local.reverse()
		foreign.reverse()
		origins.reverse()

		for n,timestamp in enumerate(timestamps):
			year = timestamp[:4]
			month = timestamp[5:7]
			day = timestamp[8:10]
			date = "%s/%s/%s" % (month, day, year)

			if date not in dates:
				# for RAWGraphs input:
				for tld in origins[n]:
					print(date, "\t", tld, "\t", origins[n][tld])
				#print(date, "\tLocal\t", local[n])
				#print(date, "\tForeign\t", foreign[n])
				dates.append(date)

			#visualize.DMI_reference_dist_diachronic(args.topic, language, local, foreign)

if __name__ == "__main__":
	main()
