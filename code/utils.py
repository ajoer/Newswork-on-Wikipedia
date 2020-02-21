#!/usr/bin/python3
"""
	Anaysis utils for Wikipedia edit history analysis.

"""

from Levenshtein import distance as levenshtein_distance

def allow_levenshtein_distance(list1, list2):
	''' Allow Levenshtein distance between "non-unique" elements, e.g. "Ma'an" and "Maan". '''
	
	if len(list1) == 0 or len(list2) == 0: return list1, list2

	for x in set(list1):
		for y in set(list2):

			distance = levenshtein_distance(x, y)
			if distance < len(x)/3: 
				try:
					list1.remove(x)
				except ValueError:
					continue
				list2.remove(y)
				
	return list1, list2


if __name__ == '__main__':
	allow_levenshtein_distance()