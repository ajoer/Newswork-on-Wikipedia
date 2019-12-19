#!/usr/bin/python3
"""

	Modules for processesing Wikipedia revision histories data, e.g. for temporal analysis using revision history. 

	a.k.jorgensen@uva.nl
	December 2019

"""
import nltk
import preprocess
import re

def get_clickables(content):
	''' gets all clickable objects out of the content of a revision history timestamp. '''

	categories = []
	images = []
	languages = []
	links = []	# Get all clickable objects
	exp = re.compile("\[ \[ [A-Za-z0-9.|()-:' ëé]* \] \]") #-.|():' ëé
	clickables = exp.findall(content)

	if len(clickables) > 0:
		clickables = [x[4:-3].strip() for x in clickables]
		
		for clickable in clickables:

			try:
				# Get categories, LVs and images:
				if " : " in clickable:
					x, y = clickable.split(" : ")

					# language codes are lower case and 2-3 letters
					if x[0].islower() and 1 < len(x) < 4:
						languages.append(x)
					# images have px definitions (and different file endings; png, jpg etc.)
					elif "px" in y: #elif ".jpg" in y or ".PNG" in y:
						images.append(y.split("|")[0])
					else:
						categories.append(y)

				else:
					if "|" in clickable:
						clickable = clickable.split("|")[0]
						links.append(clickable)
					else:
						links.append(clickable)

			except ValueError:
				pass

	return categories, images, languages, links

def get_references(revision_content):
	''' gets the references out of the content of a revision history timestamp. '''

	references = []

	for word in revision_content.strip().split():
		if word.startswith("//www."):
			reference = word[6:]
			references.append(reference)
	
	return references

def get_section_titles(content):
	''' gets all section titles from the content of a revision history timestamp. '''

	exp = re.compile("={2,}[\-A-Za-z0-9.|():' üïëöäåæøáúíóé]+={2,}")
	### TODO: check the findings, "===Januar-febuar=== " doet het niet.
	sections = exp.findall(content)

	section_hierarchy = []
	number_of_sections = 0

	for sec in sections:
		top_level = ""
		second_level = ""
		third_level = ""
		fourth_level = ""
		
		try:
			if sec[1] == "=" and sec[2] != "=": 
				top_level = sec[2:-2].strip(" ")
				section_hierarchy.append(top_level)
				number_of_sections += 1

			elif sec[2] == "=" and sec[3] != "=": 
				second_level = (top_level, sec[3:-3].strip(" "))
				if top_level in section_hierarchy:
					section_hierarchy[section_hierarchy.index(top_level)] = second_level
					number_of_sections += 1

			elif sec[3] == "=" and sec[4] != "=": 
				third_level = (top_level, second_level, sec[4:-4].strip(" "))
				if second_level in section_hierarchy:
					section_hierarchy[section_hierarchy.index(second_level)] = third_level
					number_of_sections += 1

			elif sec[4] == "=": 
				fourth_level = (top_level, second_level, third_level, sec[5:-5].strip(" "))
				if third_level in section_hierarchy:
					section_hierarchy[section_hierarchy.index(third_level)] = fourth_level
					number_of_sections += 1

		except IndexError: pass

	return section_hierarchy, number_of_sections

def process_revision(revision, elements="all"):
	''' takes "elements" as input. Can be "entities" for temporal entity analysis for an event, or "all" for getting all contents processed for e.g. PoI analysis. '''

	output = dict()

	content = revision["slots"]["main"]["*"]
	content = preprocess.preprocess_content(content)

	categories, images, languages, links = get_clickables(content)

	if elements == "entities":
		return links, content

	elif elements == "revision_references":
		references = get_references(content)
		return references 

	else:
		section_hierarchy, number_of_sections = get_section_titles(content)

		output["categories"] = categories
		output["content"] = content
		output["images"] = images
		output["languages"] = languages
		output["links"] = links
		output["references"] = get_references(content)
		output["section_hierarchy"] = section_hierarchy
		output["number_of_sections"] = number_of_sections

		return output

if __name__ == "__main__":
	get_clickables()
	get_references()
	get_section_titles()
	process_revision()
