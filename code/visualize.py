#!/usr/bin/python3
"""
	Make visualizations.

"""
import matplotlib.pyplot as plt
import numpy as np

def reference_dist_diachronic(topic, language, num_of_domains, local_counters, foreign_counters, local_news_counters, foreign_news_counters):
	''' creates a bar chart of the distribution of the types of references over time '''

	local = []
	foreign = []
	local_news = []
	foreign_news = []

	timestamps = [timestamp for timestamp in num_of_domains.keys()]

	for timestamp in timestamps:
		
		total = num_of_domains[timestamp]

		if total > 0:

			l = (int(sum(local_counters[timestamp].values())) / total) * 100
			f = (int(sum(foreign_counters[timestamp].values())) / total) * 100
			ln = (int(sum(local_news_counters[timestamp].values())) / total) * 100
			fn = (int(sum(foreign_news_counters[timestamp].values())) / total) * 100

			local.append(l)
			foreign.append(f)			
			local_news.append(ln)
			foreign_news.append(fn)

		else: 
			local_news.append(0)
			foreign_news.append(0)
			local.append(0)
			foreign.append(0)

	timestamps.reverse()
	local_news.reverse()
	foreign_news.reverse()
	local.reverse()
	foreign.reverse()

	ind = np.arange(len(timestamps))   
	width = 0.15      

	p1 = plt.bar(ind, local, width, color='forestgreen')
	p2 = plt.bar(ind+width, foreign, width, color='royalblue')
	p3 = plt.bar(ind+2*width, local_news, width, color='crimson')
	p4 = plt.bar(ind+3*width, foreign_news, width, color='midnightblue')

	plt.ylabel("percentage")
	plt.title("Reference type distributions for '%s' in %s" % (topic, language))
	plt.xticks(ind, [x[:10] for x in timestamps], rotation=30, fontsize=6)
	plt.yticks(np.arange(0, 110, 10))
	plt.legend((p1[0], p2[0], p3[0], p4[0]), ("Local non-news", "Foreign non-news", "Local news", "Foreign news"))

	# print the total number of references above each timestamp distribution:
	for r1, r2, r3, r4, timestamp in zip(p1, p2, p3, p4, timestamps):
		h1 = r1.get_height()
		h2 = r2.get_height()
		h3 = r3.get_height()
		h4 = r4.get_height()
		plt.text(r1.get_x()+r1.get_width()/4., max(h1,h2,h3,h4)+2, '%s'% num_of_domains[timestamp], rotation=30, fontsize=8)
	plt.show()

def DMI_reference_dist_diachronic(topic, language, local, foreign):
	''' creates a bar chart of the distribution of the types of references over time '''

	timestamps = [timestamp for timestamp in reference_revisions.keys()]

	timestamps.reverse()
	local.reverse()
	foreign.reverse()

	ind = np.arange(len(timestamps))   
	width = 0.15      

	p1 = plt.bar(ind, local, width, color='forestgreen')
	p2 = plt.bar(ind+width, foreign, width, bottom=local, color='royalblue')

	plt.ylabel("percentage")
	plt.title("Reference type distributions for '%s' in %s" % (topic, language))
	plt.xticks(ind, [x[:10] for x in timestamps], rotation=30, fontsize=6)
	plt.yticks(np.arange(0, 110, 10))
	plt.legend((p1[0], p2[0]), ("Local", "Foreign"))

	# print the total number of references above each timestamp distribution:
	for r1, r2, timestamp in zip(p1, p2, timestamps):
		h1 = r1.get_height()
		h2 = r2.get_height()
		plt.text(r1.get_x()+r1.get_width()/2., max(h1,h2)+2, '%s'% num_of_domains[timestamp], rotation=30, fontsize=8)
	plt.show()


if "__name__" == "__main__":
	reference_dist_diachronic()
	DMI_reference_dist_diachronic()