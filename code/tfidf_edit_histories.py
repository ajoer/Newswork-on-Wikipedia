#!/usr/bin/python3
"""
	Get term tfidf in the revision history of a Wikipedia article. 
"""

import argparse
import general
import math
import numpy
import process_revision
import string
import visualize

from collections import defaultdict, Counter

parser = argparse.ArgumentParser(description=''' ''')

parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()

def get_content_data(revision):
	''' Get entities and their frequencies '''

	if not "texthidden" in revision["slots"]["main"].keys():

		timestamp = revision["timestamp"]
		content = process_revision.process_revision(revision, elements="content")

		word_counter = Counter(content)

	return word_counter, timestamp

def get_number_of_docs(BoW, words_history):

	num_of_docs = Counter()

	for w in BoW:
		for timestamp in words_history:
			if w in words_history[timestamp].keys():
				num_of_docs[w] += 1
	return num_of_docs

def calculate_tfidf(w, words, word_in_num_of_docs, total_num_of_docs):

	# print("word freq", words[w])
	# print("total", sum(words.values()))
	# print("num of docs", total_num_of_docs)
	# print("num of docs with w", words_in_num_of_docs[w])

	tf = words[w] / sum(words.values())
	idf = math.log(total_num_of_docs / word_in_num_of_docs)

	tfidf = tf * idf
	return tfidf

def get_tfidf_for_timestamps(words_history, BoW, words_in_num_of_docs, total_num_of_docs):
	for timestamp in words_history:
		tfidfs = Counter()

		for w in words_history[timestamp]:

			tfidf = calculate_tfidf(w, words_history[timestamp], words_in_num_of_docs[w], total_num_of_docs)
			tfidfs[w] = tfidf

		print(timestamp)
		print("top tfidfs:")
		top_tfidfs = []
		for (k,v) in tfidfs.most_common(50):
			top_tfidfs.append(k)
		print(' - '.join(top_tfidfs))
		print()
		print()


def main():

	for data, language in general.open_data("processed", args.topic):

		revisions = data['revisions']
		BoW = []
		words_history = defaultdict()
		total_num_of_docs = len(revisions)

		for revision in revisions:

			word_counter, timestamp = get_content_data(revision)

			words_history[timestamp] = word_counter
			BoW += word_counter.keys()

		BoW = set(BoW)
		words_in_num_of_docs = get_number_of_docs(BoW, words_history)

		get_tfidf_for_timestamps(words_history, BoW, words_in_num_of_docs, total_num_of_docs)

if __name__ == "__main__":
	main()