#!/usr/bin/python3
"""
	Parse and clean the edit histories of Wikipedia language versions.
	Ouput: yield revision history dictionary with clean data. 
	Fields = tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""
import get_wiki_content
import nltk
import re
import string

from collections import Counter, defaultdict, OrderedDict

regex_letters = "\dA-Za-zğäåæáéëíıïóøöúü"
regex_symbols = "\"'(){}[\]&=«»:.,?_~–\-/| "

def replace_link(input_string, link, text):
	# Replace link with text
	output_string = input_string.replace("[[%s]]" % link, text)
	output_string = output_string.replace("[[%s|%s]]" % (link, text), text)

	return output_string

def get_links(input_string):

	links = []
	texts = []

	double_square_bracket, content_subbed = get_occurrences(r"\[\[(.*?)\]\]", input_string)
	for element in double_square_bracket:
		elements = element.split("|")

		link = elements[0]

		if len(elements) == 2:
			text = elements[1]
		else: 
			text = link
		links.append(link)
		texts.append(text)
	return links, texts

def get_occurrences(regex, content):
	# Reg ex to get all references/citations in an edit history.
	# Deletes the occurences from the content

	exp = re.compile(regex)
	occurrences = exp.findall(content)
	content = re.sub(exp, '', content)

	return occurrences, content

def get_reference_types(input_list):
	# Extract the reference type from a reference/citation block in an edit history, 
	# e.g. "book", "thesis", "news" etc.
	types = Counter()

	for element in input_list:
		try:
			reference_type = re.search("{{[c|C]ite (.*?)( |\|)", element).group(1)
			if len(reference_type) <= 1: continue
			types[reference_type] += 1

		except AttributeError:
			types[None] += 1

	return types

def get_tlds(url_list):
	# Extract the tlds from each url in a reference/citation block in an edit history.

	tlds = Counter()

	for url in url_list:
		tld = url.split("/")[0].split(".")[-1]
		tlds[tld] += 1

	return tlds 

def get_urls(input_list):

	# Todo: check whether this is the best way.

	urls = []
	http_regex = "http[s]*:\/\/([^ ]*)"

	for element in input_list:
		# they differ in endings:
		url = re.search(http_regex + r"( |}})", element)
		if url:
			url = url.group(1).split("|")[0]
		else:
			url = re.search(http_regex, element)
			if not url: continue
			url = url.group(1).split("|")[0]

		#if url is None: continue
		if "www" in url:
			url = url[4:]
		urls.append(url)
	return urls

def parse_images(content):
	''' Extract and parse images.'''
	images = []
	captions = []
	links_from_captions = []
	extensions = [".jpg", ".svg", ".png"]

	for line in content.split("\n"):
		for extension in extensions:

			if not extension in line.lower(): continue

			# Images
			image_title, image_extension = re.search(r"(:|=)([^(:|=)].*)(.jpg|.svg|.png|.JPG|.SVG|.PNG)", line).group(2,3)

			if ":" in image_title:
				image_title = image_title.split(":")[-1]

			image_title = '_'.join([x for x in image_title.split()])
			image_link = "https://commons.wikimedia.org/wiki/File:" + image_title + image_extension

			images.append(image_link)
			content = content.replace(line, "")

			# Captions
			# Some languages (e.g. EN) make use of this structure for captions: "alt=British soldiers....". They can have links in the caption.
			if "|alt=" in line:

				elements = line.split("|alt=")[-1].split("|")[1:]
				caption = '|'.join(elements)[:-2]
				content = content.replace(line, caption)
				
			# Other languages (e.g. NL) do not...
			else:
				caption = re.search(r"\|([^|]*)\]\]", line)
				if not caption: continue 
				caption = caption.group(1)

				if "px" in caption: continue

			# Get links and remove from caption
			links, texts = get_links(caption)

			for link, text in zip(links, texts):
				caption = replace_link(caption, link, text)
				content = replace_link(content, link, text)
				
				links_from_captions.append(link)
				captions.append(caption)

	return content, images, captions, links_from_captions

def parse_links_categories(content):
	# Parse links and categories from an edit history. 
	# Must be run after parse_images() because images have the same markup, and will otherwise feature as links.
	categories = []

	links, texts = get_links(content)
	
	for link, text in zip(links,texts):
		# filter out categories:
		if ":" in link:
			category = link.split(":")[1]
			categories.append(category)
			links.remove(link)
			content = replace_link(content, link, text)

		else:
			content = replace_link(content, link, text)

	return content, links, categories

def parse_references(content):
	''' Extract and analyze references and their origin (tld) over time.'''
	reference_template_types = Counter() # some references have "type" markup, e.g. "book", "thesis", "news" etc.

	references, content = get_occurrences(r"<ref(.*?)<\/ref>", content) 
	citations, content = get_occurrences(r"{{[c|C]ite [" + regex_letters + regex_symbols + ">]+}}", content)
	external_links = get_urls([x for x in content.split()])

	urls = get_urls(references + citations)

	tlds_origin = get_tlds(urls + external_links)
	reference_types = get_reference_types(references + citations)
	reference_template_types += reference_types
	return content, tlds_origin, reference_template_types

def parse_sections(content):
	# Parse sections from edit history

	#Todo: consider another way to parse section titles with better depth.

	sections = []
	header1s, content = get_occurrences(r"[^=]={2}([^=].*?)={2}", content)
	header2s, content = get_occurrences(r"[^=]={3}([^=].*?)={3}", content)
	header3s, content = get_occurrences(r"[^=]={4}([^=].*?)={4}", content)
	sections.append([x.strip() for x in header1s])
	sections.append([x.strip("=").strip() for x in header2s])
	sections.append([x.strip("==").strip() for x in header3s])

	return content, sections

def parse_text(content):
	# Clean remaining content for tables, noise and image markup. Also cleans italics markup.

	clean_content = []
	italics, content = get_occurrences(r"\'\'", content)

	for line in content.split("\n"):

		if len(line) == 0: continue
		if line[0] in string.punctuation or "px" in line: continue

		# Add end punct to lines
		if line[-1] not in string.punctuation: line += "."
		clean_content.append(line)

	content = ' '.join([w for w in clean_content])
	content = ' '.join(nltk.word_tokenize(content))

	return content

if __name__ == "__main__":
	parse_images(content)
	parse_links_categories(content)
	parse_references(content)
	parse_sections(content)
	parse_text(content) 