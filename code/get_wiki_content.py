#!/usr/bin/python3
"""
	Gets page + complete edit history from Wikipedia given language(s) and a topic. 
	Uses the Wikipedia API.
	Yiels full page + edit history in a Wikipedia page object.
"""

from urllib.request import urlopen
from Wikipedia.wikipedia import wikipedia
from Wikipedia.wikipedia import exceptions

def get_wiki_data(language, title):
	''' Get wikipedia revision history for a title in a given language and yield output'''
	
	wikipedia.set_lang(language)

	# add underscore in multiword titles: "refugee crisis" --> "refugee_crisis"
	if len(title.split()) > 1:
		title = '_'.join(title.split())
		print("Edited title:\t", title)	
	
	try:
		page = wikipedia.WikipediaPage(title)
		return page

	except exceptions.PageError:
		print("There is no '%s' page in the '%s' language version of Wikipedia, try another one" % (title, language))
		return None

def main(topic):

	input_data = open("data/topics/%s.txt" % topic).readlines()

	for line in sorted(input_data):
		language, title = line.split(',')[0], line.split(',')[1].strip()

		print("\nLanguage:\t", language)
		print("Title:\t\t", title)

		data = get_wiki_data(language, title)
		yield data, language

if __name__ == "__main__":
	main()