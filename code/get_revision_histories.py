#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: txt file with tab separated language, title pairs, e.g. 'refugee_crisis'
	Ouput: yield revision history dictionary with clean data. 
	Output fields: tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""

import argparse
import get_wiki_content
import nltk
import re
import revision_parser
import string
import utils

from collections import Counter, defaultdict, OrderedDict

parser = argparse.ArgumentParser(description='''Get and parse edit histories of Wikipedia language versions.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")
parser.add_argument("--language", help="e.g. 'da'. (for debugging)")

args = parser.parse_args()

def parse_revisions(revisions):

	for n, revision in enumerate(revisions):
		parsed_data = defaultdict()
		timestamp = revision["timestamp"]
		content = revision["slots"]["main"]["*"]

		content, tlds_origin, reference_template_types = revision_parser.parse_references(content)
		content, images, captions, links_from_captions = revision_parser.parse_images(content)
		content, links, categories = revision_parser.parse_links_categories(content)
		content, sections = revision_parser.parse_sections(content)
		content = revision_parser.parse_text(content) 

		parsed_data["tlds_origin"] = tlds_origin
		parsed_data["reference_template_types"] = reference_template_types
		parsed_data["images"] = images
		parsed_data["captions"] = captions
		parsed_data["links"] = links + links_from_captions
		parsed_data["categories"] = categories
		parsed_data["sections"] = sections
		parsed_data["content"] = content

		yield timestamp, parsed_data

def main():

	input_data = open("data/topics/%s.txt" % args.topic).readlines()

	for line in sorted(input_data):
		language, title = line.split(',')[0], line.split(',')[1].strip()
		
		if args.language:
			if language != args.language: continue
		
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		data = get_wiki_content.main(language, title) # Wikipedia page object, dict-like

		if data == None: continue

		revisions = data.revisions
		output_data = OrderedDict()


		print("Parsing %s..." % language)
		for timestamp, parsed_data in parse_revisions(revisions):
			output_data[timestamp] = parsed_data

		utils.save_to_json(args.topic, language, output_data, "parsed")

if __name__ == "__main__":
	main()