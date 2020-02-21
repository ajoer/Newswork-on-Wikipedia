#!/usr/bin/python3
"""
	Get and parse Wikipedia revision histories from selected languages on a topic. 
	Ouput: JSON with parsed and tokenized revision histories. One file per language.
"""
import argparse
import utils_io as uio
import WikiRevisionParser.wikirevparser as wikirevparser

argsparser = argparse.ArgumentParser(description='''Get and parse edit histories of Wikipedia language versions.''')
argsparser.add_argument("event", help="e.g. 'refugee_crisis'.")
argsparser.add_argument("--language", help="e.g. 'da'. (for debugging)")
argsparser.add_argument("--check_os", default="y", help="e.g. 'y'. (for debugging)")

args = argsparser.parse_args()

def get_data():

	input_data = open("resources/events/%s.txt" % args.event).readlines()

	for line in sorted(input_data):
		language, title = line.split('\t')[0], line.split('\t')[1].strip()
		
		if args.language:
			if language != args.language: continue

		if args.check_os == "y":
			if uio.check_if_exists(args.event, language): 
				print("%s has already been parsed for %s" %(args.event, language)) 
				continue
			else:
				print(args.event, language)
		
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		parser_instance = wikirevparser.ProcessRevisions(language, title)

		page = parser_instance.wikipedia_page()
		if page == None: continue

		data = parser_instance.parse_revisions()
		if data == None: continue

		uio.save_to_json(args.event, language, data)
		
if __name__ == "__main__":
	get_data()