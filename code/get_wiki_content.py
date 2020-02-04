#!/usr/bin/python3
"""
	Gets page + complete edit history from Wikipedia given language and a topic. 
	Uses the Wikipedia API.
	Returns full page + edit history in a Wikipedia page object for the language.
"""

from urllib.request import urlopen
from Wikipedia.wikipedia import wikipedia
from Wikipedia.wikipedia import exceptions

def main(language, title):
	''' Get wikipedia revision history for a title in a given language and yield output'''
	
	wikipedia.set_lang(language)

	# add underscore in multiword titles: "refugee crisis" --> "refugee_crisis"
	if len(title.split()) > 1:
		title = '_'.join(title.split())
		print("Edited title:\t", title)	
	
	print("Getting data for %s..." % language)
	try:
		page = wikipedia.WikipediaPage(title)
		return page

	except exceptions.PageError:
		print("There is no '%s' page in the '%s' language version of Wikipedia, try another one" % (title, language))
		return None


if __name__ == "__main__":
	main()