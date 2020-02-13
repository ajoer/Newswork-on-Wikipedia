import argparse
import utils
import WikiRevisionParser.parser as parser

argsparser = argparse.ArgumentParser(description='''Get and parse edit histories of Wikipedia language versions.''')
argsparser.add_argument("event", help="e.g. 'refugee_crisis'.")
argsparser.add_argument("--language", help="e.g. 'da'. (for debugging)")
argsparser.add_argument("--check_os", help="e.g. 'y'. (for debugging)")

args = argsparser.parse_args()

def get_data():

	input_data = open("resources/events/%s.txt" % args.event).readlines()

	for line in sorted(input_data):
		language, title = line.split(',')[0], line.split(',')[1].strip()
		
		if args.language:
			if language != args.language: continue

		if args.check_os == "y":
			if utils.check_if_exists(args.event, language): 
				print("%s has already been parsed for %s" %(args.event, language)) 
				continue
		
		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		data = parser.ProcessRevisions(language, title).data
		utils.save_to_json(args.event, language, data)

if __name__ == "__main__":
	get_data()