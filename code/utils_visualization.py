#!/usr/bin/python3
"""
	Visualization utils for newswork analysis module.
"""
import matplotlib.pyplot as plt
import numpy as np
import utils_io as uio

from scipy.interpolate import make_interp_spline, BSpline

colors = ["indianred", "goldenrod", "steelblue", "darkolivegreen", "purple"]
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
	plt.bar(dates, added)
	plt.bar(dates, removed)

	labels = [dates[0]]+[x for n,x in enumerate(dates) if float(n) in [round(x) for x in np.arange(0+(len(dates)-2)/10, len(dates)-1, 5)]]+[dates[-1]]
	plt.xticks(labels, rotation = 45)
	plt.tight_layout()

	directory_name = "visualizations/%s/%s/" % (topic, analysis)
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)

	plt.close()

def plot_article_development(dates, elements, titles, topic, language, analysis):
	
	fig, ax = plt.subplots()
	plt.xlabel('time')

	for n, element in enumerate(elements):
		if len(element) == 2: # For addition/removal development visualization: [ [1, 0, 0, 2, 0], [0, 0, -3, 0, 0] ]
			plt.ylabel('values')
			ax.plot(dates, element[0], label="+ %s" % titles[n], linestyle=linestyles[0], color=colors[n])
			ax.plot(dates, element[1], label="- %s" % titles[n], linestyle=linestyles[1], color=colors[n])
		else: # For general article development visualization: [1, 0, 0, 2, 0]
			plt.ylabel('scaled values')
			ax.plot(dates, element, label=titles[n], linestyle=linestyles[0], color=colors[n])
	
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	labels = [dates[0]]+[x for n,x in enumerate(dates) if float(n) in [round(x) for x in np.arange(0+(len(dates)-2)/10, len(dates)-1, 10)]]+[dates[-1]]
	plt.xticks(labels, rotation = 45)
	plt.tight_layout()

	directory_name = "visualizations/%s/%s/" % (topic, analysis)
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)

	plt.close()

if __name__ == "__main__":
	plot_barchart()
	plot_article_development()