#!/usr/bin/python3

"""

"""

from bs4 import BeautifulSoup
from bs4.element import Comment


def filter_text(element):

	# filters out everything non-text and empty lines
	# TODO: filter out notes/references
	# li = lists, e.g. timeline

	if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'li']:
		return False
	if isinstance(element, Comment):
		return False
	if element == "\n":
		return False
	return True


def get_text_from_html(soup):

    texts = soup.findAll(text=True)
    # visible_texts is an iterator
    visible_texts = filter(filter_text, texts) 
    return u" ".join(t.strip() for t in visible_texts)

def process_data(outname,raw_data):

	#raw_textdata is a string
	data = ''.join(x for x in raw_data.strip())
	soup = BeautifulSoup(data, 'html.parser')

   	# process per data type
	text = get_text_from_html(soup)
	tables = soup.findAll(lambda tag: tag.name=='table')  #soup.findAll('table')
	print(tables)
	print(len(tables))
	images = '' #soup.find_all('img')
	wikilinks = ''
	references = ''
	named_entities = ''
	# save html
	if outname is not None:
		with open(outname + "_raw.txt", 'w', encoding='utf-8') as outfile:
   			outfile.write(soup.prettify())


if __name__== "__main__":
	process_data()
