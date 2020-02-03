#!/usr/bin/python3
"""
	Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.
	Input: txt file with tab separated language, title pairs, e.g. 'refugee_crisis'
	Ouput: yield revision history dictionary with clean data. 
	Output fields: tlds_origin, reference_template_types, images, captions, links, categories, sections, content.
"""

import argparse
import general
import nltk
import re
import string

from collections import defaultdict, Counter

parser = argparse.ArgumentParser(description='''Quantitatively analyze the edit histories of Wikipedia language versions for newsiness and encyclopedia-ness.''')
parser.add_argument("topic", help="e.g. 'refugee_crisis'.")

args = parser.parse_args()