#!/usr/bin/python3
"""

	Gets data from Wikipedia given language(s) and topic 
	Uses the Wikipedia API.

	a.k.jorgensen@uva.nl
	November 2019

"""
from Wikipedia.wikipedia import wikipedia
from Wikipedia.wikipedia import exceptions

from collections import defaultdict
from datetime import datetime

def get_wiki_data(language, title):

	wikipedia.set_lang(language)

	# make "refugee crisis" "refugee_crisis"
	if len(title.split()) > 1:
		title = '_'.join(title.split())
		print("Edited title:\t", title)	
	
	try:
		page = wikipedia.WikipediaPage(title)
		data = defaultdict()

		data['_TODAY_'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
		data['_TITLE_'] = title

		data["categories"] = page.categories
		data["content"] = page.content
		data["links"] = page.links
		data["images"] = page.images
		data["references"] = page.references
		data["revision_id"] = page.revision_id
		data["revisions"] = page.revisions
		data["sections"] = page.sections

		# coordinates are Decimal sometimes, need to be floats for JSON
		if page.coordinates is not None:
			data["coordinates"] = (float(page.coordinates[0]), float(page.coordinates[1]))

		return data

	except exceptions.PageError:
		print("There is no '%s' page in the '%s' language version of Wikipedia, try another one" % (title, language))
		return None


if __name__ == "__main__":
	get_wiki_data()