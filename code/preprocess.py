#!/usr/bin/python3

import argparse
import json
import nltk

from get_data import save_to_json

parser = argparse.ArgumentParser(description='Preprocess Wikipedia data, e.g. images, text, links, revisions')
parser.add_argument("--titles", default="brexit", help="title of a Wikipedia page, str, e.g. 'Brexit'.")
parser.add_argument("--languages", default="no", help="two letter language code, str, e.g. 'en'.")
parser.add_argument("--date", default="191115", help="six digit date of Wikipedia scrape, str, e.g. '191115'.")
parser.add_argument("--save", default="n", help="save to location, str, 'y' or 'n'.")

args = parser.parse_args()


def process_categories(categories_list):
	''' clean the label "category" off the categories '''

	clean_categories = []

	for category in categories_list:
		category = category.split(":",1)[1:]
		clean_categories.append(category)

	return clean_categories

def process_content(content):
	''' tokenizes and lower cases '''

	nltk.word_tokenize(content)
	clean_content = ' '.join(x.lower() for x in content)

	return clean_content


def process_images(image_list):
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

def process_rawWiki():

	for language in args.languages.split(','):
		for title in args.titles.split(','):
			json_file = open('./output/raw/%s_%s_%s_raw.json' % (title, language, args.date))

			data = json.load(json_file)
			data['categories'] = process_categories(data['categories'])
			data['content'] = process_content(data['content'])
			data['images'] = process_images(data['images'])

			if args.save == "y":
		 		save_to_json(data, title, language, "processed")

process_rawWiki()


