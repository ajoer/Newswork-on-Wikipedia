#!/usr/bin/python3
"""
	Make visualizations.

"""
import matplotlib.pyplot as plt
import numpy as np

def diachronic_distribution_references(topic, language, dict_of_news_counters, dict_of_local_counters, dict_of_localnews_counters, dict_of_domain_counters):
	# visualize amount of news sources in references over time
	
	local_news_percentages = []
	foreign_news_percentages = []
	local_percentages = []
	foreign_percentages = []
	timestamps = [timestamp for timestamp in dict_of_news_counters.keys()]

	print("timestamp 0:\t", timestamps[0])
	print("timestamp -1:\t", timestamps[-1])

	for timestamp in timestamps:
		total_sum_links = int(sum(dict_of_domain_counters[timestamp].values()))

		if total_sum_links > 0:

			sum_localnews = int(sum(dict_of_localnews_counters[timestamp].values()))

			local_news_percentage = (sum_localnews / total_sum_links) * 100
			foreign_news_percentage = (float(sum(dict_of_news_counters[timestamp].values())-sum_localnews) / total_sum_links) * 100
			local_percentage = (float(sum(dict_of_local_counters[timestamp].values())-sum_localnews) / total_sum_links) * 100

			local_news_percentages.append(local_news_percentage)
			foreign_news_percentages.append(foreign_news_percentage)
			local_percentages.append(local_percentage)
			
			foreign_percentage = 100-(local_news_percentage+foreign_news_percentage+local_percentage)
			foreign_percentages.append(foreign_percentage)

			total = local_news_percentage + foreign_news_percentage + local_percentage + foreign_percentage
			if total != 100:
				print("The sums don't add up! Check it out: ", local_news_percentage, " + ", foreign_news_percentage, " + ", local_percentage, " + ", foreign_percentage, " = ", total)

			#print("this is the amount of news at timestamp %s:\t %s of total %s references" % (timestamp, round((sum(news_counter[timestamp].values()) / sum(domain_counter[timestamp].values())) * 100, 20), sum(domain_counter[timestamp].values())))
		else: 
			local_news_percentages.append(0)
			foreign_news_percentages.append(0)
			local_percentages.append(0)
			foreign_percentages.append(0)

			#print("There are no references at timestamp %s" % timestamp) 

	timestamps.reverse()
	local_news_percentages.reverse()
	foreign_news_percentages.reverse()
	local_percentages.reverse()
	foreign_percentages.reverse()

	ind = np.arange(len(timestamps))   
	width = 0.15      

	p1 = plt.bar(ind, local_news_percentages, width, color='forestgreen')
	p2 = plt.bar(ind+width, foreign_news_percentages, width, color='royalblue') #, bottom=news_percentages)
	p3 = plt.bar(ind+2*width, local_percentages, width, color='crimson') #, bottom=news_percentages+local_percentages)
	p4 = plt.bar(ind+3*width, foreign_percentages, width, color='midnightblue') #, bottom=news_percentages+local_percentages) #+localnews_percentages)

	plt.ylabel("percentage")
	plt.title("Reference type distributions for '%s' in %s" % (topic, language))
	plt.xticks(ind, [x[:10] for x in timestamps], rotation=30, fontsize=6)
	plt.yticks(np.arange(0, 110, 10))
	plt.legend((p1[0], p2[0], p3[0], p4[0]), ("Local news", "Foreign news", "Local non-news", "Foreign non-news"))

	# get total number of references above each timestamp distribution:
	for r1,r2,r3,r4,timestamp in zip(p1,p2,p3,p4,timestamps):
		h1 = r1.get_height()
		h2 = r2.get_height()
		h3 = r3.get_height()
		h4 = r4.get_height()
		plt.text(r1.get_x()+r1.get_width()/4., max(h1,h2,h3,h4)+2, '%s'% int(sum(dict_of_domain_counters[timestamp].values())), rotation=30, fontsize=8)
	#plt.savefig("output/visualizations/reference_distributions/%s/%s_%s.png" % (topic, topic, language))
	plt.show()

if "__name__" == "__main__":
	diachronic_distribution_references()