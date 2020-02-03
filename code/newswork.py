#!/usr/bin/python3
"""
	Analyze edit histories of Wikipedia language versions for newsiness and encyclopedia-ness. 
"""

import argparse
import general
import nltk
import numpy
import process_revision
import re
import string
import visualize

from collections import defaultdict, Counter, OrderedDict

parser = argparse.ArgumentParser(description=''' Analyze edit histories of Wikipedia language versions for newsiness and encyclopedia-ness. ''')
parser.add_argument("topic", default="test", help="Location of input JSON file(s), str.")
parser.add_argument("--language", help="language code(s), str")

args = parser.parse_args()

regex_letters = "\dA-Za-zğäåæáéëíıïóøöúü"
regex_symbols = "\"'(){}[\]&=«»:.,?_~–\-/| "

def get_links(string):

	links = []
	texts = []

	double_square_bracket, content_subbed = extract_elements(r"\[\[(.*?)\]\]", string)
	for element in double_square_bracket:
		elements = element.split("|")

		if len(elements) > 1:
			link, text = elements[0], elements[1].strip("]]")
			links.append(link)
			texts.append(text)
		else: 
			link, text = elements[0], elements[0].strip("]]").strip("[[")
			links.append(link)
			texts.append(text)
	return links, texts

def extract_images(content):
	''' Extract and plot images over time.'''
	images = []
	captions = []
	links_from_captions = []
	extensions = [".jpg", ".svg", ".png"]

	for line in content.split("\n"):
		for extension in extensions:

			if extension in line.lower():
				content = content.replace(line, "")
				image_title, image_extension = re.search(r"(:|=)([^(:|=)].*)(.jpg|.svg|.png|.JPG|.SVG|.PNG)", line).group(2,3)

				if ":" in image_title:
					image_title = image_title.split(":")[-1]

				image_title = '_'.join([x for x in image_title.split()])
				image_link = "https://commons.wikimedia.org/wiki/File:" + image_title + image_extension

				images.append(image_link)

				# Get captions
				# Some languages (e.g. EN) make use of this structure for captions: "alt=British soldiers....". They can have links in the caption.
				if "|alt=" in line:

					elements = line.split("|alt=")[-1].split("|")[1:]
					caption = '|'.join(elements)[:-2]
					content = content.replace(line, caption)
					links, texts = get_links(caption)
					
					for link, text in zip(links, texts):
						caption = caption.replace("[[%s]]" % link, text)
						caption = caption.replace("[[%s|%s]]" % (link, text), text)
						content = content.replace("[[%s]]" % link, text)
						content = content.replace("[[%s|%s]]" % (link, text), text)
						links_from_captions.append(link)
					captions.append(caption)

				# Other languages (e.g. NL) do not...
				else:
					caption = re.search(r"\|([^|]*)\]\]", line)
					if caption: 
						caption = caption.group(1)

						# remove image mark up
						if not "px" in caption:
							links, texts = get_links(caption)
							#remove links
							for link, text in zip(links, texts):
								caption = caption.replace("[[%s]]" % link, text)
								caption = caption.replace("[[%s|%s]]" % (link, text), text)
								content = content.replace("[[%s]]" % link, text)
								content = content.replace("[[%s|%s]]" % (link, text), text)
								links_from_captions.append(link)
							captions.append(caption)

	return content, images, captions, links_from_captions
		

def get_links_categories(content):
	# Extract links and categories from an edit history. Must be run after get_images() because images have the same markup, and will otherwise feature as links.
	categories = []

	links, texts = get_links(content)
	
	for link, text in zip(links,texts):
		# filter out categories:
		if ":" in link:
			category = link.split(":")[1]

			categories.append(category)
			links.remove(link)
			content = content.replace("[[%s]]" % link, "")

		else:
			links.append(link)
			content = content.replace("[[%s]]" % link, text)

	return content, links, categories

def extract_elements(regex, content):
	# Reg ex to get all references/citations in an edit history.

	exp = re.compile(regex)
	hits = exp.findall(content)
	content = re.sub(exp, '', content)

	return hits, content

def get_urls(input_list):

	urls = []
	http_regex = "http[s]*:\/\/([^ ]*)"

	for element in input_list:
		# they differ in endings:
		url = re.search(http_regex + r"( |}})", element)
		if url:
			url = url.group(1).split("|")[0]
		else:
			url = re.search(http_regex, element)
			if url:
				url = url.group(1).split("|")[0]
		if not url is None:
			if "www" in url:
				url = url[4:]
			urls.append(url)
	return urls

def extract_tlds(url_list):
	# Extract the tlds from each url in a reference/citation block in an edit history.
	tlds = Counter()

	for url in url_list:
		tld = url.split("/")[0].split(".")[-1]
		tlds[tld] += 1

	return tlds 

def extract_reference_type(input_list):
	# Extract the reference type from a reference/citation block in an edit history, e.g. "book", "thesis", "news" etc.
	types = Counter()

	for element in input_list:
		try:
			reference_type = re.search("{{[c|C]ite (.*?)( |\|)", element).group(1)
			types[reference_type] += 1
		except AttributeError:
			pass
			types[None] += 1
	return types

def extract_sections(content):
	# Extract sections from edit history

	sections = []
	header1s, content = extract_elements(r"[^=]={2}([^=].*?)={2}", content)
	header2s, content = extract_elements(r"[^=]={3}([^=].*?)={3}", content)
	header3s, content = extract_elements(r"[^=]={4}([^=].*?)={4}", content)
	sections.append([x.strip() for x in header1s])
	sections.append([x.strip("=").strip() for x in header2s])
	sections.append([x.strip("==").strip() for x in header3s])

	return content, sections

def get_references(content):
	''' Extract and analyze references and their origin (tld) over time.'''
	reference_template_types = Counter() # some references have "type" markup, e.g. "book", "thesis", "news" etc.

	# References
	references, content = extract_elements(r"<ref(.*?)<\/ref>", content) 
	# Citations
	citations, content = extract_elements(r"{{[c|C]ite [" + regex_letters + regex_symbols + ">]+}}", content)

	# some References are in External Links section w/o markup
	external_links = get_urls([x for x in content.split()])
	#TODO: remove external links from content

	urls = get_urls(references + citations)

	tlds_origin = extract_tlds(urls + external_links)
	reference_types = extract_reference_type(references + citations)
	reference_template_types += reference_types
	return content, tlds_origin, reference_template_types

def clean_text(content):
	# Clean remaining content for tables, noise and image markup. Also cleans italics markup.

	clean_content = []

	italics, content = extract_elements(r"\'\'", content)

	for line in content.split("\n"):
		if len(line) > 0:
			if not line[0] in string.punctuation and "px" not in line: 

				# Add end punct to lines
				if line[-1] not in string.punctuation:
					line += "."
				clean_content.append(line)

	content = ' '.join([w for w in clean_content])
	content = ' '.join(nltk.word_tokenize(content))
	return content
	
def main():

	for data, language in general.open_data("processed", args.topic):
		if language == "da":
		
			revisions = data['revisions']

			for n,revision in enumerate(revisions):
				if n < 10:
					timestamp = revision["timestamp"]
					content = revision["slots"]["main"]["*"]

					#remove all valuable aspects from the content, before cleaning the text
					content, tlds_origin, reference_template_types = get_references(content)
					content, images, captions, links_from_captions = extract_images(content)
					content, links, categories = get_links_categories(content)
					links += links_from_captions
					content, sections = extract_sections(content)
					content = clean_text(content) 

					print("tlds_origin\t", tlds_origin)
					print("reference_template_types\t", reference_template_types)
					print("images\t\t", images)
					print("captions\t\t", captions)
					print("links\t\t", links)
					print("categories\t", categories)
					print("sections\t", sections)
					print(30*"*")
				
		#general.save_to_json(args.topic, language, entities_history, "tmp")

if __name__ == "__main__":
	main()