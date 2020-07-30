#!/usr/bin/python3
"""
	Visualization utils for revision analysis.
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import utils_io as uio

def plot_wikipedian_edittypes(wikipedian_edittypes, timestamps, topic, language):

	wikipedian_edit_style = {
		"anon_content": ["indianred", "dashed"],
		"anon_editorial": ["indianred", "dotted"],
		"reg_content": ["steelblue", "dashed"],
		"reg_editorial": ["steelblue", "dotted"],
		"bot_content": ["darkolivegreen", "dashed"],
		"bot_editorial": ["darkolivegreen", "dotted"]
	}

	fig, ax = plt.subplots()
	for w_e in wikipedian_edittypes:
		ax.plot(timestamps, wikipedian_edittypes[w_e], color=wikipedian_edit_style[w_e][0], linestyle=wikipedian_edit_style[w_e][1], label=" ".join(w_e.split("_")))
	ax.tick_params(labelbottom=False)
	# Shrink current axis's height by 10% on the bottom
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.1,
	                 box.width, box.height * 0.9])

	# Put a legend below current axis
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
	          fancybox=True, shadow=True, ncol=3)

	directory_name = "visualizations/%s/wikipedian_edittypes/" % topic
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)
	plt.close()

def plot_content_magnitude(content_sizes, timestamps, topic, language):
	fig, ax = plt.subplots()
	ax.plot(timestamps, content_sizes, color="orange", label="content magnitude")
	ax.tick_params(labelbottom=False)
	ax.legend()

	directory_name = "visualizations/%s/content_magnitude/" % topic
	uio.mkdirectory(directory_name)
	file_name = "%s.png" % language
	plt.savefig(directory_name + file_name)
	plt.close()

def plot_additions_deletions_per_wikipediantype(data, timestamps, topic, language):

	for (change,endings) in [("additions", "add"), ("deletions", "del")]:

		fig, ax = plt.subplots()
		ax.plot(timestamps, data[f"registered_{endings}"], label="registered")
		ax.plot(timestamps, data[f"anonymous_{endings}"], label="anonymous")
		ax.plot(timestamps, data[f"bot_{endings}"], label="bots")
		ax.legend()

		directory_name = f"visualizations/{topic}/additions_deletions/"
		uio.mkdirectory(directory_name)
		file_name = f"{language}_{change}.png"
		plt.savefig(directory_name + file_name)
		plt.close()

def plot_creation_time(creation_dates, LVs, colors, continents):

	fig = go.Figure()
	fig.add_trace(go.Scatter(
	    x=creation_dates,
	    y=LVs,
	    mode="markers",
	    marker=dict(color=colors, size=8),
	    text=continents
	))
	
	fig.update_layout(
		title="Date of page creation",
	    xaxis_title="Date",
	    yaxis_title="Language Version",
	    yaxis_dtick = 1
  	)

	fig.write_html("visualizations/creation_times.html")

if __name__ == "__main__":
	plot_over_time()
	plot_content_development()