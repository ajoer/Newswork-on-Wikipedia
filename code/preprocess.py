#!/usr/bin/python3
"""

	Preprocesses Wikipedia data.

	a.k.jorgensen@uva.nl
	November 2019

"""
import nltk

from collections import defaultdict

def preprocess_categories(categories_list):
	''' clean the label "category" off the categories '''

	clean_categories = []
	for category in categories_list:
		category = category.split(":",1)[1:]
		clean_categories.append(''.join(category))
	return clean_categories

def preprocess_content(content):
	''' tokenizes and lower cases '''

	content = nltk.word_tokenize(content)
	return ' '.join(content)

def preprocess_images(image_list):
	''' the images have an .upload. name in Wikipedia, 
	but the url to their location in Wikimedia is different.'''

	clean_image_urls = []

	for image in image_list:
		if "wikimedia" in image:
			name_of_image = image.split('/')[-1] 
			image_url = "https://commons.wikimedia.org/wiki/File:" + name_of_image
			clean_image_urls.append(image_url)

		else:
			print("There seems to be an image with a location outside of Wikimedia:\t", image)

	return clean_image_urls

def preprocess_references(references_list):
	''' clean the "https://" or "http://" off the references '''	
	clean_references = []
	for reference in references_list:
		if not reference.startswith("http"):
			print("Here's a reference which is not a link:\t", reference)
		else:
			reference = reference.split("//")[-1]
			clean_references.append(reference)

	return clean_references

def get_references_from_revisions(revisions):
	''' pulls the references out of the content of a revision history 
		output = dict with list of references at each revision timestamp '''

	revision_references = defaultdict()
	for rev in revisions:
		references = []
		timestamp = rev["timestamp"]
		content = rev["slots"]["main"]["*"]
		content = preprocess_content(content)
		
		for word in content.strip().split():
			if word.startswith("//www."):
				reference = word[6:]
				references.append(reference)

		revision_references[timestamp] = references
	return revision_references

if __name__ == "__main__":
	process_categories()
	process_content()
	process_images()
	preprocess_references()
	get_references_from_revisions()


