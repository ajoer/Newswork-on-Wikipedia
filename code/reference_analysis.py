#!/usr/bin/python3
"""
	Process reference data from Wikipedia, from JSON files
"""

import argparse
import glob
import general
import preprocess
import visualize

from collections import Counter, defaultdict
from enum import Enum

parser = argparse.ArgumentParser(description='Process JSON file containing Wikipedia dumps.')
parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()

# output:
# ----  the input is the list of references, just need to split them into categories. ------
## news, language, non_news, non_language = sets of references
## counter of domains
## counter of TLDs 

## right now, nws 


#list of languages that have other letter combinations for domain
language_domain = {
	"da": "dk",
	"en": "uk",
	"nl": "be",
	"nn": "no",
	"sv": "se"
}

def reference_types(language, timestamp, news_sources, list_of_references):

	domain_counter = Counter() # counter of domains, e.g. google.com
	tld_counter = Counter() # counter of top-level domain, e.g. com

	news = Counter() # counter of links that have a domain in the news list
	local = Counter() # counter of links that have a national/language tld or have the language specified in the url
	local_news = Counter() # counter of links that are in the news and local counters simultaneously


	for reference in list_of_references:

		domain = reference.split('/')[0]
		if domain.startswith("www"):
			domain = domain[4:]
		domain_counter[domain] += 1
		
		tld = domain.split('.')[-1]
		tld_counter[tld] += 1

		# Local domains
		if tld == language or "/"+language+"/" in reference:
			local[reference] += 1

		elif language in language_domain.keys():
			if tld == language_domain[language]:
				local[reference] += 1

		# news domains
		if domain in news_sources:
			news[reference] += 1

	local_keys = {x for x in local.keys()}
	news_keys = {x for x in news.keys()}
	for key in local_keys.intersection(news_keys):
		local_news[key] = local[key]
		if local[key] != news[key]:
			print("they dont match:\t", local[key], news[key])

	#if len(list_of_references) > 0:
	#	print("local_news makes up %s percent of the references, of which there are %s" % (round((len(local_news) / len(list_of_references) *100),2), len(list_of_references)))
	# print("domain_counter", sum(domain_counter.values()))
	# print("tld_counter", sum(tld_counter.values()))
	# print("local", sum(local.values()))
	# print("news", sum(news.values()))

	return domain_counter, tld_counter, local, news, local_news


def main():
	
	input_files = glob.glob("output/processed/%s/*.json" % args.topic)

	for file_name in sorted(input_files):

		data = general.read_from_json(file_name)
		language = file_name.split('/')[-1].split('_')[-2]

		print("\nLanguage:\t", language)
		print("Title:\t\t", args.topic)

		news_files = glob.glob("data/news_sources/*.txt")
		news_sources = []
		for news_file in news_files:
			for x in open(news_file).read().strip().split():
				news_sources.append(x)
		
		# dictionaries with reference information per timestamp
		dict_of_domain_counters = defaultdict()
		dict_of_tld_counters = defaultdict()
		dict_of_local_counters = defaultdict()
		dict_of_news_counters = defaultdict()
		dict_of_localnews_counters = defaultdict()

		# latest
		timestamp = data["_TODAY_"]
		domain_counter, tld_counter, local, news, local_news = reference_types(language, timestamp, news_sources, data['references'])
		
		dict_of_domain_counters[timestamp] = domain_counter
		dict_of_tld_counters[timestamp] = tld_counter
		dict_of_local_counters[timestamp] = local
		dict_of_news_counters[timestamp] = news
		dict_of_localnews_counters[timestamp] = local_news
		
		# revisions
		revisions = data['revision_references']
		for rev in revisions:
			timestamp = rev
			domain_counter, tld_counter, local, news, local_news = reference_types(language, rev, news_sources, revisions[rev])

			dict_of_domain_counters[timestamp] = domain_counter
			dict_of_tld_counters[timestamp] = tld_counter
			dict_of_local_counters[timestamp] = local
			dict_of_news_counters[timestamp] = news
			dict_of_localnews_counters[timestamp] = local_news
		
		print(50*"*")
		print(len(dict_of_domain_counters.keys()))
		#visualize.diachronic_distribution_references(args.topic, language, dict_of_news_counters, dict_of_local_counters, dict_of_localnews_counters, dict_of_domain_counters)

if __name__ == "__main__":
	main()


