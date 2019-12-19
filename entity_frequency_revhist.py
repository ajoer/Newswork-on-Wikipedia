#!/usr/bin/python3
"""
	Get entities (blue links) and their frequency for each timepoint in the revision history of a Wikipedia article. 
"""

import argparse
import general
import numpy
import process_revision
import visualize

from collections import defaultdict, Counter

parser = argparse.ArgumentParser(description=''' Get entities (blue links) and their frequency for each 
								timepoint in the revision history of a Wikipedia article. 
								Data format is a dict(lambda: dict(list)) with a dict for each timestamp and a list for each entity with 
								[count, relative frequency in relation to content, relative frequency in relation to other entities, most salient word for entity]. 
								Output is saved as a dictionary to output/entity_frequency/<topic>/<topic>_<language>_ef.json. ''')

parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()

# TODO(akj): add most salient word for each entity from entity page.

def get_entity_data(revisions):
	''' Get entities and their frequencies '''
	entities_history = defaultdict(lambda: dict(list))

	for revision in revisions:
		
		if not "texthidden" in revision["slots"]["main"].keys():

			entities_data = dict()
			timestamp = revision["timestamp"]
			links, content = process_revision.process_revision(revision, elements="entities")
			 
			entities = Counter(links)
			len_of_content = len(content)
			sum_of_entities = sum(entities.values())

			for entity in entities:

				frequency = entities[entity]
				entity_data = [frequency, round(frequency/len_of_content,2), round(frequency/sum_of_entities,2)]
				entities_data[entity] = entity_data

			entities_history[timestamp] = entities_data

	return entities_history

def main():

	for data, language in general.open_data("processed", args.topic):

		revisions = data['revisions']
		entities_history = get_entity_data(revisions)

		general.save_to_json(args.topic, language, entities_history, "entity_frequency")

if __name__ == "__main__":
	main()