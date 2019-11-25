# wiki-as-news

get_data.py

This file scrapes Wikipedia for a given list of languages and a list of titles. NB the titles must exist for each language, otherwise the script skips that language/title pair.
Input: a list of languages (>0) and a list of titles (>0)
Output: a dictionary, where each key is a data element from the Wikipedia page and the value is the data for that element, e.g. links: ['link1.com','link2.org','link3.net'].
The full list of data elements is: "categories", "content", "coordinates", "links", "images", "references", "revisions", "revision_id", and "sections". 
The dictionary is saved as a json if called with "--save y"

preprocess.py 

This file preprocesses the "categories", "content" and "images" elements data.
The categories are stripped of the "Category:" tag they all start with. Input: list of categories,e.g. "Category:British Politics". Output list of categories, e.g. "British Politics". Some categories have the prefix "Wikipedia", e.g. "Category:Wikipedia:XXXXX", these are not stripped, e.g. "Wikipedia:XXXXX".
The content (the text) is tokenized and lowercased.
The images have an "upload" url, and are given the real url location of the image in Wikimedia.

Output contains two directories, raw and processed.
The output from get_data is in "output/raw" and the output from preprocessed.py is in "output/processed"
