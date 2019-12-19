#!/usr/bin/python3
"""
	Get points of interest from revision history with significant change. 
"""
import argparse
import general
import numpy
import process_revision
import visualize

from collections import defaultdict

parser = argparse.ArgumentParser(description=''' Get the points of interest (PoI) in an article's edit history. 
								PoIs are seen as edits of significant change in an article's history. 
								Change is the sum of percentage change from t1 to t2 across a number of measurable elements. 
								The value is assigned to t2. Timestamp changes > XX percentile are made Points of Interest. 
								Output is saved as a dictionary to output/poi/<topic>/<topic>_<language>_poi.json. ''')
parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()


def make_revision_representation(revisions):
	''' Get data for PoI. '''
	revision_representations = []
	timestamps = []
	revision_data = defaultdict(lambda: dict())

	for revision in revisions:

		if not "texthidden" in revision["slots"]["main"].keys():

			timestamp = revision["timestamp"]
			timestamps.append(timestamp)
			timestamp_output = process_revision.process_revision(revision, elements="all")

			if not timestamp_output == None:
				revision_data[timestamp] = timestamp_output
				representation = []

				for key in timestamp_output:
					if type(timestamp_output[key]) == int:
						representation.append(timestamp_output[key])
					if type(timestamp_output[key]) == list:
						representation.append(len(timestamp_output[key]))

				revision_representations.append(numpy.array(representation))

	revision_representations.reverse(), timestamps.reverse()
	print("there are %d revisions in this history" % len(timestamps))

	return revision_representations, timestamps, revision_data

def get_pois(revision_changes, timestamps, revision_data, percentile_number):
	''' Get revision history changes with percentage change scores in the XX percentile. '''

	percentile = numpy.percentile(revision_changes, percentile_number)
	output = defaultdict()
	tsv_output = [("timestamp"," sum of percentage changes")]

	for n, revision_change in enumerate(revision_changes):
		
		if revision_change > percentile:
			timestamp = timestamps[n+1]
			output[timestamp] = revision_data[timestamp]
			output[timestamp]["perc_change"] = revision_change
			tsv_output.append((timestamp, revision_change))

	return output, tsv_output

def percentage_change(v1, v2):

	if not v1 == 0:
		abs_diff = abs(v1-v2)
		perc_change = (abs_diff / abs(v1))
		return perc_change
	else:
		return 0

def get_revision_PC(revision_representations):
	''' Calculate the percentage change for each revision history. '''
	
	revision_changes = []

	for n, revision in enumerate(revision_representations):

		if n < len(revision_representations)-1:
			revision_change = 0
			next_revision = revision_representations[n+1]
			
			for m, (v1, v2) in enumerate(zip(revision, next_revision)):
				revision_change += percentage_change(v1, v2) / len(revision)

			revision_changes.append(round(revision_change,2))

	return revision_changes

def main():

	for data, language in general.open_data("processed", args.topic):

		# data:
		revisions = data['revisions']
		revision_representations, timestamps, revision_data = make_revision_representation(revisions)
		
		# get PoIs:
		revision_changes = get_revision_PC(revision_representations)
		
		# save to json
		if len(revision_changes) <= 150:
			percentile_number = 80

		elif 150 < len(revision_changes) <= 250:
			percentile_number = 90

		elif 250 < len(revision_changes) < 350:
			percentile_number = 95

		else:
			percentile_number = 98

		output, tsv_output = get_pois(revision_changes, timestamps, revision_data, percentile_number)
		general.save_to_json(args.topic, language, output, "poi")
		general.save_pois_to_tsv(args.topic, language, tsv_output, "poi")


if __name__ == "__main__":
	main()