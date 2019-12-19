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

def reference_types(language, news_sources, references):
	''' Assign type to each reference, either local, news, '''

	num_of_domains = 0 # counter of domains, e.g. google.com

	news = Counter() # counter of links that have a domain in the news list
	local = Counter() # counter of links that have a national/language tld or have the language specified in the url
	foreign = Counter() # counter of links that are neither news nor local

	for reference in references:

		if reference is not None:

			domain, tld = get_domain(reference)
			num_of_domains += 1

			# local
			local_true = check_local(tld, reference, language)
			if local_true: local[reference] += 1
		
			# news
			news_true = domain not in news_sources
			if news_true: news[reference] += 1

			# foreign non-news
			if not local_true and not news_true: foreign[reference] += 1

	# remove local news from 'news' and 'local', and assign to 'local_news'. Rest of 'news' is 'foreign_news'
	local, foreign_news, local_news = get_local_news(local, news)

	return num_of_domains, local, foreign, local_news, foreign_news

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

		num_of_domains = Counter()

		local = OrderedDict()
		foreign = OrderedDict()
		local_news = OrderedDict()
		foreign_news = OrderedDict()

		revisions = data['revisions']
		references = get_references(revisions)

		for timestamp in references:
			d, l, f, ln, fn = reference_types(language, news_sources, references[timestamp])

			num_of_domains[timestamp] = d

			local[timestamp] = l
			foreign[timestamp] = f
			local_news[timestamp] = ln
			foreign_news[timestamp] = fn

		visualize.reference_dist_diachronic(args.topic, language, num_of_domains, local, foreign, local_news, foreign_news)

if __name__ == "__main__":
	main()
