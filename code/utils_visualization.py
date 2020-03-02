#!/usr/bin/python3
"""
	Visualization utils for newswork analysis module.
"""
import matplotlib.pyplot as plt
import matplotlib._color_data as mcd
import numpy as np
import utils_io as uio

from datetime import datetime
from sklearn.preprocessing import Normalizer

#colors = ["indianred", "goldenrod", "steelblue", "darkolivegreen", "purple", "red", "blue", "green", "orange", "yellow","indianred", "goldenrod", "steelblue", "darkolivegreen", "purple", "red", "blue", "green", "orange", "yellow","indianred", "goldenrod", "steelblue", "darkolivegreen", "purple", "red", "blue", "green", "orange", "yellow","indianred", "goldenrod", "steelblue", "darkolivegreen", "purple", "red", "blue", "green", "orange", "yellow"]
colors = [mcd.XKCD_COLORS[c] for c in mcd.XKCD_COLORS]
linestyles = ["solid", "dotted"]

def get_RAWgraph_area_data(all_keys, input_dict):
	print("date\tkey\tvalue")

	for date in input_dict:
		for key in all_keys:
			if key in input_dict[date]:
				print(date, "\t", key, "\t", input_dict[date][key])
			else:
				print(date, "\t", key, "\t", 0)

def get_RAWgraph_barchart_data(input_dict, change_type):
	print("date\tkey\tvalue")

	for date in input_dict:
		print(date, "\t", change_type, "\t", input_dict[date])

def plot_barchart(dates, added, removed, topic, language, analysis):
	''' Plot changes to links. ''' 
	plt.axhline(0, color='grey')
	plt.xlabel('dates')
	plt.ylabel('changes to %s' % topic)
	#plt.xlim([min(dates), max(dates)])

	# scale values for comparative visual analysis across languages
	## NB: scaling here doesn't work for some reason
	#added_transformed = Normalizer().fit_transform(np.array(added).reshape(1, -1))
	#removed_transformed = Normalizer().fit_transform(np.array(removed).reshape(1, -1))
	plt.bar(dates, added)
	plt.bar(dates, removed)
	
	labels = [dates[0], dates[round(len(dates)/2)], dates[-1]] #dates[0]]+[x for n,x in enumerate(dates) if float(n) in [round(x) for x in np.arange(0+(len(dates)-2)/10, len(dates)-1, 5)]]+[dates[-1]]
	plt.xticks(labels, rotation = 45)
	plt.tight_layout()

	directory_name = "visualizations/%s/%s/" % (topic, analysis)
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)

	plt.close()
 
def plot_article_development(dates, elements, titles, topic, language, analysis):
	
	fig, ax = plt.subplots()
	plt.xlabel('Time')

	for n, element in enumerate(elements):
		if len(element) == 2: # For addition/removal development visualization: [ [1, 0, 0, 2, 0], [0, 0, -3, 0, 0] ]
			plt.ylabel('Values')

			# scale for comparitive visual analysis between languages
			X0_transformed = Normalizer().fit_transform(np.array(element[0]).reshape(1, -1))
			X1_transformed = Normalizer().fit_transform(np.array(element[1]).reshape(1, -1))
	
			ax.plot(dates, X0_transformed.transpose(), label="+ %s" % titles[n], linestyle=linestyles[0], color=colors[n])
			ax.plot(dates, X1_transformed.transpose(), label="- %s" % titles[n], linestyle=linestyles[1], color=colors[n])
		else: # For general article development visualization: [1, 0, 0, 2, 0]
			plt.ylabel('Normalized values')
			# normalize values to same space:
			# NB: also doesn't work
			X_transformed = Normalizer().fit_transform(np.array(element).reshape(1, -1))
			ax.plot(dates, X_transformed.transpose(), label=titles[n], linestyle=linestyles[0], color=colors[n])
	
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	labels = [dates[0], dates[len(dates)/4], dates[len(dates)/2], dates[(len(dates)/4)*3], dates[-1] #[dates[0]]+[x for n,x in enumerate(dates) if float(n) in [round(x) for x in np.arange(0+(len(dates)-2)/10, len(dates)-1, 10)]]+[dates[-1]]
	plt.xticks(labels, rotation = 90)
	plt.tight_layout()

	directory_name = "visualizations/%s/%s/" % (topic, analysis)
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)

	plt.close()

def plot_element_across_languages(dates, data, element, languages, topic, language):

	fig, ax = plt.subplots()
	plt.xlabel('time')
	plt.title("%s" % element)

	label_dates = []
	for n, lang_data in enumerate(data):

		language = languages[n]
		# get dates for labels:
		lang_dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ") for ts in dates[languages[n]]]
		label_dates += lang_dates

		# normalize values to same space:
		X_transformed = Normalizer().fit_transform(np.array(lang_data).reshape(1, -1)) #, np.array(lang_dates))
		plt.ylabel('values')
		ax.plot(lang_dates, X_transformed.transpose(), label=language, color=colors[n])
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	#plt.xticks(labels, rotation = 45)
	plt.tight_layout()
	plt.show()
	# directory_name = "visualizations/%s/%s/" % (topic, analysis)
	# uio.mkdirectory(directory_name)
	# file_name = "%s.png" % language
	# plt.savefig(directory_name + file_name)

	# plt.close()

if __name__ == "__main__":
	plot_barchart()
	plot_article_development()